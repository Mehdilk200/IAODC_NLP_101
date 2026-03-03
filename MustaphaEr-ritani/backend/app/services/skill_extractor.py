"""
Skill Extractor Service.
Uses Google Gemini API for intelligent, context-aware skill extraction.
Falls back to dictionary matching if Gemini is unavailable.
"""

import json
import logging
import re
from typing import List, Set, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Gemini API Integration
# ─────────────────────────────────────────────

def _get_gemini_model():
    """Get configured Gemini model instance."""
    try:
        from app.core.config import settings
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set, Gemini extraction disabled")
            return None

        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        logger.info("✅ Gemini model configured")
        return model
    except Exception as e:
        logger.error(f"Failed to configure Gemini: {e}")
        return None


# ─────────────────────────────────────────────
# Gemini Skill Extraction Prompts
# ─────────────────────────────────────────────

CV_SKILL_PROMPT = """You are an expert technical recruiter analyzing a CV/resume.

Extract ONLY the actual technical skills, tools, frameworks, programming languages, platforms, and technologies that this person demonstrably has based on their CV.

STRICT RULES:
1. Extract ONLY real, concrete technical skills (things you can install, code with, configure, deploy)
2. DO NOT extract:
   - Job titles (e.g. "Developer", "Engineer", "Data Scientist")
   - Soft skills (e.g. "leadership", "communication", "teamwork")
   - Education degrees (e.g. "Bachelor", "Master", "PhD")
   - Generic words (e.g. "development", "system", "application", "project")
   - Company names or locations
   - Phrases or sentences
   - Personal info (names, emails, phones)
3. Normalize skill names to their standard form (e.g. "reactjs" → "React", "node.js" → "Node.js", "mongo" → "MongoDB")
4. Keep multi-word skills as one item (e.g. "Machine Learning", "Deep Learning", "Power BI")
5. For French CVs, translate skill names to English (e.g. "apprentissage automatique" → "Machine Learning")

Return ONLY a JSON array of skill strings, nothing else.
Example output: ["Python", "React", "MongoDB", "Docker", "Machine Learning", "TensorFlow"]

CV TEXT:
{text}
"""

JOB_SKILL_PROMPT = """You are an expert technical recruiter analyzing a job description.

Extract ONLY the required technical skills, tools, frameworks, programming languages, platforms, and technologies from this job description.

STRICT RULES:
1. Extract ONLY real, concrete technical skills that are required or preferred (things you can install, code with, configure, deploy)
2. DO NOT extract:
   - Job titles or role names
   - Soft skills
   - Education requirements
   - Generic words (e.g. "development", "application", "system")
   - Action verbs (e.g. "build", "integrate", "deploy")
   - Company names or locations
3. Normalize skill names to their standard form (e.g. "reactjs" → "React", "postgres" → "PostgreSQL")
4. Keep multi-word skills as one item (e.g. "Machine Learning", "REST API", "Power BI")

Return ONLY a JSON array of skill strings, nothing else.
Example output: ["Python", "FastAPI", "React", "Docker", "Machine Learning", "PostgreSQL"]

JOB DESCRIPTION:
{text}
"""


def extract_skills_gemini(text: str, is_job: bool = False) -> List[str]:
    """
    Extract skills using Gemini API.
    Uses different prompts for CVs vs job descriptions.

    Args:
        text: The CV or job description text
        is_job: If True, uses job description prompt

    Returns:
        List of extracted skill strings, or empty list on failure
    """
    model = _get_gemini_model()
    if not model:
        return []

    if not text or not text.strip():
        return []

    # Truncate to avoid token limits (Gemini handles long context well, but be safe)
    text_truncated = text[:8000]

    prompt = (JOB_SKILL_PROMPT if is_job else CV_SKILL_PROMPT).format(text=text_truncated)

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.1,  # Low temperature for deterministic extraction
                "max_output_tokens": 1024,
            }
        )

        raw_response = response.text.strip()
        logger.info(f"Gemini raw response: {raw_response[:200]}...")

        # Parse JSON array from response
        # Handle cases where Gemini wraps response in ```json ... ```
        json_text = raw_response
        if "```" in json_text:
            # Extract content between code fences
            match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', json_text, re.DOTALL)
            if match:
                json_text = match.group(1).strip()

        skills = json.loads(json_text)

        if not isinstance(skills, list):
            logger.warning(f"Gemini returned non-list: {type(skills)}")
            return []

        # Clean and deduplicate
        cleaned = []
        seen = set()
        for skill in skills:
            if isinstance(skill, str):
                s = skill.strip()
                if s and s.lower() not in seen:
                    seen.add(s.lower())
                    cleaned.append(s)

        logger.info(f"✅ Gemini extracted {len(cleaned)} skills: {cleaned}")
        return cleaned

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        logger.error(f"Raw response was: {raw_response[:500]}")
        return []
    except Exception as e:
        logger.error(f"Gemini extraction failed: {e}")
        return []


