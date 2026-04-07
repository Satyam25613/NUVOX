# NUVOX — Development Blueprint

## Build Sequence

| Phase | Name | Status |
|-------|------|--------|
| 1 | Project Setup | ✅ Complete |
| 2 | Authentication | ✅ N/A — No Auth (MVP) |
| 3 | Resume Upload | 🔲 Pending |
| 4 | Persona Selection | 🔲 Pending |
| 5 | Interview Engine | 🔲 Pending |
| 6 | Evaluation Engine | 🔲 Pending |
| 7 | Report Page | 🔲 Pending |
| 8 | Testing & Cleanup | 🔲 Pending |

## Database Schema (Supabase SQL)

Run this SQL in Supabase SQL Editor to create all tables:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Resumes table (no user_id — MVP, no auth)
CREATE TABLE IF NOT EXISTS resumes (
    id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_text text,
    skills      jsonb,
    projects    jsonb
);

-- Interviews table
CREATE TABLE IF NOT EXISTS interviews (
    id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id   uuid REFERENCES resumes(id),
    persona     text,
    date        timestamp DEFAULT now()
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_id    uuid REFERENCES interviews(id),
    question        text,
    answer          text,
    timestamp       timestamp DEFAULT now()
);

-- Reports table
CREATE TABLE IF NOT EXISTS reports (
    id                      uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_id            uuid REFERENCES interviews(id),
    communication_score     integer,
    technical_score         integer,
    confidence_score        integer,
    problem_solving_score   integer,
    feedback                jsonb
);
```

## Environment Variables

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Backend (`backend/.env`)
```
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SECRET_KEY=your_secret_key
```

## Running Locally

### Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# → http://localhost:8000
```

## Gemini Live API Configuration

- **Model**: `gemini-2.5-flash-native-audio-preview-12-2025`
- **Input Audio**: 16-bit PCM, 16kHz, mono (`audio/pcm`)
- **Output Audio**: 24kHz
- **Session Limits**: 12 questions OR 15 minutes

## Deployment

| Component | Platform | Command |
|-----------|----------|---------|
| Frontend | Vercel | `vercel --prod` |
| Backend | Render | Docker or Git deploy |
| Database | Supabase | Already hosted |
