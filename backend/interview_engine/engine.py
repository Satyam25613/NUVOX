"""
NUVOX — Interview Engine (Gemini Live API)
Model: models/gemini-2.5-flash-native-audio-preview-12-2025

Bridges FastAPI WebSocket ↔ Gemini Live bidiGenerateContent session.
Uses Gemini's native input/output audio transcription for accurate
transcript capture (critical for report generation).
"""

import os
import json
import asyncio
import logging
from google import genai
from google.genai import types
from fastapi import WebSocket, WebSocketDisconnect

from interview_engine.personas import PERSONAS, PERSONA_LABELS, PERSONA_OPENING_QUESTIONS
from database.supabase_client import get_resume_by_interview, get_interview, save_message
from utils.key_manager import get_next_key, mark_key_exhausted

logger = logging.getLogger("nuvox")

MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"

# Audio I/O constants
AUDIO_MIME_IN  = "audio/pcm"     # Browser→Gemini: 16kHz PCM16 mono
AUDIO_MIME_OUT = "audio/pcm"     # Gemini→Browser: 24kHz PCM16 mono


def _extract_candidate_name(resume_text: str) -> str:
    """Try to extract candidate name from first few lines of resume."""
    if not resume_text:
        return ""
    lines = [l.strip() for l in resume_text.split("\n") if l.strip()]
    # Name is usually in first 1-3 lines, short, no digits
    for line in lines[:4]:
        words = line.split()
        if 1 < len(words) <= 5 and all(w.replace(".", "").isalpha() for w in words):
            return line.strip()
    return ""


