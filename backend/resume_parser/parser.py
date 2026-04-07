import io
import pdfplumber
import re
import logging

logger = logging.getLogger("nuvox")


def parse_resume_pdf(pdf_bytes: bytes) -> dict:
    """
    Parse a PDF resume and extract text, skills, and projects.

    Args:
        pdf_bytes: Raw PDF file bytes

    Returns:
        Dictionary with 'text', 'skills', and 'projects' keys
    """
    text = ""

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {str(e)}")

    if not text.strip():
        raise ValueError("Could not extract any text from the PDF.")

    skills = extract_skills(text)
    projects = extract_projects(text)

    logger.info(f"Resume parsed: {len(text)} chars, {len(skills)} skills, {len(projects)} projects")

    return {
        "text": text.strip(),
        "skills": skills,
        "projects": projects,
    }


def extract_skills(text: str) -> list:
    """Extract skills from resume text using word-boundary matching."""

    # Skills with their regex patterns — short skills use word boundaries
    # to prevent false positives (e.g. "C" matching "Computer")
    known_skills = {
        # Programming languages (short names need strict whitespace/punctuation boundaries)
        "Python": r'\bPython\b',
        "Java": r'\bJava\b(?!Script)',  # Java but NOT JavaScript
        "JavaScript": r'\bJavaScript\b',
        "TypeScript": r'\bTypeScript\b',
        "C": r'(?<!\w)C(?!\w)(?!\+\+|#|\w)',  # strictly isolated C
        "C++": r'(?<!\w)C\+\+',
        "C#": r'(?<!\w)C#',
        "Go": r'(?<!\w)Go(?:lang)?(?!\w)(?!\s*(?:to|for|ahead|back|on|ing|od|al|es|ver))',  # isolated Go
        "Rust": r'\bRust\b',
        "Ruby": r'\bRuby\b',
        "PHP": r'\bPHP\b',
        "Swift": r'\bSwift\b',
        "Kotlin": r'\bKotlin\b',
        "Dart": r'\bDart\b',
        "R": r'(?<!\w)R(?!\w)(?!\s*(?:&|and|e(?:search|port|sults|view|ference|sponsi|d|ceived|mote|levant)))',
        "MATLAB": r'\bMATLAB\b',
        "Scala": r'\bScala\b',

        # Web technologies
        "HTML": r'\bHTML\b',
        "CSS": r'\bCSS\b',
        "React": r'\bReact\b',
        "Angular": r'\bAngular\b',
        "Vue": r'\bVue\b',
        "Next.js": r'\bNext\.js\b',
        "Node.js": r'\bNode\.js\b',
        "Express": r'\bExpress\b(?:\.js)?',
        "Django": r'\bDjango\b',
        "Flask": r'\bFlask\b',
        "FastAPI": r'\bFastAPI\b',
        "Spring Boot": r'\bSpring\s*Boot\b',
        "Laravel": r'\bLaravel\b',

        # Databases
        "SQL": r'\bSQL\b',
        "MySQL": r'\bMySQL\b',
        "PostgreSQL": r'\bPostgreSQL\b',
        "MongoDB": r'\bMongoDB\b',
        "Redis": r'\bRedis\b',
        "Firebase": r'\bFirebase\b',
        "Supabase": r'\bSupabase\b',
        "DBMS": r'\bDBMS\b',
        "NoSQL": r'\bNoSQL\b',

        # Cloud & DevOps
        "AWS": r'\bAWS\b',
        "Azure": r'\bAzure\b',
        "GCP": r'\bGCP\b',
        "Google Cloud": r'\bGoogle\s*Cloud\b',
        "Docker": r'\bDocker\b',
        "Kubernetes": r'\bKubernetes\b',
        "Git": r'\bGit\b(?!Hub)',  # Git but NOT GitHub
        "GitHub": r'\bGitHub\b',
        "Linux": r'\bLinux\b',

        # AI/ML
        "TensorFlow": r'\bTensorFlow\b',
        "PyTorch": r'\bPyTorch\b',
        "Scikit-learn": r'\bScikit[- ]learn\b',
        "Pandas": r'\bPandas\b',
        "NumPy": r'\bNumPy\b',
        "Machine Learning": r'\bMachine\s*Learning\b',
        "Deep Learning": r'\bDeep\s*Learning\b',
        "NLP": r'\bNLP\b',
        "Computer Vision": r'\bComputer\s*Vision\b',
        "Data Science": r'\bData\s*Science\b',
        "Data Analysis": r'\bData\s*Analy(?:sis|tics)\b',

        # BI & Visualization
        "Tableau": r'\bTableau\b',
        "Power BI": r'\bPower\s*BI\b',
        "Excel": r'\bExcel\b',

        # Testing
        "Selenium": r'\bSelenium\b',
        "Jest": r'\bJest\b',
        "Cypress": r'\bCypress\b',
        "JUnit": r'\bJUnit\b',
        "Manual Testing": r'\bManual\s*Testing\b',

        # Design
        "Figma": r'\bFigma\b',
        "Adobe XD": r'\bAdobe\s*XD\b',

        # Practices
        "DevOps": r'\bDevOps\b',
        "CI/CD": r'\bCI\s*/?\s*CD\b',
        "Agile": r'\bAgile\b',
        "Scrum": r'\bScrum\b',
        "REST API": r'\bREST\s*API\b',
        "GraphQL": r'\bGraphQL\b',
        "WebSocket": r'\bWebSocket\b',

        # Frameworks/CSS
        "Tailwind": r'\bTailwind\b',
        "Bootstrap": r'\bBootstrap\b',
        "Material UI": r'\bMaterial\s*UI\b',

        # Security tools
        "Burp Suite": r'\bBurp\s*Suite\b',
        "Wireshark": r'\bWireshark\b',
        "Kali Linux": r'\bKali\s*Linux\b',

        # Virtualization
        "VMware": r'\bVMware\b',
        "VirtualBox": r'\bVirtualBox\b',

        # Marketing/Business
        "SEO": r'\bSEO\b',
        "SEM": r'\bSEM\b',
        "Google Analytics": r'\bGoogle\s*Analytics\b',
        "CRM": r'\bCRM\b',
        "Digital Marketing": r'\bDigital\s*Marketing\b',
    }

    found_skills = []
    
    # Pre-calculate skills section bounds for 1-char filtering
    text_lower = text.lower()
    skills_context_indices = []
    for keyword in ["skills", "technologies", "stack", "tools"]:
        for match in re.finditer(r'\b' + re.escape(keyword) + r'\b', text_lower):
            start = max(0, match.start() - 500)
            end = min(len(text_lower), match.end() + 500)
            skills_context_indices.append((start, end))

    for skill_name, pattern in known_skills.items():
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if not matches:
            continue
            
        if len(skill_name) == 1:
            valid_match = False
            for match in matches:
                # Must be inside a skills section context
                if any(start <= match.start() <= end for start, end in skills_context_indices):
                    valid_match = True
                    break
            if not valid_match:
                continue
                
        found_skills.append(skill_name)

    return list(set(found_skills))


