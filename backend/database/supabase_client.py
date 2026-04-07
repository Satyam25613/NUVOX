"""
NUVOX — Database Client
Uses file-based JSON persistence for local/demo deployments.
Data survives server restarts.
"""
from __future__ import annotations

import os
import json
import logging
import threading
from pathlib import Path

logger = logging.getLogger("nuvox")

# ── File-based persistence ─────────────────────────────────────────
# Use relative path from this file's directory
DB_FILE = Path(__file__).parent / "local_db.json"
_lock   = threading.Lock()

def _load_db() -> dict:
    if DB_FILE.exists():
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load DB, starting fresh: {e}")
    return {"resumes": [], "interviews": [], "messages": [], "reports": []}

def _save_db(db: dict):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=2)
    except IOError as e:
        logger.error(f"Failed to save DB: {e}")

# ─── Resumes ──────────────────────────────────────────────────────

def save_resume(resume_id: str, resume_text: str, skills: list, projects: list):
    data = {"id": resume_id, "resume_text": resume_text, "skills": skills, "projects": projects}
    with _lock:
        db = _load_db()
        db["resumes"].append(data)
        _save_db(db)

def get_resume(resume_id: str) -> dict | None:
    with _lock:
        db = _load_db()
    for r in db["resumes"]:
        if r["id"] == resume_id:
            return r
    return None

def get_latest_resume() -> dict | None:
    with _lock:
        db = _load_db()
    return db["resumes"][-1] if db["resumes"] else None

def get_resume_by_interview(interview_id: str) -> dict | None:
    interview = get_interview(interview_id)
    if not interview:
        return None
    resume_id = interview.get("resume_id")
    if not resume_id:
        return get_latest_resume()
    return get_resume(resume_id)

# ─── Interviews ───────────────────────────────────────────────────

def create_interview(interview_id: str, persona: str, resume_id: str = None):
    data = {"id": interview_id, "persona": persona}
    if resume_id:
        data["resume_id"] = resume_id
    with _lock:
        db = _load_db()
        db["interviews"].append(data)
        _save_db(db)

def get_interview(interview_id: str) -> dict | None:
    with _lock:
        db = _load_db()
    for i in db["interviews"]:
        if i["id"] == interview_id:
            return i
    return None

# ─── Messages ─────────────────────────────────────────────────────

def save_message(interview_id: str, question: str, answer: str):
    data = {"interview_id": interview_id, "question": question or "", "answer": answer or ""}
    with _lock:
        db = _load_db()
        db["messages"].append(data)
        _save_db(db)

def get_interview_messages(interview_id: str) -> list:
    with _lock:
        db = _load_db()
    return [m for m in db["messages"] if m["interview_id"] == interview_id]

# ─── Reports ──────────────────────────────────────────────────────

def save_report(
    report_id: str,
    interview_id: str,
    score: int,
    communication: int,
    technical: int,
    confidence: int,
    feedback: str,
    strengths: list,
    improvements: list,
    recommendation: str,
    transcript: str,
):
    data = {
        "id": report_id,
        "interview_id": interview_id,
        "score": score,
        "communication": communication,
        "technical": technical,
        "confidence": confidence,
        "feedback": feedback,
        "strengths": strengths,
        "improvements": improvements,
        "recommendation": recommendation,
        "transcript": transcript,
    }
    with _lock:
        db = _load_db()
        # Remove any old report for this interview first (upsert behaviour)
        db["reports"] = [r for r in db["reports"] if r.get("interview_id") != interview_id]
        db["reports"].append(data)
        _save_db(db)

def get_report(interview_id: str) -> dict | None:
    with _lock:
        db = _load_db()
    for r in db["reports"]:
        if r["interview_id"] == interview_id:
            return r
    return None
