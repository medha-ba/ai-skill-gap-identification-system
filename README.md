# 🧠 AI-Based Skill Gap Identification System

An intelligent web application that analyzes resumes against job roles using **NLP and Machine Learning** to identify skill gaps, score ATS compatibility, suggest career paths, generate personalized interview questions, and recommend courses — all in a sleek, modern dark-themed UI.

---

## ✨ Features

### 📄 Resume Analysis
- Upload a PDF resume and select a target job role (or paste a custom job description)
- NLP-powered skill extraction using **spaCy** tokenization and **TF-IDF cosine similarity**
- Identifies **matched skills** and **missing skills** with percentage-based scoring

### 🕸️ Skill Radar Chart
- Interactive spider/radar chart comparing your skills vs. job requirements
- Green dots for matched skills, red dots for gaps — instant visual feedback

### 📋 ATS Compatibility Score
- Evaluates resume quality across 5 categories: Contact Info, Resume Length, Skill Keyword Density, Section Headers, and Action Verbs
- Provides a 0–100 ATS score with actionable improvement suggestions

### 🛤️ AI Career Path Suggestions
- Compares your resume skills against **all available job roles**
- Ranks the top 3 best-fit alternative career paths with match percentages
- Shows matched/missing skills for each suggested role

### 💬 Personalized Interview Preparation
- Generates **12 tailored interview questions** based on your analysis:
  - 5 Technical Questions (from your strong skills)
  - 3 Improvement Questions (targeting your weak areas)
  - 2 Scenario-Based Questions (role-specific real-world problems)
  - 2 Behavioral Questions (leadership & communication)
- Difficulty scales with experience level (Entry / Mid / Senior)
- 200+ curated questions across 30+ skills

### 📚 Course Recommendations
- Personalized course suggestions for each missing skill
- Sourced from platforms like Coursera, Udemy, and edX

### 📥 PDF Report Export
- Download a professionally formatted analysis report
- Includes: skill match stats, ATS score, career paths, and course recommendations

### 🔐 User Authentication
- Secure login and signup with session-based authentication
- Password hashing and HTTP-only cookies for security

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI, Uvicorn |
| **NLP Engine** | spaCy (`en_core_web_sm`), TF-IDF (scikit-learn) |
| **Database** | SQLite |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5 |
| **Charts** | Chart.js (Bar + Radar) |
| **Auth** | Session cookies, SHA-256 hashing |

---

## 📁 Project Structure

```
ai-skill-gap-identification-system/
├── main.py                 # FastAPI app — routes, auth, API endpoints
├── database.py             # SQLite DB — users, sessions, courses
├── skill_extractor.py      # NLP skill extraction, gap analysis, ATS scoring, career paths
├── resume_parser.py        # PDF text extraction using pdfplumber
├── recommender.py          # Course recommendation engine
├── interview_prep.py       # Interview question generator (200+ questions)
├── skills.json             # Skills database — 10 job roles, 80+ skills
├── requirements.txt        # Python dependencies
├── templates/
│   ├── index.html          # Main dashboard (6-tab interface)
│   └── login.html          # Login / Signup page
└── static/
    └── style.css           # Dark glassmorphism theme
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/medha-ba/ai-skill-gap-identification-system.git
cd ai-skill-gap-identification-system

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Run the application
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open your browser at **http://localhost:8000** → Sign up → Upload a resume → Explore all 6 tabs!

---

## 📸 Screenshots

### Login Page
Dark glassmorphism login/signup with tabbed interface.

### Dashboard — Overview Tab
Skill match ring, bar chart, radar chart, and ATS preview.

### Career Paths Tab
AI-suggested alternative roles ranked by skill match percentage.

### Interview Prep Tab
Personalized questions organized by category with experience level selector.

---

## 🔑 Supported Job Roles

- Data Analyst
- Data Scientist
- ML Engineer
- Web Developer
- Frontend Developer
- Backend Developer
- Full Stack Developer
- Data Engineer
- DevOps Engineer
- Cybersecurity Analyst

---

## 📝 How It Works

1. **Upload** your resume (PDF) and select a target job role
2. **spaCy NLP** extracts skills from your resume text
3. **TF-IDF cosine similarity** measures overall text alignment
4. **Skill gap analysis** identifies matched vs. missing skills
5. **ATS engine** scores resume formatting and keyword density
6. **Career path AI** finds your best-fit alternative roles
7. **Interview generator** creates role-specific practice questions
8. **Recommender** suggests courses for each missing skill

---

## 📄 License

This project is for educational purposes.

---

<p align="center">
  Built with ❤️ using FastAPI, spaCy, and Chart.js
</p>
