"""
skill_extractor.py - NLP-based skill extraction from resume and job description text.
Uses spaCy for tokenization/preprocessing and TF-IDF cosine similarity for better matching.
"""

import json
import re
import logging
from pathlib import Path
from typing import Optional

import spacy

# Optional: scikit-learn for TF-IDF cosine similarity
# May not be available on Python 3.13 Windows due to DLL issues
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except (ImportError, OSError) as _sklearn_err:
    SKLEARN_AVAILABLE = False
    import logging as _log
    _log.getLogger(__name__).warning(
        f"[NLP] scikit-learn unavailable ({_sklearn_err}). TF-IDF similarity will be disabled."
    )

logger = logging.getLogger(__name__)

# Load spaCy English model (small model, no GPU required)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("[NLP] spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
    nlp = None

# Load skills database from JSON
SKILLS_JSON_PATH = Path(__file__).parent / "skills.json"

def load_skills_db() -> dict:
    """Load the predefined skills database from skills.json."""
    with open(SKILLS_JSON_PATH, "r") as f:
        return json.load(f)

def preprocess_text(text: str) -> str:
    """
    NLP preprocessing pipeline:
    1. Lowercase conversion
    2. Remove special characters (keep alphanumeric + spaces)
    3. Tokenization via spaCy
    4. Remove stopwords
    5. Return cleaned text

    Args:
        text: Raw input text
    
    Returns:
        Preprocessed text string
    """
    if not text:
        return ""

    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Remove extra whitespace and certain special characters
    text = re.sub(r"[^\w\s\+\#\./]", " ", text)  # keep +, #, ., / for skills like c++, c#, rest api
    text = re.sub(r"\s+", " ", text).strip()

    # Step 3 & 4: Tokenize with spaCy and remove stopwords if model is available
    if nlp:
        doc = nlp(text)
        tokens = [token.text for token in doc if not token.is_stop and len(token.text) > 1]
        return " ".join(tokens)
    else:
        # Fallback: basic whitespace tokenization without stopword removal
        return text


def extract_skills_from_text(text: str, all_skills: list[str]) -> list[str]:
    """
    Extract skills from text by checking if any known skill appears in the text.
    Uses substring/phrase matching to capture multi-word skills (e.g., "machine learning").

    Args:
        text: The preprocessed or raw text to search in
        all_skills: List of known skill strings to look for
    
    Returns:
        Sorted list of found skills
    """
    text_lower = text.lower()
    found_skills = set()

    for skill in all_skills:
        # Use word-boundary aware matching for single words, phrase matching for multi-word
        skill_lower = skill.lower()
        if len(skill_lower.split()) == 1:
            # Single word: match as whole word
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        else:
            # Multi-word skill: phrase match
            if skill_lower in text_lower:
                found_skills.add(skill)

    return sorted(found_skills)


def extract_resume_skills(resume_text: str) -> list[str]:
    """
    Extract skills from the resume text.
    
    Args:
        resume_text: Raw text extracted from PDF resume
    
    Returns:
        List of detected skills from the resume
    """
    skills_db = load_skills_db()
    all_skills = skills_db.get("technical_skills", []) + skills_db.get("soft_skills", [])
    
    # Preprocess resume text
    processed_text = preprocess_text(resume_text)
    
    # Extract skills from both raw and preprocessed text to maximize coverage
    skills_raw = extract_skills_from_text(resume_text, all_skills)
    skills_processed = extract_skills_from_text(processed_text, all_skills)

    # Combine both results
    combined = set(skills_raw) | set(skills_processed)
    logger.info(f"[Extractor] Found {len(combined)} skills in resume.")
    return sorted(combined)


def get_job_role_skills(job_role: str) -> list[str]:
    """
    Return predefined required skills for a specific job role.
    
    Args:
        job_role: Name of the job role (must match key in skills.json)
    
    Returns:
        List of required skills for the job role
    """
    skills_db = load_skills_db()
    job_roles = skills_db.get("job_roles", {})
    return job_roles.get(job_role, [])


