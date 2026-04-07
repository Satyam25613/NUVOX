# NUVOX — UI/UX Design Skill
## Complete Frontend Design System for Antigravity
**Version:** 1.0 | **Style:** Glassmorphism + Dark Luxury

---

> **INSTRUCTION FOR ANTIGRAVITY:**
> This document defines the complete visual identity of NUVOX.
> Every page, every component, every color, every font must follow this system exactly.
> Do not use your own design judgment. Follow this skill document.
> If something is not defined here, ask before designing it.

---

## 1. The Problem NUVOX Solves (Design Context)

Understanding the problem shapes the design. Read this before designing anything.

**The Student's Reality:**
A final year student sitting alone in their hostel room, nervous about upcoming interviews. They have no one to practice with. Mock interview services cost ₹2000–₹5000 per session. Their college placement cell gives them a PDF and says "all the best." They show up to the real interview unprepared, they blank out, they fail.

**What NUVOX Does:**
NUVOX gives that student a calm, professional AI interviewer available at midnight, for free, that adapts to their resume, speaks to them in real voice, and tells them exactly what they did wrong — without judgment.

**The Emotional Journey of the User:**
```
Nervous → Opens NUVOX → Feels calmer (clean, professional UI)
                      → Uploads resume (feels seen — it knows me)
                      → Selects persona (feels in control)
                      → Interview starts (feels challenged but safe)
                      → Report arrives (feels honest feedback)
                      → Closes NUVOX (feels more ready than before)
```

**Design Mission:**
The UI must feel like a **premium career tool** — not a student project, not a toy, not a chatbot.
It should feel like something that costs money but is free.
Every screen should make the student feel: *"I am being taken seriously."*

---

## 2. Visual Identity

### Brand Name
```
NUVOX
```

### Tagline
```
New Voice. New Career.
```

### Brand Personality
- **Confident** — not arrogant, but assured
- **Premium** — feels expensive, polished
- **Calm** — reduces anxiety, not adds to it
- **Futuristic** — AI-forward, cutting-edge
- **Trustworthy** — honest feedback, no sugarcoating

---

## 3. Color System

### Base Colors (Dark Theme — Primary)

```css
:root {
  /* Backgrounds */
  --bg-base:        #050810;   /* deep navy black — page background */
  --bg-surface:     #0d1117;   /* slightly lighter — card backgrounds */
  --bg-elevated:    #111827;   /* elevated surfaces */

  /* Glass Effect Colors */
  --glass-bg:       rgba(255, 255, 255, 0.05);   /* glass card fill */
  --glass-border:   rgba(255, 255, 255, 0.10);   /* glass card border */
  --glass-hover:    rgba(255, 255, 255, 0.08);   /* glass hover state */
  --glass-active:   rgba(255, 255, 255, 0.12);   /* glass active/selected */

  /* Brand Accent — Electric Blue */
  --accent-primary:   #3B82F6;   /* main blue — buttons, highlights */
  --accent-bright:    #60A5FA;   /* brighter blue — hover, glow */
  --accent-glow:      rgba(59, 130, 246, 0.3);   /* blue glow for effects */
  --accent-subtle:    rgba(59, 130, 246, 0.1);   /* very subtle blue tint */

  /* Secondary Accent — Cyan */
  --accent-cyan:      #06B6D4;   /* secondary highlights, icons */
  --accent-cyan-glow: rgba(6, 182, 212, 0.25);

  /* Score Colors */
  --score-excellent:  #10B981;   /* green — high scores */
  --score-good:       #3B82F6;   /* blue — medium scores */
  --score-average:    #F59E0B;   /* amber — average scores */
  --score-poor:       #EF4444;   /* red — low scores */

  /* Text */
  --text-primary:   #F1F5F9;   /* main readable text */
  --text-secondary: #94A3B8;   /* secondary labels, descriptions */
  --text-muted:     #475569;   /* disabled, placeholders */
  --text-accent:    #60A5FA;   /* linked text, accent labels */

  /* Borders */
  --border-subtle:  rgba(255, 255, 255, 0.06);
  --border-default: rgba(255, 255, 255, 0.10);
  --border-strong:  rgba(255, 255, 255, 0.18);
  --border-accent:  rgba(59, 130, 246, 0.40);
}
```

