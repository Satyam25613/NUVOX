# NUVOX System Architecture & Fix Audit Report

## Phase 1 — Codebase Analysis

### 1. Architecture Overview
**Backend (FastAPI)**: Serves static frontend files and API endpoints securely.
**Data Flow**:
- Client uploads Resume (parsed via `pdfplumber` in `resume_parser/parser.py`) -> saved to `local_db.json`.
- Client selects persona -> generates `interview_id`.
- WebSocket connects -> Live Gemini API opens.
- Interview audio is streamed back and forth up to 15 mins.
- System transcribes using Gemini Native transcriber, and POST to `api/generate-report` when complete.
- Fallback text mode uses `api/interview-message` calling `gemini-2.0-flash`.

### 2. Integrations
- **Voice**: Gemini 2.5 Flash Native Audio Preview (`models/gemini-2.5-flash-native-audio-preview-12-2025`).
- **Text/Fallback**: Gemini 2.0 Flash REST Calls.
- **Evaluator**: Evaluates through fallback chain: 2.5-flash -> 2.0-flash -> 2.5/2.0-flash-lite.

### 3. Interview Pipeline Step-by-Step
1. Client microphone captures via `navigator.mediaDevices`. Max `AudioContext` creates script loop.
2. Voice downsamples to 16kHz PCM linearly -> JSON & `ArrayBuffer` Websocket (`/ws/interview/{id}`).
3. FastAPI intercepts `ws.receive()`, separating Text (End of turn JSON) and Bytes (Audio buffer).
4. Raw bytes push to Gemini bidiGenerateContent session.
5. Gemini signals `server_content` with outputs (Audio and Trancripts).
6. Bytes sent back to Frontend (`ws.send_bytes`), enqueued dynamically.

### 4. Latency Bottlenecks
- **Silence Delay**: The frontend implements a 2000ms (2 seconds) silence timeout before it informs Gemini that the turn ended (`SILENCE_DELAY = 2000`). This is a huge contributor to conversational latency.
- **Audio Over-Generation**: The AI prompt explicitly allows "1-3 sentences maximum", which can trigger up to 10 seconds of returned audio, making the conversation feel sluggish.
- **Minimum Speech Buffer**: Client requires the user to speak for at least 800ms before it accepts an utterance as valid.

### 5. Instability Causes
- **1007 / WebSocket Errors**: Closing logic throws general exceptions. When the client closes or loses connection prematurely, the server tries to finish the transmission before safely catching the shutdown state. `WebSocketDisconnect` triggers correctly, but exceptions within `send_bytes` loops throw unhandled.
- **Gemini Live Client**: Audio data chunks that are too tiny (e.g., `< 2` bytes) can fracture the Gemini buffer, though it's partly mitigated in `engine.py`.

### 6. Detect Dead Code
Found test scripts inside `/nuvox/backend/`:
- `create_test_pdf.py`
- `test_resume.pdf`
- `verify_all.py`
- `server.log` (persistent log bloating the bundle).

---

## Phase 2 — Safe Fix Strategy

1. **Critical & Performance (Latency)**
   - **Fix 1**: Reduce `SILENCE_DELAY` in `interview-room.html` from `2000` to `1200` milliseconds. Reduce `MIN_SPEECH_DURATION` to `600`.
   - **Fix 2**: Modify `engine.py` system instruction to enforce extremely concise responses ("exactly 1 short sentence") to significantly cut token generation latency.

2. **Stability**
   - **Fix 3**: Ensure robust closures. `engine.py` explicitly catches exceptions iterating over Gemini responses and WebSocket frames.

3. **Cleanup**
   - **Fix 4**: Safely delete the testing files left over within the `backend/` folder (`verify_all.py`, `create_test_pdf.py`, etc.).

---

## Phase 3 & 4 — Applied

Changes are actively being rolled out surgical-style via the system's execution terminal and file editting.