def extract_projects(text: str) -> list:
    """Extract project names and descriptions from resume text."""
    projects = []

    projects_section = extract_section(text, ["projects", "personal projects", "academic projects", "key projects"])
    if not projects_section:
        return []

    # Split into individual project blocks
    lines = projects_section.split("\n")
    current_project = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Skip lines that are clearly not project titles
        if len(line) < 5:
            continue
        if len(line) > 80:
            # Long lines are descriptions, not titles
            if current_project:
                current_project["description"] += line + " "
            continue

        # Bullet points are descriptions
        if line.startswith(("•", "-", "–", "*", "▪", "○")):
            if current_project:
                # Clean bullet prefix
                desc_text = re.sub(r'^[•\-–*▪○]\s*', '', line)
                current_project["description"] += desc_text + " "
            continue

        # Filter out garbage: must contain at least 2 words and look like a title
        words = line.split()
        if len(words) < 2:
            continue

        # Skip lines that look like section content, not titles
        # (starts with lowercase, or is a sentence fragment)
        if line[0].islower() and not line.startswith(("e-", "i-")):
            if current_project:
                current_project["description"] += line + " "
            continue

        # This looks like a project title
        if current_project and current_project["name"]:
            projects.append(current_project)
        current_project = {"name": line, "description": ""}

    if current_project and current_project["name"]:
        projects.append(current_project)

    # Clean up: trim descriptions, filter out garbage entries
    cleaned = []
    
    # Project title delimiters
    delimiters = [" - ", " | ", " : ", " — "]
    reject_words = ["solutions", "insights", "actionable", "responsible", 
                    "utilizing", "leveraging", "experience", "skills"]
                    
    for p in projects[:5]:  # Max 5 projects
        name = p["name"]
        
        # Split on delimiters and take the first part
        for delim in delimiters:
            if delim in name:
                name = name.split(delim)[0]
                
        name = name.strip()
        desc = p["description"].strip()

        # Reject names longer than 60 chars
        if len(name) > 60:
            continue
            
        # Reject names containing description words
        name_lower = name.lower()
        if any(rw in name_lower for rw in reject_words):
            continue

        # Skip entries with garbage names (too generic or fragment-like)
        if name.endswith(".") and len(name.split()) <= 4:
            continue
        if name.lower() in ["skills", "education", "experience", "certifications"]:
            continue

        cleaned.append({"name": name, "description": desc[:300]})  # Cap description length

    if len(cleaned) < 2:
        return []
        
    return cleaned


def extract_section(text: str, section_names: list) -> str:
    """Extract a section from resume text by looking for section headers."""
    lines = text.split("\n")
    capturing = False
    section_text = ""

    # Common section header patterns
    section_headers = [
        "education", "experience", "work experience", "skills", "technical skills",
        "projects", "personal projects", "academic projects", "key projects",
        "certifications", "achievements", "publications", "interests",
        "languages", "summary", "objective", "contact", "references",
        "tools", "technologies", "leadership", "involvement",
        "positions of responsibility",
    ]

    for line in lines:
        line_clean = line.strip().lower()

        if any(name in line_clean for name in section_names):
            capturing = True
            continue

        if capturing:
            # Stop if we hit another section header
            if any(header in line_clean for header in section_headers if header not in section_names):
                if len(line_clean) < 40:  # Likely a header, not content
                    break
            section_text += line + "\n"

    return section_text.strip()