### Background Gradient (Apply to `<body>`)

```css
body {
  background-color: var(--bg-base);
  background-image:
    radial-gradient(ellipse 80% 60% at 20% 10%, rgba(59, 130, 246, 0.08) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 80%, rgba(6, 182, 212, 0.06) 0%, transparent 60%),
    radial-gradient(ellipse 40% 40% at 50% 50%, rgba(99, 102, 241, 0.04) 0%, transparent 70%);
  min-height: 100vh;
}
```

---

## 4. Typography

### Font Stack

```css
/* Import in _document.js or globals.css */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

:root {
  --font-display: 'Syne', sans-serif;   /* headings, brand name, titles */
  --font-body:    'Inter', sans-serif;  /* body text, labels, descriptions */
}
```

**Why Syne:** Angular, modern, geometric. Feels like a premium SaaS product. Not overused. Strong at large sizes — perfect for the NUVOX brand name and page headings.

**Why Inter:** Maximum readability for body text, scores, and feedback content.

### Type Scale

```css
/* Brand / Hero */
.text-brand     { font-family: var(--font-display); font-size: 3.5rem;  font-weight: 800; letter-spacing: -0.03em; }
.text-hero      { font-family: var(--font-display); font-size: 2.5rem;  font-weight: 700; letter-spacing: -0.02em; }

/* Page Headings */
.text-h1        { font-family: var(--font-display); font-size: 2rem;    font-weight: 700; letter-spacing: -0.01em; }
.text-h2        { font-family: var(--font-display); font-size: 1.5rem;  font-weight: 600; }
.text-h3        { font-family: var(--font-display); font-size: 1.25rem; font-weight: 600; }

/* Body */
.text-body-lg   { font-family: var(--font-body);    font-size: 1.125rem; font-weight: 400; line-height: 1.7; }
.text-body      { font-family: var(--font-body);    font-size: 1rem;     font-weight: 400; line-height: 1.6; }
.text-small     { font-family: var(--font-body);    font-size: 0.875rem; font-weight: 400; }
.text-label     { font-family: var(--font-body);    font-size: 0.75rem;  font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; }
```

---

## 5. Glassmorphism Design System

### What is Glassmorphism (for Antigravity)

Glassmorphism = frosted glass effect on cards and panels.
It creates depth by layering transparent surfaces over a blurred background.
NUVOX uses this to make the UI feel premium and futuristic without being heavy.

### Core Glass Card

```css
.glass-card {
  background:           var(--glass-bg);
  backdrop-filter:      blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border:               1px solid var(--glass-border);
  border-radius:        16px;
  position:             relative;
  overflow:             hidden;
}

/* Inner top highlight — makes it look like light hits the glass */
.glass-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(255,255,255,0.15) 30%,
    rgba(255,255,255,0.20) 50%,
    rgba(255,255,255,0.15) 70%,
    transparent 100%
  );
}
```

### Glass Card Variants

```css
/* Default — neutral glass */
.glass-card-default {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Accent — blue tinted glass (use for selected states, active cards) */
.glass-card-accent {
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.25);
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.08), inset 0 1px 0 rgba(255,255,255,0.1);
}

/* Success — green tinted glass (use for high scores, completed states) */
.glass-card-success {
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.25);
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.08);
}

/* Warning — amber tinted (use for average scores) */
.glass-card-warning {
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.25);
  box-shadow: 0 0 30px rgba(245, 158, 11, 0.08);
}
```

### Glass Hover Effect

```css
.glass-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
  background:    rgba(255, 255, 255, 0.08);
  border-color:  rgba(255, 255, 255, 0.15);
  transform:     translateY(-2px);
  box-shadow:    0 20px 60px rgba(0, 0, 0, 0.4), 0 0 40px rgba(59, 130, 246, 0.08);
}
```

---

## 6. Component Library

### 6.1 Primary Button