# ─────────────────────────────────────────────
# Fallback: Dictionary-Based Extraction
# ─────────────────────────────────────────────

TECH_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl",
    # Web Frameworks
    "react", "angular", "vue", "nextjs", "fastapi", "django", "flask",
    "express", "spring", "laravel", "rails", "nodejs", "node.js",
    # Databases
    "mongodb", "postgresql", "mysql", "sqlite", "redis", "elasticsearch",
    "cassandra", "dynamodb", "oracle", "sql server", "firebase",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "github actions", "ci/cd", "linux", "nginx", "apache",
    # ML / AI
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "hugging face", "transformers", "bert", "gpt", "llm", "langchain",
    "opencv", "yolo", "xgboost", "lightgbm",
    # Data
    "data analysis", "data science", "data engineering", "etl",
    "spark", "hadoop", "kafka", "airflow", "dbt", "tableau", "power bi",
    "excel", "sql", "nosql",
    # Security
    "cybersecurity", "penetration testing", "oauth", "jwt", "ssl", "tls",
    # Other Tech
    "git", "rest api", "graphql", "microservices", "api", "json", "xml",
    "html", "css", "sass", "tailwind", "bootstrap",
}

# Normalization Mapping
SKILL_NORMALIZATION = {
    "reactjs": "React", "react.js": "React", "react": "React",
    "node.js": "Node.js", "nodejs": "Node.js",
    "tensorflow": "TensorFlow",
    "mongo": "MongoDB", "mongodb": "MongoDB",
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "aws": "AWS", "amazon web services": "AWS",
    "gcp": "Google Cloud", "google cloud": "Google Cloud",
    "azure": "Azure",
    "docker": "Docker",
    "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "ci/cd": "CI/CD",
    "nlp": "NLP",
    "ai": "AI",
    "ml": "Machine Learning", "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "js": "JavaScript", "javascript": "JavaScript",
    "ts": "TypeScript", "typescript": "TypeScript",
    "py": "Python", "python": "Python",
    "html": "HTML", "css": "CSS",
    "sql": "SQL", "nosql": "NoSQL",
    "git": "Git",
    "pandas": "Pandas", "numpy": "NumPy",
    "pytorch": "PyTorch",
    "keras": "Keras",
    "scikit-learn": "Scikit-learn",
    "fastapi": "FastAPI",
    "django": "Django", "flask": "Flask",
    "linux": "Linux",
    "opencv": "OpenCV",
    "power bi": "Power BI",
    "tableau": "Tableau",
    "kafka": "Kafka", "spark": "Spark",
    "etl": "ETL",
    "jwt": "JWT",
    "rest api": "REST API",
    "graphql": "GraphQL",
    "excel": "Excel",
}

# French skill aliases
FRENCH_SKILL_ALIASES = {
    "apprentissage automatique": "Machine Learning",
    "apprentissage profond": "Deep Learning",
    "traitement du langage naturel": "NLP",
    "vision par ordinateur": "Computer Vision",
    "base de données": "Database",
    "développement web": "Web Development",
    "sécurité informatique": "Cybersecurity",
    "intelligence artificielle": "AI",
    "système de gestion de base de données": "DBMS",
}

# Words that should NOT be matched as the single-letter/short skill "r" or "go"
SHORT_SKILL_FALSE_POSITIVES = {"r", "go", "c"}


def extract_skills_dictionary(text: str) -> Set[str]:
    """
    Fallback: Match skills from curated dictionary using word-boundary matching.
    More precise than simple substring matching.
    """
    text_lower = text.lower()
    found = set()

    # Check French aliases first
    for fr_skill, en_skill in FRENCH_SKILL_ALIASES.items():
        if fr_skill in text_lower:
            found.add(en_skill)

    # Check tech skills with word-boundary matching
    for skill in TECH_SKILLS:
        if skill in SHORT_SKILL_FALSE_POSITIVES:
            # For short skills like "r", "go", "c" — require word boundaries
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)
        elif len(skill) <= 3:
            # Short skills need word boundary check
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)
        else:
            # Longer skills can use substring match
            if skill in text_lower:
                found.add(skill)

    # Normalize found skills
    normalized = set()
    for skill in found:
        norm = SKILL_NORMALIZATION.get(skill, skill.title())
        normalized.add(norm)

    return normalized


