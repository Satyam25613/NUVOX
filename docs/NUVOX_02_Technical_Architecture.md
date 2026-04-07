# NUVOX — Technical Architecture

## 1. System Architecture

```
┌─────────────┐     HTTP/WS      ┌──────────────┐     API      ┌─────────────┐
│   Frontend   │ ◄──────────────► │   Backend    │ ◄──────────► │   Gemini    │
│  (Next.js)   │                  │  (FastAPI)   │              │   Live API  │
│  Port: 3000  │                  │  Port: 8000  │              │             │
└─────────────┘                   └──────┬───────┘              └─────────────┘
                                         │
                                         │ SQL
                                         ▼
                                  ┌──────────────┐
                                  │   Supabase   │
                                  │  (PostgreSQL)│
                                  └──────────────┘
```

## 2. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js (Pages Router) | UI, routing, SSR |
| Styling | Tailwind CSS | Utility-first CSS |
| Backend | FastAPI | REST API + WebSocket |
| Voice AI | Gemini Live API | Real-time voice interview |
| Eval AI | Gemini 2.0 Flash | Report generation (text) |
| Database | Supabase (PostgreSQL) | Data persistence |
| Auth | Supabase Auth | User authentication |
| PDF Parsing | pdfplumber | Resume text extraction |

## 3. Data Flow

### Interview Flow
```
1. Student logs in → Dashboard
2. Uploads resume → PDF parsed → Skills extracted → Stored in Supabase
3. Selects persona → Interview session created in Supabase
4. Interview room opens → WebSocket connects to FastAPI
5. FastAPI connects to Gemini Live API with persona prompt + resume context
6. Browser captures mic → 16kHz PCM → FastAPI → Gemini Live API
7. Gemini responds → Audio → FastAPI → Browser (playback)
8. Each Q&A turn saved to messages table
9. Session auto-ends at 12 questions OR 15 minutes
10. Report generated via Gemini text API → Saved to reports table
11. Student sees report with scores and feedback
```

### Audio Pipeline
```
Browser Mic → MediaStream API → ScriptProcessor → Float32 → PCM16 (16kHz mono)
    ↓
WebSocket → FastAPI → Gemini Live API (audio/pcm)
    ↓
Gemini Response Audio (24kHz) → FastAPI → WebSocket → Browser → AudioContext → Speaker
```

## 4. API Architecture

### HTTP Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/upload-resume` | Upload and parse PDF |
| POST | `/api/start-interview` | Create interview session |
| POST | `/api/interview-message` | Save Q&A (text fallback) |
| POST | `/api/generate-report` | Trigger report generation |
| GET | `/api/report/{interview_id}` | Fetch report |

### WebSocket
| Type | Endpoint | Purpose |
|------|----------|---------|
| WS | `/ws/interview/{interview_id}` | Real-time voice stream |

## 5. Database Schema

5 tables: `users`, `resumes`, `interviews`, `messages`, `reports`

See `NUVOX_03_Development_Blueprint.md` for full schema.

## 6. Deployment Architecture

| Component | Platform | Tier |
|-----------|----------|------|
| Frontend | Vercel | Free |
| Backend | Render | Free |
| Database | Supabase | Free |
| AI | Google AI Studio | Free |