```css
.btn-primary {
  background:      linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
  color:           #fff;
  font-family:     var(--font-display);
  font-size:       0.9rem;
  font-weight:     600;
  letter-spacing:  0.02em;
  padding:         12px 28px;
  border-radius:   10px;
  border:          1px solid rgba(59, 130, 246, 0.4);
  cursor:          pointer;
  position:        relative;
  overflow:        hidden;
  transition:      all 0.25s ease;
  box-shadow:      0 4px 20px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover {
  transform:       translateY(-1px);
  box-shadow:      0 8px 30px rgba(59, 130, 246, 0.5);
  background:      linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%);
}

.btn-primary:active {
  transform:       translateY(0px);
  box-shadow:      0 4px 15px rgba(59, 130, 246, 0.3);
}
```

### 6.2 Secondary Button (Ghost)

```css
.btn-secondary {
  background:      transparent;
  color:           var(--text-primary);
  font-family:     var(--font-display);
  font-size:       0.9rem;
  font-weight:     600;
  padding:         12px 28px;
  border-radius:   10px;
  border:          1px solid var(--border-default);
  cursor:          pointer;
  transition:      all 0.25s ease;
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  border-color:    var(--border-accent);
  background:      var(--accent-subtle);
  color:           var(--accent-bright);
}
```

### 6.3 Input Field

```css
.input-field {
  width:           100%;
  background:      rgba(255, 255, 255, 0.04);
  border:          1px solid var(--border-default);
  border-radius:   10px;
  padding:         14px 18px;
  color:           var(--text-primary);
  font-family:     var(--font-body);
  font-size:       1rem;
  outline:         none;
  transition:      all 0.2s ease;
  backdrop-filter: blur(10px);
}

.input-field::placeholder {
  color: var(--text-muted);
}

.input-field:focus {
  border-color:    var(--accent-primary);
  background:      rgba(59, 130, 246, 0.06);
  box-shadow:      0 0 0 3px rgba(59, 130, 246, 0.15);
}
```

### 6.4 Badge / Tag

```css
.badge {
  display:         inline-flex;
  align-items:     center;
  gap:             6px;
  padding:         4px 12px;
  border-radius:   20px;
  font-family:     var(--font-body);
  font-size:       0.75rem;
  font-weight:     500;
  letter-spacing:  0.04em;
}

.badge-blue {
  background: rgba(59, 130, 246, 0.15);
  border:     1px solid rgba(59, 130, 246, 0.3);
  color:      #93C5FD;
}

.badge-green {
  background: rgba(16, 185, 129, 0.15);
  border:     1px solid rgba(16, 185, 129, 0.3);
  color:      #6EE7B7;
}

.badge-amber {
  background: rgba(245, 158, 11, 0.15);
  border:     1px solid rgba(245, 158, 11, 0.3);
  color:      #FCD34D;
}
```

### 6.5 Score Ring (for Report Page)

```css
/* Circular score display */
.score-ring-container {
  position:   relative;
  width:       100px;
  height:      100px;
  display:     flex;
  align-items: center;
  justify-content: center;
}

.score-value {
  font-family:  var(--font-display);
  font-size:    1.75rem;
  font-weight:  800;
  color:        var(--text-primary);
}

.score-label {
  font-family:  var(--font-body);
  font-size:    0.75rem;
  color:        var(--text-secondary);
  text-align:   center;
  margin-top:   8px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* Use SVG circle with stroke-dasharray for animated ring */
/* stroke color = score color based on value:
   8-10 → var(--score-excellent)
   6-7  → var(--score-good)
   4-5  → var(--score-average)
   1-3  → var(--score-poor)
*/
```

### 6.6 Divider

```css
.divider {
  height:       1px;
  background:   linear-gradient(90deg,
    transparent 0%,
    rgba(255,255,255,0.08) 20%,
    rgba(255,255,255,0.12) 50%,
    rgba(255,255,255,0.08) 80%,
    transparent 100%
  );
  margin:       24px 0;
}
```

---

## 7. Page Designs

### 7.1 Login / Landing Page (`/`)

**Layout:** Centered single column. Full viewport height. Minimal.

**Background:** Dark base with subtle radial blue glow at top-right.

**Elements:**
```
TOP CENTER:
  NUVOX                          ← brand name, Syne 800, 3rem, white
  New Voice. New Career.         ← tagline, Inter 400, 1rem, text-secondary

CENTER CARD (glass-card, max-width 420px):
  "Welcome back"                 ← Syne 700, 1.5rem
  Email input
  Password input
  [Sign In] button               ← btn-primary, full width
  ─────────────────
  "Don't have an account? Sign up"

BOTTOM:
  Small text: "Trusted by 1000+ students"  ← social proof, muted
```