class InterviewEngine:
    """
    Bridges FastAPI WebSocket ↔ Gemini Live bidiGenerateContent session.
    Uses Gemini's native input/output audio transcription for accurate
    transcript capture (critical for report generation).
    """

    def __init__(self, interview_id: str, websocket: WebSocket):
        self.interview_id = interview_id
        self.fastapi_ws   = websocket
        
        self.current_key = get_next_key()
        self.client  = genai.Client(api_key=self.current_key)
        self.session = None

        # Transcript accumulators — these collect text across a single turn
        self._current_ai_text = []       # AI's spoken words (from outputTranscription)
        self._current_user_text = []     # User's spoken words (from inputTranscription)
        self._turn_count = 0

    # ── System instruction ─────────────────────────────────────────

    async def _build_system_instruction(self) -> str:
        interview = get_interview(self.interview_id)
        if not interview:
            raise ValueError(f"Interview {self.interview_id} not found")

        persona_name   = interview.get("persona", "software_developer")
        persona_prompt = PERSONAS.get(persona_name, PERSONAS["software_developer"])
        persona_label  = PERSONA_LABELS.get(persona_name, "the role")
        opening_q      = PERSONA_OPENING_QUESTIONS.get(persona_name, "Tell me about yourself.")

        # Load resume data
        candidate_name = "the candidate"
        skills_str     = "Not provided"
        projects_str   = "Not provided"

        resume_data = get_resume_by_interview(self.interview_id)
        if resume_data:
            resume_text = resume_data.get("resume_text", "").strip()
            extracted_name = _extract_candidate_name(resume_text)
            if extracted_name:
                candidate_name = extracted_name

            skills = resume_data.get("skills", [])
            if skills:
                skills_str = ", ".join(str(s) for s in skills[:20])

            projects = resume_data.get("projects", [])
            if projects:
                proj_names = []
                for p in projects[:5]:
                    if isinstance(p, dict):
                        proj_names.append(p.get("name", str(p)))
                    else:
                        proj_names.append(str(p))
                projects_str = ", ".join(proj_names) if proj_names else "Not provided"

        first_name = candidate_name.split()[0] if candidate_name != "the candidate" else ""
        greeting_name = first_name if first_name else "there"

        system_prompt = f"""CRITICAL: You are a voice AI interviewer. Speak ONLY your actual words to the candidate. Never output asterisks, stars, markdown, internal thoughts, reasoning steps, system notes, or meta-commentary of any kind. Do not describe what you are about to do. Just do it.

You are a professional AI interviewer named Alex conducting a mock interview for NUVOX.

CANDIDATE PROFILE:
- Name: {candidate_name}
- Role applying for: {persona_label}
- Key skills from resume: {skills_str}
- Projects on resume: {projects_str}

YOUR BEHAVIOUR:
- Greet the candidate warmly by name if known
- Ask one question at a time
- Wait for their full answer before continuing
- Ask follow-up questions based on their actual resume projects when possible
- Maximum 12 questions total across the entire interview
- Do not evaluate or give hints during the interview
- Keep each response extremely brief. Exactly 1 short sentence.
- Professional but warm, human tone
- Never output markdown formatting of any kind

OPENING SCRIPT (deliver this exactly as your very first response):
Hello {greeting_name}! I'm Alex, your interviewer today. I've reviewed your background and I'm excited to learn more about your experience as a {persona_label}. We'll spend about 15 minutes together — I'll ask you up to 12 questions, so just speak naturally. There are no trick questions here. Ready? Let's begin. {opening_q}

INTERVIEW STYLE:
{persona_prompt}"""

        return system_prompt

    # ── Main session ───────────────────────────────────────────────

    async def run(self):
        sys_instr = await self._build_system_instruction()

        # Handshake 1: Connected
        await self.fastapi_ws.send_json({
            "type": "connected",
            "state": "ready",
            "message": "Interview session established",
            "interview_id": self.interview_id
        })

        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=sys_instr,
            # Enable Gemini-native transcription for BOTH sides of conversation
            inputAudioTranscription=types.AudioTranscriptionConfig(),
            outputAudioTranscription=types.AudioTranscriptionConfig(),
        )

        logger.info(f"Connecting → model={MODEL} interview={self.interview_id}")

        for attempt in range(2):
            try:
                async with self.client.aio.live.connect(model=MODEL, config=config) as session:
                    self.session = session
                    logger.info(f"✓ Connected to Gemini Live")

                    # Handshake 2: Session Ready
                    await self.fastapi_ws.send_json({
                        "type": "session_ready",
                        "state": "listening",
                        "message": "AI interviewer is ready"
                    })

                    # Text greeting trigger — safe, always works
                    await session.send(
                        input="Hello, please begin the interview now.",
                        end_of_turn=True
                    )
                    logger.info(f"✓ Greeting trigger sent")

                    receive_task = asyncio.create_task(self._receive_from_gemini())
                    send_task    = asyncio.create_task(self._send_to_gemini())

                    done, pending = await asyncio.wait(
                        [receive_task, send_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    for task in done:
                        try:
                            task.result()
                        except (WebSocketDisconnect, asyncio.CancelledError):
                            pass
                        except Exception as e:
                            logger.warning(f"Task error: {type(e).__name__}: {e}")

                    for task in pending:
                        task.cancel()
                        try:
                            await task
                        except Exception:
                            pass

                    logger.info(f"Session closed — {self.interview_id}")
                    break

            except Exception as e:
                error_str = str(e)
                logger.error(f"Gemini connection failed: {type(e).__name__}: {e}")
                
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                    mark_key_exhausted(self.current_key)
                    if attempt == 0:
                        # Retry once with next key for session start
                        self.current_key = get_next_key()
                        self.client = genai.Client(api_key=self.current_key)
                        logger.info(f"Retrying connection for interview={self.interview_id} with next key...")
                        continue

                # Notify browser the connection failed
                try:
                    await self.fastapi_ws.send_json({
                        "type": "error",
                        "message": f"AI connection failed: {str(e)}. Try refreshing or switching to text mode.",
                    })
                except Exception:
                    pass
                raise

    # ── Browser → Gemini ───────────────────────────────────────────

    async def _send_to_gemini(self):
        """Relay raw PCM16 bytes and control signals from browser WebSocket → Gemini Live."""
        try:
            while True:
                message = await self.fastapi_ws.receive()

                # Handle text messages (control signals)
                if 'text' in message:
                    try:
                        data = json.loads(message['text'])
                        if data.get('type') == 'end_of_turn':
                            # Tell Gemini the user finished speaking
                            await self.session.send(
                                input={"data": b'', "mime_type": "audio/pcm"},
                                end_of_turn=True
                            )
                    except json.JSONDecodeError:
                        pass

                # Handle binary messages (audio bytes)
                elif 'bytes' in message:
                    audio_data = message['bytes']
                    if not audio_data or len(audio_data) < 2:
                        continue
                    if self.session:
                        try:
                            await self.session.send(
                                input={"data": audio_data, "mime_type": "audio/pcm"},
                                end_of_turn=False
                            )
                        except Exception as e:
                            logger.warning(f"Failed to send audio to Gemini: {type(e).__name__}: {e}")
                            # Don't crash — just skip this chunk

        except WebSocketDisconnect:
            logger.info("Browser disconnected (send loop)")
            raise
        except Exception as e:
            logger.error(f"_send_to_gemini error: {type(e).__name__}: {e}")
            raise

    # ── Gemini → Browser ───────────────────────────────────────────

    async def _save_turn_transcript(self):
        """Save accumulated transcript for the completed turn to DB."""
        ai_text = " ".join(self._current_ai_text).strip()
        user_text = " ".join(self._current_user_text).strip()

        if ai_text or user_text:
            question = ai_text if ai_text else f"[AI turn {self._turn_count}]"
            answer = user_text if user_text else ""
            logger.info(f"Transcript turn {self._turn_count}: Q={question[:80]}... A={answer[:80]}...")
            save_message(
                interview_id=self.interview_id,
                question=question,
                answer=answer,
            )

            # Also send transcript to browser for display
            try:
                if ai_text:
                    await self.fastapi_ws.send_json({
                        "type": "transcript",
                        "role": "interviewer",
                        "text": ai_text,
                    })
            except Exception:
                pass

        # Reset buffers
        self._current_ai_text = []
        self._current_user_text = []

    async def _receive_from_gemini(self):
        """
        Relay Gemini audio → browser and collect transcriptions.

        Uses Gemini's native transcription API:
        - outputTranscription: text of what the AI SAYS
        - inputTranscription: text of what the USER SAYS

        These are the authoritative transcripts used for report generation.
        """
        try:
            while True:
                self._turn_count += 1
                logger.info(f"Waiting for Gemini turn #{self._turn_count}...")

                async for response in self.session.receive():
                    if not response.server_content:
                        continue

                    sc = response.server_content

                    # ── Capture OUTPUT transcription (what AI says) ────
                    if hasattr(sc, 'output_transcription') and sc.output_transcription:
                        ot = sc.output_transcription
                        if hasattr(ot, 'text') and ot.text:
                            self._current_ai_text.append(ot.text)
                    elif hasattr(sc, 'outputTranscription') and sc.outputTranscription:
                        ot = sc.outputTranscription
                        if hasattr(ot, 'text') and ot.text:
                            self._current_ai_text.append(ot.text)

                    # ── Capture INPUT transcription (what user says) ───
                    if hasattr(sc, 'input_transcription') and sc.input_transcription:
                        it = sc.input_transcription
                        if hasattr(it, 'text') and it.text:
                            self._current_user_text.append(it.text)
                    elif hasattr(sc, 'inputTranscription') and sc.inputTranscription:
                        it = sc.inputTranscription
                        if hasattr(it, 'text') and it.text:
                            self._current_user_text.append(it.text)

                    # ── Check if turn is complete (Gemini finished speaking) ──
                    if sc.turn_complete:
                        logger.info(f"Gemini turn #{self._turn_count} complete")
                        await self._save_turn_transcript()
                        break

                    # ── Forward audio to browser ──────────────────────
                    if sc.model_turn:
                        for part in sc.model_turn.parts:
                            if part.inline_data and part.inline_data.data:
                                audio = part.inline_data.data
                                if isinstance(audio, bytes) and len(audio) > 0:
                                    try:
                                        await self.fastapi_ws.send_bytes(audio)
                                    except (RuntimeError, WebSocketDisconnect):
                                        logger.warning("WS send_bytes failed — browser disconnected")
                                        await self._save_turn_transcript()
                                        return

        except Exception as e:
            logger.error(f"_receive_from_gemini error: {type(e).__name__}: {e}")
            # Save whatever transcript we have before exiting
            await self._save_turn_transcript()
