# NUVOX — Product Requirements Document (PRD)

## 1. Product Overview

**NUVOX** is an AI-powered mock interview platform for students. It enables students to practice interviews with 7 different AI interviewer personas, using real-time voice interaction powered by Google's Gemini Live API.

### Mission
Help students prepare for job interviews through realistic AI-driven practice sessions with personalized feedback.

### Target Users
- College students preparing for campus placements
- Job seekers practicing for technical and non-technical interviews
- Anyone wanting to improve their interview skills

## 2. Key Features

### 2.1 Authentication
- Email/password sign-up and login via Supabase Auth
- Secure session management
- Redirect to dashboard after login

### 2.2 Resume Upload
- PDF resume upload (max 5MB)
- AI-powered resume parsing to extract skills, projects, and experience
- Parsed data used to personalize interview questions

### 2.3 Persona Selection
- 7 interviewer personas:
  1. Software Developer — DSA, algorithms, coding
  2. Web Developer — HTML/CSS/JS, React, APIs
  3. QA Engineer — testing, automation, bug tracking
  4. Marketing Specialist — digital marketing, campaigns
  5. Sales Executive — sales techniques, objection handling
  6. Product Manager — product thinking, prioritization
  7. Data Analyst — SQL, Excel, Tableau, statistics

### 2.4 Live Voice Interview
- Real-time voice conversation using Gemini Live API
- Audio format: 16-bit PCM, 16kHz mono (input), 24kHz (output)
- Session limits: 12 questions OR 15 minutes (whichever comes first)
- On-screen timer
- Automatic session ending with report trigger

### 2.5 AI Evaluation
- Post-interview transcript analysis via Gemini text API
- 4 scored metrics (1-10): Communication, Technical, Confidence, Problem Solving
- Overall feedback (150-300 words)
- 3 areas of improvement
- 3 suggested topics to study

### 2.6 Report Page
- Visual score cards with circular progress indicators
- Detailed feedback display
- Actionable improvement suggestions

## 3. Non-Functional Requirements

- **Cost**: ₹0 — all free tiers only
- **Performance**: Real-time audio < 500ms latency
- **Browser Support**: Chrome, Firefox, Edge
- **Security**: No hardcoded API keys, Supabase RLS
- **Error Handling**: All errors shown to user, no silent failures

## 4. Constraints

- Gemini Live API only (no Deepgram, no Attendee API)
- No paid APIs allowed
- Fallback to text mode if voice is unstable