def extract_skills_from_job_description(jd_text: str) -> list[str]:
    """
    Extract required skills from a pasted job description.
    Uses the same NLP pipeline as resume extraction.
    
    Args:
        jd_text: Raw job description text pasted by user
    
    Returns:
        List of detected skills in the job description
    """
    skills_db = load_skills_db()
    all_skills = skills_db.get("technical_skills", []) + skills_db.get("soft_skills", [])
    
    # Extract from both raw and preprocessed
    skills_raw = extract_skills_from_text(jd_text, all_skills)
    processed = preprocess_text(jd_text)
    skills_proc = extract_skills_from_text(processed, all_skills)
    
    combined = set(skills_raw) | set(skills_proc)
    logger.info(f"[Extractor] Found {len(combined)} skills in job description.")
    return sorted(combined)


def get_available_job_roles() -> list[str]:
    """Return list of all supported job roles."""
    skills_db = load_skills_db()
    return list(skills_db.get("job_roles", {}).keys())


def compute_tfidf_similarity(resume_text: str, job_text: str) -> float:
    """
    Compute cosine similarity between resume text and job description/role skills
    using TF-IDF vectorization.
    
    This provides a more nuanced similarity score beyond simple skill matching.
    
    Args:
        resume_text: Raw or preprocessed resume text
        job_text: Job description text or space-joined skills
    
    Returns:
        Cosine similarity score as a float between 0.0 and 1.0
    """
    if not resume_text or not job_text:
        return 0.0

    if not SKLEARN_AVAILABLE:
        logger.warning("[TF-IDF] scikit-learn not available. Skipping cosine similarity.")
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),     # Use unigrams and bigrams
            stop_words="english",   # Remove English stopwords
            lowercase=True
        )
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = float(similarity[0][0])
        return round(score, 4)
    except Exception as e:
        logger.warning(f"[TF-IDF] Similarity computation failed: {e}")
        return 0.0


def analyze_skill_gap(
    resume_text: str,
    job_role: Optional[str] = None,
    job_description: Optional[str] = None
) -> dict:
    """
    Core analysis function that:
    1. Extracts resume skills
    2. Gets required skills (from role or JD)
    3. Computes matched/missing skills
    4. Calculates match percentage
    5. Computes TF-IDF similarity score

    Args:
        resume_text: Raw text extracted from PDF
        job_role: Selected job role name (optional)
        job_description: Pasted job description (optional)
    
    Returns:
        Dict with matched_skills, missing_skills, match_percentage, tfidf_similarity
    """
    if not job_role and not job_description:
        raise ValueError("Provide either a job role or a job description.")

    # Extract resume skills
    resume_skills = extract_resume_skills(resume_text)

    # Get required skills
    if job_role:
        required_skills = get_job_role_skills(job_role)
        job_text_for_similarity = " ".join(required_skills)
    else:
        required_skills = extract_skills_from_job_description(job_description)
        job_text_for_similarity = job_description

    if not required_skills:
        raise ValueError(
            "Could not determine required skills. "
            "If using a job description, ensure it contains recognizable skills."
        )

    # Convert to lowercase sets for comparison
    resume_lower = {s.lower() for s in resume_skills}
    required_lower = {s.lower() for s in required_skills}

    matched_lower = resume_lower & required_lower
    missing_lower = required_lower - resume_lower

    # Map back to original casing from required_skills
    required_map = {s.lower(): s for s in required_skills}
    matched_skills = sorted([required_map.get(s, s) for s in matched_lower])
    missing_skills = sorted([required_map.get(s, s) for s in missing_lower])

    # Calculate match percentage
    total = len(required_skills)
    match_pct = round((len(matched_skills) / total) * 100, 1) if total > 0 else 0.0

    # TF-IDF cosine similarity
    tfidf_score = compute_tfidf_similarity(resume_text, job_text_for_similarity)

    logger.info(
        f"[Gap Analysis] Matched: {len(matched_skills)}, Missing: {len(missing_skills)}, "
        f"Score: {match_pct}%, TF-IDF: {tfidf_score}"
    )

    return {
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_pct,
        "tfidf_similarity": tfidf_score,
        "total_required": total,
        "total_matched": len(matched_skills),
        "total_missing": len(missing_skills),
    }


# ============================================================
# CAREER PATH SUGGESTION
# ============================================================