**Vibe:** Calm. Not cluttered. First impression = trust.

---

### 7.2 Dashboard (`/dashboard`)

**Layout:** Left sidebar (64px wide, icon-only) + main content area.

**Sidebar:**
```css
.sidebar {
  width:            64px;
  height:           100vh;
  background:       rgba(255,255,255,0.03);
  border-right:     1px solid var(--border-subtle);
  backdrop-filter:  blur(20px);
  display:          flex;
  flex-direction:   column;
  align-items:      center;
  padding:          24px 0;
  gap:              8px;
  position:         fixed;
  left:             0; top: 0;
}
```

Sidebar icons: Home, Upload, History, Settings. Active icon = accent blue with subtle glow.

**Main Content:**
```
HEADER ROW:
  "Good morning, [Name]"          ← Syne 700, 1.75rem
  "Ready for your next interview?" ← Inter 400, text-secondary

STATS ROW (3 glass cards in a row):
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │  Interviews  │  │  Avg Score   │  │  Best Score  │
  │     12       │  │    7.4/10    │  │    9.2/10    │
  └──────────────┘  └──────────────┘  └──────────────┘

CTA CARD (glass-card-accent, prominent):
  "Start a New Interview"
  "Choose your role and practice with AI"
  [Start Interview →]             ← btn-primary

RECENT INTERVIEWS (list):
  Each row = glass card with:
    persona icon | "Software Developer" | date | score badge | [View Report]
```

---

### 7.3 Resume Upload (`/resume-upload`)

**Layout:** Centered, single column, max-width 600px.

**Step indicator at top:**
```
① Upload Resume  →  ② Select Persona  →  ③ Start Interview
[active]             [inactive]             [inactive]
```

**Upload Zone:**
```css
.upload-zone {
  border:           2px dashed rgba(59, 130, 246, 0.3);
  border-radius:    16px;
  background:       rgba(59, 130, 246, 0.04);
  padding:          60px 40px;
  text-align:       center;
  cursor:           pointer;
  transition:       all 0.3s ease;
}

.upload-zone:hover,
.upload-zone.drag-over {
  border-color:     rgba(59, 130, 246, 0.7);
  background:       rgba(59, 130, 246, 0.08);
  box-shadow:       0 0 40px rgba(59, 130, 246, 0.12);
}
```

Inside upload zone:
```
↑ cloud upload icon (40px, accent blue)
"Drag and drop your resume here"   ← Syne 600, 1.1rem
"or click to browse"               ← Inter 400, text-secondary
"Supports PDF only"                ← badge-blue
```

**After successful upload — extracted skills section:**
```
✓ Resume parsed successfully       ← green badge

YOUR SKILLS (chips):
  [Python] [React] [SQL] [Node.js] [Machine Learning]
  ← each = badge-blue

[Continue to Persona Selection →]  ← btn-primary
```

---

### 7.4 Persona Selection (`/persona-selection`)

**Layout:** 3-column responsive grid (becomes 2-col on tablet, 1-col on mobile).

**Step indicator:** Step 2 active.

**Page title:**
```
"Who's interviewing you today?"    ← Syne 700, 2rem, center
"Pick a role that matches your goal" ← Inter 400, text-secondary, center
```

**Persona Card:**
```css
.persona-card {
  /* glass-card base */
  background:      rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(20px);
  border:          1px solid rgba(255, 255, 255, 0.08);
  border-radius:   16px;
  padding:         28px 24px;
  cursor:          pointer;
  transition:      all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.persona-card:hover {
  transform:       translateY(-4px);
  border-color:    rgba(59, 130, 246, 0.4);
  background:      rgba(59, 130, 246, 0.06);
  box-shadow:      0 20px 60px rgba(0,0,0,0.4), 0 0 40px rgba(59,130,246,0.1);
}

.persona-card.selected {
  border-color:    rgba(59, 130, 246, 0.6);
  background:      rgba(59, 130, 246, 0.10);
  box-shadow:      0 0 0 2px rgba(59,130,246,0.3), 0 20px 60px rgba(0,0,0,0.4);
}
```

