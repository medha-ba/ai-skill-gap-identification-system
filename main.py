"""
main.py - FastAPI application for the AI-Based Skill Gap Identification System.
Provides REST API endpoints, authentication, and serves the frontend HTML templates.
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Request, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Internal modules
from database import (
    init_db, create_user, verify_user,
    create_session, get_user_by_session, delete_session,
)
from resume_parser import extract_text_from_pdf
from skill_extractor import analyze_skill_gap, get_available_job_roles, analyze_ats_compatibility, suggest_career_paths
from recommender import get_recommendations
from interview_prep import generate_interview_questions

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: Initialize DB on startup."""
    logger.info("[Startup] Initializing database...")
    init_db()
    logger.info("[Startup] Application ready.")
    yield
    logger.info("[Shutdown] Application shutting down.")


# Initialize FastAPI app
app = FastAPI(
    title="AI Skill Gap Identification System",
    description="Upload a resume and compare it against a job role or description to identify skill gaps.",
    version="2.0.0",
    lifespan=lifespan,
)

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates for HTML rendering
templates = Jinja2Templates(directory="templates")


# ============================================================
# AUTH HELPERS
# ============================================================

def _get_current_user(session_token: str | None) -> dict | None:
    """Get the current logged-in user from the session cookie."""
    if not session_token:
        return None
    return get_user_by_session(session_token)


# ============================================================
# PAGE ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session: str = Cookie(default=None)):
    """
    Main dashboard page — requires login.
    If not logged in, redirect to /login.
    """
    user = _get_current_user(session)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    job_roles = get_available_job_roles()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "job_roles": job_roles, "user": user},
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, session: str = Cookie(default=None)):
    """
    Login / Sign-up page.
    If already logged in, redirect to /.
    """
    user = _get_current_user(session)
    if user:
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse("login.html", {"request": request})


# ============================================================
# AUTH API ENDPOINTS
# ============================================================

class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str


@app.post("/api/auth/login")
async def api_login(body: LoginRequest):
    """Authenticate user and return session cookie."""
    user = verify_user(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_session(user["id"])
    response = JSONResponse(content={"status": "ok", "user": user["full_name"]})
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )
    logger.info(f"[Auth] Login: {user['email']}")
    return response


@app.post("/api/auth/signup")
async def api_signup(body: SignupRequest):
    """Register a new user and return session cookie."""
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    if not body.full_name.strip():
        raise HTTPException(status_code=400, detail="Full name is required.")
    if not body.email.strip():
        raise HTTPException(status_code=400, detail="Email is required.")

    try:
        user = create_user(body.full_name, body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    token = create_session(user["id"])
    response = JSONResponse(content={"status": "ok", "user": user["full_name"]})
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    logger.info(f"[Auth] Signup: {user['email']}")
    return response


@app.get("/api/auth/logout")
async def api_logout(session: str = Cookie(default=None)):
    """Log out — clear session cookie."""
    if session:
        delete_session(session)
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session")
    return response


@app.get("/api/auth/me")
async def api_me(session: str = Cookie(default=None)):
    """Get current user info."""
    user = _get_current_user(session)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return {"user": user}


# ============================================================
# JOB ROLES API
# ============================================================

@app.get("/api/job-roles")
async def get_job_roles():
    """API endpoint to retrieve the list of available job roles."""
    roles = get_available_job_roles()
    return {"job_roles": roles}


# ============================================================
# ANALYSIS API
# ============================================================

@app.post("/api/analyze")
async def analyze(
    resume: UploadFile = File(..., description="Upload a PDF resume"),
    job_role: Optional[str] = Form(None, description="Select a predefined job role"),
    job_description: Optional[str] = Form(None, description="Or paste a job description"),
    session: str = Cookie(default=None),
):
    """
    Main analysis endpoint.
    Accepts a PDF resume and either a job role or job description.
    Returns skill gap analysis results with course recommendations.
    """
    # Check auth
    user = _get_current_user(session)
    if not user:
        raise HTTPException(status_code=401, detail="Please log in to use the analyzer.")

    # ----- Validate inputs -----
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported. Please upload a .pdf file."
        )

    if not job_role and (not job_description or not job_description.strip()):
        raise HTTPException(
            status_code=400,
            detail="Please select a job role OR paste a job description."
        )

    # ----- Read PDF bytes -----
    try:
        file_bytes = await resume.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # ----- Extract text from PDF -----
    try:
        resume_text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # ----- Perform skill gap analysis -----
    try:
        active_job_role = job_role if job_role and job_role.strip() else None
        active_jd = job_description.strip() if job_description and job_description.strip() else None

        if active_job_role:
            active_jd = None

        gap_result = analyze_skill_gap(
            resume_text=resume_text,
            job_role=active_job_role,
            job_description=active_jd
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during analysis.")

    # ----- Get course recommendations for missing skills -----
    try:
        recommendations = get_recommendations(gap_result["missing_skills"])
    except Exception as e:
        logger.warning(f"[API] Recommendation error (non-fatal): {e}")
        recommendations = []

    # ----- Compute ATS compatibility score -----
    try:
        ats_result = analyze_ats_compatibility(resume_text, gap_result)
    except Exception as e:
        logger.warning(f"[API] ATS analysis error (non-fatal): {e}")
        ats_result = {"score": 0, "label": "Unknown", "suggestions": [], "breakdown": {}, "word_count": 0}

    # ----- Build response -----
    response = {
        "status": "success",
        "filename": resume.filename,
        "job_role": active_job_role or "Custom Job Description",
        "match_percentage": gap_result["match_percentage"],
        "tfidf_similarity": gap_result["tfidf_similarity"],
        "total_required": gap_result["total_required"],
        "total_matched": gap_result["total_matched"],
        "total_missing": gap_result["total_missing"],
        "resume_skills": gap_result["resume_skills"],
        "required_skills": gap_result["required_skills"],
        "matched_skills": gap_result["matched_skills"],
        "missing_skills": gap_result["missing_skills"],
        "recommendations": recommendations,
        "ats": {
            "score":       ats_result["score"],
            "label":       ats_result["label"],
            "suggestions": ats_result["suggestions"],
            "breakdown":   ats_result["breakdown"],
            "word_count":  ats_result["word_count"],
        },
        # Career path suggestions
        "career_paths": suggest_career_paths(
            resume_skills=gap_result["resume_skills"],
            current_role=active_job_role,
            top_n=3,
        ),
    }

    logger.info(
        f"[API] Analysis complete for '{resume.filename}': "
        f"{gap_result['match_percentage']}% match | "
        f"{gap_result['total_matched']} matched | "
        f"{gap_result['total_missing']} missing"
    )

    return JSONResponse(content=response)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "AI Skill Gap Identification System is running."}


# ============================================================
# INTERVIEW PREP API
# ============================================================

class InterviewPrepRequest(BaseModel):
    job_role: str
    matched_skills: list[str]
    missing_skills: list[str]
    match_percentage: float
    experience_level: str = "mid"


@app.post("/api/interview-prep")
async def interview_prep(body: InterviewPrepRequest, session: str = Cookie(default=None)):
    """Generate personalized interview preparation questions."""
    user = _get_current_user(session)
    if not user:
        raise HTTPException(status_code=401, detail="Please log in.")

    try:
        result = generate_interview_questions(
            job_role=body.job_role,
            matched_skills=body.matched_skills,
            missing_skills=body.missing_skills,
            match_percentage=body.match_percentage,
            experience_level=body.experience_level,
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"[API] Interview prep error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate interview questions.")