# ─────────────────────────────────────────────
# Main Extraction Function
# ─────────────────────────────────────────────

def extract_skills(text: str, is_job: bool = False) -> List[str]:
    """
    Extract skills from text using Gemini API (primary) with dictionary fallback.

    Strategy:
    1. Try Gemini API first (most accurate, context-aware)
    2. Fall back to dictionary matching if Gemini fails or is unavailable

    Args:
        text: CV or job description text
        is_job: Whether the text is a job description

    Returns:
        Sorted, deduplicated list of skill strings
    """
    if not text or not text.strip():
        return []

    # Primary: Gemini API
    gemini_skills = extract_skills_gemini(text, is_job=is_job)

    if gemini_skills:
        logger.info(f"Using Gemini extraction ({len(gemini_skills)} skills)")
        return sorted(gemini_skills)

    # Fallback: Dictionary matching
    logger.warning("Gemini unavailable, falling back to dictionary matching")
    dict_skills = extract_skills_dictionary(text)
    return sorted(list(dict_skills))


# ─────────────────────────────────────────────
# Skill Comparison (Matching Logic)
# ─────────────────────────────────────────────

def normalize_skill(skill: str) -> str:
    """
    Normalize skill string for consistent matching.
    """
    s = skill.lower().strip()

    # Check manual mapping first
    if s in SKILL_NORMALIZATION:
        return SKILL_NORMALIZATION[s].lower()

    return s


def compare_skills(cv_skills: List[str], job_skills: List[str]):
    """
    Compare CV skills against job required skills intelligently.
    1. Exact Match (Normalized)
    2. Semantic Match (Embeddings > 0.75)

    Returns:
        matched_skills: List[str]
        missing_skills: List[str]
        match_score: float (0-100)
    """
    from sentence_transformers import util
    from app.services.embedding import _get_model as get_embedding_model

    if not job_skills:
        return [], [], 0.0

    # 1. Normalize all skills
    norm_cv = {}
    for s in cv_skills:
        n = normalize_skill(s)
        norm_cv[n] = s

    norm_job = {}
    for s in job_skills:
        n = normalize_skill(s)
        norm_job[n] = s

    cv_set = set(norm_cv.keys())
    job_set = set(norm_job.keys())

    # 2. Exact Match
    exact_matches = cv_set.intersection(job_set)
    matched_display = {norm_job[m] for m in exact_matches}

    # Identify remaining
    remaining_job = list(job_set - exact_matches)
    remaining_cv = list(cv_set - exact_matches)

    # 3. Semantic Match
    if remaining_job and remaining_cv:
        try:
            model = get_embedding_model()
            job_emb = model.encode(remaining_job, convert_to_tensor=True)
            cv_emb = model.encode(remaining_cv, convert_to_tensor=True)

            cosine_scores = util.cos_sim(job_emb, cv_emb)
            threshold = 0.75

            for i, job_skill_norm in enumerate(remaining_job):
                best_score = cosine_scores[i].max()
                if best_score >= threshold:
                    best_match_idx = cosine_scores[i].argmax().item()
                    matched_cv_skill = remaining_cv[best_match_idx]
                    matched_display.add(norm_job[job_skill_norm])
                    logger.info(
                        f"Semantic Match: '{job_skill_norm}' ≈ '{matched_cv_skill}' "
                        f"(Score: {best_score:.2f})"
                    )

        except Exception as e:
            logger.error(f"Semantic matching failed: {e}")

    # 4. Final Compile
    final_matched = sorted(list(matched_display))

    norm_matched_set = {normalize_skill(s) for s in final_matched}

    final_missing = []
    for s in job_skills:
        if normalize_skill(s) not in norm_matched_set:
            final_missing.append(s)

    final_missing = sorted(list(set(final_missing)))

    # 5. Score = matched / total * 100
    score = (len(final_matched) / len(job_skills)) * 100
    score = round(score, 2)

    return final_matched, final_missing, score