**Each card contains:**
```
[Icon — 40px emoji or SVG]
[Role Name — Syne 700, 1.1rem]
[2-line description — Inter 400, 0.875rem, text-secondary]
[3 topic badges — badge-blue, small]
```

**7 Personas and their Icons + Topics:**

| Persona | Icon | Topics shown |
|---------|------|-------------|
| Software Developer | 💻 | Algorithms · Data Structures · System Design |
| Web Developer | 🌐 | React · APIs · CSS |
| QA Engineer | 🧪 | Test Cases · Automation · Bug Tracking |
| Marketing Specialist | 📣 | Campaigns · Analytics · Strategy |
| Sales Executive | 🎯 | Objection Handling · Targets · CRM |
| Product Manager | 📦 | Roadmaps · Metrics · User Research |
| Data Analyst | 📊 | SQL · Visualization · Statistics |

---

### 7.5 Interview Room (`/interview-room`)

**Layout:** Full screen. No sidebar. Immersive.

**Background:** Darker, more atmospheric. Subtle animated gradient pulse during active interview.

**Top Bar:**
```
Left:   NUVOX logo (small)
Center: "Software Developer Interview"   ← persona name
Right:  Timer  |  Question 3/12
```

**Timer Component:**
```css
.interview-timer {
  font-family:     var(--font-display);
  font-size:       1.1rem;
  font-weight:     700;
  color:           var(--text-primary);
  background:      rgba(255,255,255,0.05);
  border:          1px solid var(--border-default);
  border-radius:   8px;
  padding:         6px 14px;
}

/* When under 2 minutes left — turns amber */
.interview-timer.warning {
  color:           #FCD34D;
  border-color:    rgba(245, 158, 11, 0.4);
  background:      rgba(245, 158, 11, 0.08);
}
```

**Center — AI Interviewer Visual:**
```
A circular animated orb (80px diameter):
- Default state:     slow rotating gradient (blue → cyan)
- Speaking state:    pulsing glow, faster animation
- Listening state:   static, subtle border pulse

CSS for orb:
.ai-orb {
  width:  80px; height: 80px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, #3B82F6, #06B6D4, #3B82F6);
  animation: orb-rotate 4s linear infinite;
  box-shadow: 0 0 40px rgba(59,130,246,0.4), 0 0 80px rgba(59,130,246,0.2);
}

@keyframes orb-rotate {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.ai-orb.speaking {
  animation: orb-rotate 1s linear infinite, orb-pulse 0.8s ease-in-out infinite;
  box-shadow: 0 0 60px rgba(59,130,246,0.6), 0 0 120px rgba(59,130,246,0.3);
}

@keyframes orb-pulse {
  0%, 100% { transform: scale(1) rotate(0deg); }
  50%       { transform: scale(1.1) rotate(180deg); }
}
```

**Question Display Card (glass-card):**
```
Shows the current AI question as text
Subtle fade-in animation when new question appears
Max-width: 600px, centered
```

**Bottom — Voice Input Area:**
```
[Microphone button — large, 64px circle]
  - Default:  border pulse animation, blue border
  - Active:   solid blue fill, waveform animation

Below mic: "Click to speak" OR "Listening..." label

Audio Waveform (when student is speaking):
  5 bars of varying height, animated
  Color: var(--accent-cyan)
```

**Text Mode Fallback (if voice disabled):**
```
Replace mic button with:
  Text input box + Send button
  "Type your answer here..."
```

---

### 7.6 Report Page (`/report-page/[interview_id]`)

**Layout:** Centered, max-width 800px. Scrollable.

**Top Section:**
```
✓ Interview Complete               ← badge-green
"Your Performance Report"          ← Syne 800, 2.5rem
"Software Developer · 14 mins 22s · 12 Questions" ← meta, text-secondary
```

**Score Cards Row (4 cards in a row, wrap on mobile):**

Each score card = `glass-card` + score ring:
```
┌─────────────────┐
│   [Ring: 8/10]  │
│                 │
│  Communication  │
│   ●●●●●●●●○○   │  ← dot indicators
└─────────────────┘
```

Score ring color:
- 8–10 → `--score-excellent` (green)
- 6–7  → `--score-good` (blue)
- 4–5  → `--score-average` (amber)
- 1–3  → `--score-poor` (red)

