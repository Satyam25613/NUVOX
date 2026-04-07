import os
import uuid
import json
import asyncio
import logging
from fastapi import APIRouter, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from google import genai

from resume_parser.parser import parse_resume_pdf
from interview_engine.engine import InterviewEngine
from interview_engine.personas import PERSONAS, PERSONA_LABELS, PERSONA_OPENING_QUESTIONS
from evaluation_engine.evaluator import generate_report
from database.supabase_client import (
    save_resume,
    get_resume,
    get_latest_resume,
    create_interview,
    get_interview,
    save_message,
    get_interview_messages,
    save_report,
    get_report,
)
from utils.key_manager import get_next_key, mark_key_exhausted

logger = logging.getLogger("nuvox")
router = APIRouter()

# ─── HTTP Endpoints ───────────────────────────────────────────────────────────

@router.post("/api/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
):
    """Upload and parse a PDF resume."""
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Validate file size (10MB limit)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

    try:
        parsed = parse_resume_pdf(contents)

        resume_id = str(uuid.uuid4())
        save_resume(
            resume_id=resume_id,
            resume_text=parsed["text"],
            skills=parsed["skills"],
            projects=parsed["projects"],
        )

        logger.info(f"Resume uploaded: {resume_id} — {len(parsed['skills'])} skills, {len(parsed['projects'])} projects")

        return {
            "resume_id": resume_id,
            "status": "success",
            "skills": parsed["skills"],
            "projects": parsed["projects"],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Resume parse error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


@router.post("/api/start-interview")
async def start_interview(body: dict):
    """Create a new interview session."""
    resume_id = body.get("resume_id")
    persona = body.get("persona", "")

    PERSONA_ALIASES = {
        "technical": "software_developer",
        "software": "software_developer",
        "developer": "software_developer",
        "dev": "software_developer",
        "hr": "hr_manager",
        "human_resources": "hr_manager",
        "manager": "hr_manager",
        "behavioral": "hr_manager",
        "product": "product_manager",
        "pm": "product_manager",
        "data": "data_scientist",
        "ds": "data_scientist",
        "analyst": "data_scientist",
        "design": "ux_designer",
        "ux": "ux_designer",
        "ui": "ux_designer",
        "marketing": "marketing_specialist",
        "finance": "finance_analyst",
        "financial": "finance_analyst"
    }

    if persona:
        persona = PERSONA_ALIASES.get(persona.lower(), persona.lower())

    if not persona or persona not in PERSONAS:
        raise HTTPException(status_code=400, detail=f"Invalid persona. Choose from: {', '.join(PERSONAS.keys())}")

    if resume_id:
        resume = get_resume(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found.")

    interview_id = str(uuid.uuid4())
    create_interview(
        interview_id=interview_id,
        persona=persona,
        resume_id=resume_id,
    )

    logger.info(f"Interview created: {interview_id} — persona={persona}")

    return {
        "interview_id": interview_id,
        "status": "ready",
    }


@router.post("/api/interview-message")
async def interview_message(body: dict):
    """Save a Q&A turn and generate next question (text mode fallback)."""
    interview_id = body.get("interview_id")
    question = body.get("question", "")
    answer = body.get("answer", "")

    if not interview_id:
        raise HTTPException(status_code=400, detail="Interview ID is required.")

    # Save the message
    save_message(
        interview_id=interview_id,
        question=question,
        answer=answer,
    )

    # Get interview details for context
    interview = get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")

    # Count existing messages to track question number
    messages = get_interview_messages(interview_id)
    question_count = len(messages)

    # Check if session should end (12 questions max)
    if question_count >= 12:
        return {
            "next_question": "",
            "session_complete": True,
            "question_count": question_count,
        }

    # Generate next question using Gemini text API
    next_question = await _generate_next_question(interview, messages)

    return {
        "next_question": next_question,
        "session_complete": False,
        "question_count": question_count,
    }


async def _generate_next_question(interview: dict, messages: list) -> str:
    """Generate the next interview question using Gemini text API."""
    persona_name = interview.get("persona", "software_developer")
    persona_label = PERSONA_LABELS.get(persona_name, "the role")
    persona_prompt = PERSONAS.get(persona_name, PERSONAS["software_developer"])

    # Build conversation history
    conversation = ""
    for msg in messages[-6:]:  # Last 6 exchanges for context
        q = msg.get("question", "").strip()
        a = msg.get("answer", "").strip()
        if q:
            conversation += f"Interviewer: {q}\n"
        if a:
            conversation += f"Candidate: {a}\n"

    prompt = f"""You are Alex, a professional AI interviewer for a {persona_label} position.

{persona_prompt}

Here is the conversation so far:
{conversation}

Generate the NEXT interview question. Rules:
- Ask exactly ONE question
- Make it relevant to the previous answer
- Keep it concise (1-2 sentences max)
- Do not evaluate the candidate's answer
- Do not use markdown or special formatting
- Just output the question text, nothing else"""

    try:
        current_key = get_next_key()
        client = genai.Client(api_key=current_key)
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        next_q = response.text.strip().strip('"').strip("'")
        if next_q:
            logger.info(f"Text mode: generated question for {interview.get('id', '?')}")
            return next_q

    except Exception as e:
        error_str = str(e)
        logger.warning(f"Text question generation failed: {type(e).__name__}: {e}")
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            mark_key_exhausted(current_key)

    # Fallback questions based on persona
    fallbacks = {
        "software_developer": "Can you explain your approach to problem-solving when you encounter a complex technical challenge?",
        "web_developer": "How do you ensure your web applications are performant and accessible?",
        "qa_engineer": "What's your process for creating comprehensive test cases for a new feature?",
        "marketing_specialist": "How do you measure the success of a marketing campaign?",
        "sales_executive": "How do you handle objections from a potential client?",
        "product_manager": "How do you prioritize features when resources are limited?",
        "data_analyst": "Walk me through how you would approach analyzing a new dataset.",
    }
    return fallbacks.get(persona_name, "Tell me more about your experience with that.")


@router.post("/api/generate-report")
async def trigger_generate_report(body: dict):
    """Trigger report generation after interview ends."""
    interview_id = body.get("interview_id")

    if not interview_id:
        raise HTTPException(status_code=400, detail="Interview ID is required.")

    # Fetch all messages for this interview
    messages = get_interview_messages(interview_id)

    # Build transcript from Gemini transcription data
    transcript = ""
    if not messages:
        transcript = (
            "Note: No transcript data was captured for this interview session. "
            "The interview may have been too short or the transcription system was not active.\n"
        )
    else:
        seen = set()  # De-duplicate messages
        turn_num = 0
        for msg in messages:
            q = msg.get("question", "").strip()
            a = msg.get("answer", "").strip()

            # Skip empty or placeholder entries
            if not q and not a:
                continue
            if q == "Introduction" and not a:
                continue

            # De-duplicate
            key = f"{q}|{a}"
            if key in seen:
                continue
            seen.add(key)

            turn_num += 1
            if q and q != "Introduction":
                transcript += f"Interviewer (Q{turn_num}): {q}\n"
            if a:
                transcript += f"Candidate (A{turn_num}): {a}\n"
            transcript += "\n"

    logger.info(f"Report generation: {len(transcript)} chars, {len(messages or [])} messages")

    try:
        report_data = await generate_report(transcript)
        report_id = str(uuid.uuid4())

        save_report(
            report_id=report_id,
            interview_id=interview_id,
            score=report_data.get("overall_score", 0),
            communication=report_data.get("communication_score", 0),
            technical=report_data.get("technical_score", 0),
            confidence=report_data.get("confidence_score", 0),
            feedback=report_data.get("feedback", ""),
            strengths=report_data.get("strengths", []),
            improvements=report_data.get("improvements", []),
            recommendation=report_data.get("recommendation", ""),
            transcript=transcript,
        )

        logger.info(f"Report generated: {report_id} for interview {interview_id}")

        return {
            "report_id": report_id,
            "status": "generated",
        }

    except Exception as e:
        logger.error(f"Report generation failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/api/report/{interview_id}")
async def get_interview_report(interview_id: str):
    """Fetch a generated report."""
    report = get_report(interview_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not ready yet.")

    return {
        "communication_score": report.get("communication", 0),
        "technical_score": report.get("technical", 0),
        "confidence_score": report.get("confidence", 0),
        "problem_solving_score": report.get("score", 0),
        "overall_feedback": f"{report.get('feedback', '')}\n\nRecommendation: {report.get('recommendation', 'Pending')}",
        "areas_of_improvement": report.get("improvements", []),
        "suggested_topics": report.get("strengths", []),
    }


# ─── WebSocket Endpoint ──────────────────────────────────────────────────────

@router.websocket("/ws/interview/{interview_id}")
async def websocket_interview(websocket: WebSocket, interview_id: str):
    """Real-time voice interview via WebSocket."""
    await websocket.accept()
    logger.info(f"WebSocket connected: interview={interview_id}")

    try:
        engine = InterviewEngine(interview_id, websocket)
        # run the streaming loop with 15-min max duration
        await asyncio.wait_for(engine.run(), timeout=900)

        # End cleanly
        try:
            await websocket.send_json({
                "type": "session_end",
                "reason": "time_limit",
                "message": "Interview ended — 15 minute limit reached.",
            })
        except Exception:
            pass

    except asyncio.TimeoutError:
        logger.info(f"Interview timeout: {interview_id}")
        try:
            await websocket.send_json({
                "type": "session_end",
                "reason": "time_limit",
                "message": "Interview ended — 15 minute limit reached.",
            })
        except Exception:
            pass

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {interview_id}")

    except Exception as e:
        logger.error(f"WebSocket error ({interview_id}): {type(e).__name__}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Interview error: {str(e)}",
            })
        except Exception:
            pass

    finally:
        try:
            await websocket.close()
        except Exception:
            pass
        logger.info(f"WebSocket closed: {interview_id}")