def suggest_career_paths(resume_skills: list[str], current_role: str | None = None, top_n: int = 3) -> list[dict]:
    """
    Suggest alternative career paths based on resume skills.

    Compares resume skills against ALL job roles and returns
    the top N best-fit roles (excluding the current one).

    Args:
        resume_skills: Skills found in the resume
        current_role: Role already being analyzed (to exclude)
        top_n: Number of suggestions to return

    Returns:
        List of dicts with role, match_pct, matched_skills, missing_skills
    """
    skills_db = load_skills_db()
    job_roles = skills_db.get("job_roles", {})

    resume_set = {s.lower() for s in resume_skills}
    results = []

    for role, required in job_roles.items():
        # Skip the role already being analyzed
        if current_role and role.lower() == current_role.lower():
            continue

        required_lower = [s.lower() for s in required]
        required_set = set(required_lower)

        matched = sorted(resume_set & required_set)
        missing = sorted(required_set - resume_set)

        total = len(required_set)
        pct = round((len(matched) / total) * 100, 1) if total > 0 else 0

        results.append({
            "role": role,
            "match_percentage": pct,
            "total_required": total,
            "matched_count": len(matched),
            "missing_count": len(missing),
            "matched_skills": matched,
            "missing_skills": missing,
        })

    # Sort by match percentage descending
    results.sort(key=lambda x: x["match_percentage"], reverse=True)

    return results[:top_n]


# ============================================================
# ATS COMPATIBILITY ANALYSIS
# ============================================================