**Overall Feedback Section (glass-card):**
```
"Overall Feedback"                 ← Syne 600, section heading
[Full feedback text paragraph]     ← Inter 400, text-primary, line-height 1.8
```

**Two Column Section:**
```
┌─────────────────────┐  ┌─────────────────────┐
│  Areas to Improve   │  │  Suggested Topics   │
│  ● Answer structure │  │  ● System Design    │
│  ● Technical depth  │  │  ● OOP Concepts     │
│  ● Confidence       │  │  ● DBMS Basics      │
└─────────────────────┘  └─────────────────────┘
```

Left card border = `--score-average` amber tint
Right card border = `--accent-primary` blue tint

**Bottom CTA:**
```
[Practice Again →]    [Download Report]
btn-primary           btn-secondary
```

---

## 8. Animation Guidelines

### Allowed Animations

```css
/* Page entrance — elements fade up on load */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

.animate-fade-up {
  animation: fade-up 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

/* Stagger children: add animation-delay: calc(var(--i) * 0.1s) */

/* Subtle glow pulse — for active elements */
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(59,130,246,0.2); }
  50%       { box-shadow: 0 0 40px rgba(59,130,246,0.5); }
}

/* Score ring fill — animate on report load */
@keyframes ring-fill {
  from { stroke-dashoffset: 283; }  /* 2*PI*45 = 283 */
  to   { stroke-dashoffset: var(--target-offset); }
}
```

### Rules
- All transitions: `0.25s–0.35s ease` or `cubic-bezier(0.4, 0, 0.2, 1)`
- No jarring or fast animations — students are nervous, calm them
- Score rings animate on report page load (satisfying reveal)
- Persona cards have hover lift effect (`translateY(-4px)`)
- No looping animations except the AI orb and mic indicator

---

## 9. Spacing System

```css
/* Use these values only. No random pixel values. */
--space-1:   4px
--space-2:   8px
--space-3:   12px
--space-4:   16px
--space-5:   20px
--space-6:   24px
--space-8:   32px
--space-10:  40px
--space-12:  48px
--space-16:  64px
--space-20:  80px

/* Border radius */
--radius-sm:   6px
--radius-md:   10px
--radius-lg:   16px
--radius-xl:   24px
--radius-full: 9999px
```

---

## 10. Responsive Breakpoints

```css
/* Mobile first */
--screen-sm:  640px    /* small phones */
--screen-md:  768px    /* tablets */
--screen-lg:  1024px   /* laptops */
--screen-xl:  1280px   /* desktops */

/* Persona cards: 3-col → 2-col → 1-col */
/* Stats row: 3-col → 1-col on mobile */
/* Report scores: 4-col → 2-col → 1-col */
/* Sidebar: hidden on mobile, bottom nav instead */
```

---

## 11. What NEVER to Do

- ❌ No white or light backgrounds anywhere
- ❌ No purple gradients (overused, generic AI look)
- ❌ No Inter or Roboto for headings — use Syne only for headings
- ❌ No solid colored buttons without gradient or glow
- ❌ No flat cards without glass effect
- ❌ No lorem ipsum placeholder text
- ❌ No stock photo backgrounds
- ❌ No excessive shadows that look like Material Design
- ❌ No border-radius above 24px on cards
- ❌ No color outside the defined color system

---

## 12. Quick Reference Cheatsheet

```
Background:     #050810 base, radial blue/cyan glow
Cards:          glass — rgba(255,255,255,0.05) + blur(20px) + 1px border
Primary color:  #3B82F6 blue
Secondary:      #06B6D4 cyan
Heading font:   Syne (700/800)
Body font:      Inter (400/500)
Border radius:  16px cards, 10px buttons/inputs
Animation:      fade-up on load, lift on hover, glow on active
Text primary:   #F1F5F9
Text secondary: #94A3B8
Score colors:   green(8-10) blue(6-7) amber(4-5) red(1-3)
```

---

> **FINAL NOTE FOR ANTIGRAVITY:**
> Every page in NUVOX follows this design system.
> Do not introduce new colors, fonts, or components that are not in this document.
> If you need something not defined here, ask before creating it.
> The goal: NUVOX must look like a ₹5000/month SaaS product — even though it is free.