def analyze_ats_compatibility(resume_text: str, gap_result: dict) -> dict:
    """
    Analyze the resume for ATS (Applicant Tracking System) compatibility.

    Checks:
      1. Contact Info      — email address and phone number present
      2. Resume Length     — word count within ideal range (150–800 words)
      3. Section Structure — standard headings detected
      4. Keyword Density   — uses the existing match_percentage
      5. Skills Presence   — at least a few skills found

    Returns:
        dict with keys:
            - score (int 0-100): overall ATS compatibility score
            - label (str): "Excellent" / "Good" / "Average" / "Poor"
            - suggestions (list[str]): actionable improvement tips
            - breakdown (dict): per-category scores for display
    """
    suggestions = []
    breakdown = {}

    text_lower = resume_text.lower()

    # ----------------------------------------------------------
    # 1. CONTACT INFORMATION  (max 20 pts)
    # ----------------------------------------------------------
    contact_score = 0

    # Check for email address
    has_email = bool(re.search(
        r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', resume_text
    ))
    if has_email:
        contact_score += 10
    else:
        suggestions.append("Add your email address — ATS systems expect contact information at the top of the resume.")

    # Check for phone number (various formats: 10-digit, +91, (xxx), etc.)
    has_phone = bool(re.search(
        r'(\+?\d[\d\s\-().]{7,14}\d)', resume_text
    ))
    if has_phone:
        contact_score += 6
    else:
        suggestions.append("Add a phone number to your resume for recruiter contact and ATS parsing.")

    # Check for LinkedIn or GitHub URL
    has_profile = bool(re.search(
        r'(linkedin\.com|github\.com|portfolio|behance\.net)', text_lower
    ))
    if has_profile:
        contact_score += 4
    else:
        suggestions.append("Include a LinkedIn profile or GitHub URL to boost your ATS profile score.")

    breakdown["Contact Info"] = contact_score

    # ----------------------------------------------------------
    # 2. RESUME LENGTH (max 20 pts)
    # ----------------------------------------------------------
    word_count = len(resume_text.split())
    length_score = 0

    if word_count < 100:
        suggestions.append(
            f"Your resume is very short ({word_count} words). ATS scanners prefer resumes with 300–700 words. "
            "Add more detail about your experience and projects."
        )
        length_score = 5
    elif word_count < 200:
        suggestions.append(
            f"Your resume is brief ({word_count} words). Aim for 300–700 words by elaborating on your roles "
            "and adding specific achievements with metrics."
        )
        length_score = 10
    elif word_count <= 700:
        length_score = 20  # ideal range
    elif word_count <= 1000:
        length_score = 16
        suggestions.append(
            f"Your resume is slightly long ({word_count} words). Try to trim it to under 700 words "
            "for better ATS readability."
        )
    else:
        length_score = 10
        suggestions.append(
            f"Your resume is too long ({word_count} words). ATS systems may truncate long resumes. "
            "Condense to 1–2 pages (300–700 words)."
        )

    breakdown["Resume Length"] = length_score

    # ----------------------------------------------------------
    # 3. SECTION STRUCTURE (max 25 pts)
    # ----------------------------------------------------------
    structure_score = 0
    section_map = {
        "experience":      ["experience", "work experience", "employment", "work history", "professional experience"],
        "education":       ["education", "qualification", "academic background", "degree", "university", "college"],
        "skills":          ["skills", "technical skills", "core competencies", "expertise", "proficiencies"],
        "summary":         ["summary", "objective", "profile", "about me", "professional summary", "career objective"],
        "projects":        ["projects", "personal projects", "key projects", "academic projects", "portfolio"],
        "certifications":  ["certifications", "certificates", "courses completed", "achievements"],
    }

    found_sections = []
    for section_name, keywords in section_map.items():
        if any(kw in text_lower for kw in keywords):
            found_sections.append(section_name)

    # Award proportional score
    section_pts = {
        "experience":     8,
        "education":      6,
        "skills":         5,
        "summary":        3,
        "projects":       2,
        "certifications": 1,
    }
    for sec in found_sections:
        structure_score += section_pts.get(sec, 0)

    structure_score = min(structure_score, 25)  # cap at 25

    if "experience" not in found_sections:
        suggestions.append("Add a clearly labelled 'Experience' or 'Work Experience' section — it's the most important for ATS.")
    if "education" not in found_sections:
        suggestions.append("Include an 'Education' section with your degree, institution, and year of graduation.")
    if "skills" not in found_sections:
        suggestions.append("Add a dedicated 'Skills' section listing your technical and soft skills explicitly.")
    if "summary" not in found_sections:
        suggestions.append("Add a brief 'Professional Summary' (2–3 sentences) at the top of your resume for a stronger first impression.")
    if "projects" not in found_sections:
        suggestions.append("Include a 'Projects' section — real project experience shows practical skill, especially for tech roles.")
    if "certifications" not in found_sections:
        suggestions.append("Consider adding 'Certifications' or 'Courses' to validate your skills with credentials.")

    breakdown["Structure"] = structure_score

    # ----------------------------------------------------------
    # 4. KEYWORD / SKILL MATCH  (max 25 pts)
    # ----------------------------------------------------------
    match_pct = gap_result.get("match_percentage", 0)
    keyword_score = round((match_pct / 100) * 25)

    if match_pct < 30:
        missing_top = gap_result.get("missing_skills", [])[:5]
        if missing_top:
            suggestions.append(
                f"Your resume matches only {match_pct:.0f}% of required skills. "
                f"Consider adding: {', '.join(missing_top)}."
            )
    elif match_pct < 60:
        suggestions.append(
            f"Skill match is {match_pct:.0f}%. Tailor your resume to include more keywords "
            "from the job description to beat ATS filters."
        )

    breakdown["Keyword Match"] = keyword_score

    # ----------------------------------------------------------
    # 5. SKILLS DETECTED  (max 10 pts)
    # ----------------------------------------------------------
    skill_count = len(gap_result.get("resume_skills", []))
    if skill_count == 0:
        skills_score = 0
        suggestions.append(
            "No recognizable technical skills were detected in your resume. "
            "Use standard skill names (e.g., 'Python', 'SQL', 'React') so ATS can parse them."
        )
    elif skill_count < 5:
        skills_score = 4
        suggestions.append(
            f"Only {skill_count} skill(s) detected. List more skills explicitly in your resume."
        )
    elif skill_count < 10:
        skills_score = 7
    else:
        skills_score = 10

    breakdown["Skills Detected"] = skills_score

    # ----------------------------------------------------------
    # FINAL SCORE
    # ----------------------------------------------------------
    total_score = contact_score + length_score + structure_score + keyword_score + skills_score
    total_score = max(0, min(100, total_score))  # clamp to [0, 100]

    # Determine label
    if total_score >= 80:
        label = "Excellent"
    elif total_score >= 60:
        label = "Good"
    elif total_score >= 40:
        label = "Average"
    else:
        label = "Poor"

    # Generic ATS tips if no major issues are found
    if not suggestions:
        suggestions.append("Your resume looks strong! Keep using standard fonts and avoid tables/graphics for best ATS parsing.")

    # Always add a formatting reminder
    suggestions.append(
        "Use a clean, single-column layout without tables or graphics — ATS systems can't parse complex formatting."
    )

    logger.info(f"[ATS] Score: {total_score}/100 ({label}) | Suggestions: {len(suggestions)}")

    return {
        "score": total_score,
        "label": label,
        "suggestions": suggestions,
        "breakdown": breakdown,
        "word_count": word_count,
    }

