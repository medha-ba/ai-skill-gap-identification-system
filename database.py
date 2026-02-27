"""
database.py - SQLite database setup and course recommendation mappings.
Initializes the database, creates tables, and seeds course data.
"""

import sqlite3
import os
import hashlib
import secrets

# Path to SQLite database file
DB_PATH = "skill_gap.db"

# Course recommendations mapped to skills
COURSE_DATA = [
    # Python & Programming
    ("python", "Python for Beginners", "https://www.coursera.org/learn/python", "Coursera"),
    ("python", "Python Bootcamp", "https://www.udemy.com/course/complete-python-bootcamp/", "Udemy"),
    ("java", "Java Programming Masterclass", "https://www.udemy.com/course/java-the-complete-java-developer-course/", "Udemy"),
    ("javascript", "JavaScript: The Complete Guide", "https://www.udemy.com/course/javascript-the-complete-guide-2020-beginner-advanced/", "Udemy"),
    ("typescript", "Understanding TypeScript", "https://www.udemy.com/course/understanding-typescript/", "Udemy"),
    ("c++", "C++ Programming Course", "https://www.coursera.org/specializations/coding-for-everyone", "Coursera"),
    ("go", "Go: The Complete Developer's Guide", "https://www.udemy.com/course/go-the-complete-developers-guide/", "Udemy"),
    ("rust", "The Rust Programming Language", "https://doc.rust-lang.org/book/", "Official Docs"),

    # Web Development
    ("html", "HTML & CSS Full Course", "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "freeCodeCamp"),
    ("css", "CSS - The Complete Guide", "https://www.udemy.com/course/css-the-complete-guide-incl-flexbox-grid-sass/", "Udemy"),
    ("react", "React - The Complete Guide", "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "Udemy"),
    ("angular", "Angular - The Complete Guide", "https://www.udemy.com/course/the-complete-guide-to-angular-2/", "Udemy"),
    ("vue", "Vue - The Complete Guide", "https://www.udemy.com/course/vuejs-2-the-complete-guide/", "Udemy"),
    ("nodejs", "Node.js Developer Course", "https://www.udemy.com/course/the-complete-nodejs-developer-course-2/", "Udemy"),
    ("nextjs", "Next.js & React - The Complete Guide", "https://www.udemy.com/course/nextjs-react-the-complete-guide/", "Udemy"),
    ("django", "Django for Beginners", "https://djangoforbeginners.com/", "Django for Beginners"),
    ("flask", "Flask Web Development", "https://www.udemy.com/course/python-and-flask-bootcamp-create-websites-using-flask/", "Udemy"),
    ("fastapi", "FastAPI - The Complete Course", "https://www.udemy.com/course/fastapi-the-complete-course/", "Udemy"),
    ("rest api", "REST API Design", "https://www.udemy.com/course/rest-api-flask-and-python/", "Udemy"),
    ("graphql", "GraphQL with React", "https://www.udemy.com/course/graphql-with-react-course/", "Udemy"),

    # Databases
    ("sql", "SQL for Data Science", "https://www.coursera.org/learn/sql-for-data-science", "Coursera"),
    ("mysql", "MySQL for Beginners", "https://www.udemy.com/course/mysql-for-beginners-real-database-experience-real-fast/", "Udemy"),
    ("postgresql", "PostgreSQL for Everybody", "https://www.coursera.org/learn/database-design-postgresql", "Coursera"),
    ("mongodb", "MongoDB - The Complete Developer's Guide", "https://www.udemy.com/course/mongodb-the-complete-developers-guide/", "Udemy"),
    ("redis", "Redis Crash Course", "https://www.youtube.com/watch?v=jgpVdJB2sKQ", "YouTube"),

    # Data Science & ML
    ("machine learning", "Machine Learning", "https://www.coursera.org/learn/machine-learning", "Coursera (Andrew Ng)"),
    ("deep learning", "Deep Learning Specialization", "https://www.coursera.org/specializations/deep-learning", "Coursera"),
    ("tensorflow", "TensorFlow Developer Certificate", "https://www.coursera.org/professional-certificates/tensorflow-in-practice", "Coursera"),
    ("pytorch", "PyTorch for Deep Learning", "https://www.udemy.com/course/pytorch-for-deep-learning-and-computer-vision/", "Udemy"),
    ("scikit-learn", "Scikit-Learn Tutorial", "https://scikit-learn.org/stable/tutorial/index.html", "Official Docs"),
    ("pandas", "Pandas for Data Analysis", "https://www.udemy.com/course/data-analysis-with-pandas/", "Udemy"),
    ("numpy", "NumPy for Beginners", "https://numpy.org/learn/", "Official Docs"),
    ("nlp", "Natural Language Processing Specialization", "https://www.coursera.org/specializations/natural-language-processing", "Coursera"),
    ("computer vision", "Computer Vision Basics", "https://www.coursera.org/learn/computer-vision-basics", "Coursera"),
    ("data analysis", "Google Data Analytics Certificate", "https://www.coursera.org/professional-certificates/google-data-analytics", "Coursera"),
    ("data science", "IBM Data Science Professional Certificate", "https://www.coursera.org/professional-certificates/ibm-data-science", "Coursera"),
    ("statistics", "Statistics with Python", "https://www.coursera.org/specializations/statistics-with-python", "Coursera"),
    ("r", "R Programming", "https://www.coursera.org/learn/r-programming", "Coursera"),
    ("feature engineering", "Feature Engineering for ML", "https://www.kaggle.com/learn/feature-engineering", "Kaggle"),
    ("model deployment", "Deploying ML Models", "https://www.udemy.com/course/deployment-of-machine-learning-models/", "Udemy"),
    ("mlops", "Machine Learning Engineering for Production (MLOps)", "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops", "Coursera"),
    ("xgboost", "XGBoost for Data Science", "https://www.kaggle.com/learn/intermediate-machine-learning", "Kaggle"),
    ("generative ai", "Generative AI with LLMs", "https://www.coursera.org/learn/generative-ai-with-llms", "Coursera"),
    ("llm", "LLM Engineering: Master AI & LLMs", "https://www.udemy.com/course/llm-engineering-master-ai-and-large-language-models/", "Udemy"),

    # Data Visualization
    ("data visualization", "Data Visualization with Python", "https://www.coursera.org/learn/python-for-data-visualization", "Coursera"),
    ("tableau", "Tableau 2024 A-Z", "https://www.udemy.com/course/tableau10/", "Udemy"),
    ("power bi", "Power BI - Desktop", "https://www.udemy.com/course/microsoft-power-bi-up-running-with-power-bi-desktop/", "Udemy"),
    ("matplotlib", "Matplotlib Tutorial", "https://matplotlib.org/stable/tutorials/index.html", "Official Docs"),

    # Cloud & DevOps
    ("aws", "AWS Certified Solutions Architect", "https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/", "Udemy"),
    ("azure", "Microsoft Azure Fundamentals", "https://learn.microsoft.com/en-us/training/paths/azure-fundamentals/", "Microsoft Learn"),
    ("gcp", "Google Cloud Associate Engineer", "https://cloud.google.com/learn/training", "Google Cloud"),
    ("docker", "Docker for Beginners", "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/", "Udemy"),
    ("kubernetes", "Kubernetes for Developers", "https://www.udemy.com/course/certified-kubernetes-application-developer/", "Udemy"),
    ("ci/cd", "CI/CD with Jenkins", "https://www.udemy.com/course/jenkins-from-zero-to-hero/", "Udemy"),
    ("terraform", "Terraform for Beginners", "https://www.udemy.com/course/terraform-beginner-to-advanced/", "Udemy"),
    ("linux", "Linux Command Line Basics", "https://www.coursera.org/learn/unix", "Coursera"),
    ("git", "Git & GitHub Crash Course", "https://www.udemy.com/course/git-and-github-bootcamp/", "Udemy"),
    ("devops", "DevOps Bootcamp", "https://www.udemy.com/course/the-modern-devops-practices2/", "Udemy"),

    # Big Data
    ("spark", "Apache Spark with Python", "https://www.udemy.com/course/spark-and-python-for-big-data-with-pyspark/", "Udemy"),
    ("kafka", "Apache Kafka Series", "https://www.udemy.com/course/apache-kafka/", "Udemy"),
    ("hadoop", "Hadoop Platform and Application Framework", "https://www.coursera.org/learn/hadoop", "Coursera"),
    ("airflow", "Apache Airflow Fundamentals", "https://www.udemy.com/course/the-complete-hands-on-course-to-master-apache-airflow/", "Udemy"),
    ("etl", "ETL with Python", "https://www.udemy.com/course/python-etl-pipeline-with-pandas/", "Udemy"),

    # Cybersecurity
    ("cybersecurity", "Google Cybersecurity Certificate", "https://www.coursera.org/professional-certificates/google-cybersecurity", "Coursera"),
    ("network security", "Network Security Fundamentals", "https://www.coursera.org/learn/network-security-database-vulnerabilities", "Coursera"),
    ("ethical hacking", "Ethical Hacking Bootcamp", "https://www.udemy.com/course/learn-ethical-hacking-from-scratch/", "Udemy"),
    ("penetration testing", "Penetration Testing & Ethical Hacking", "https://www.udemy.com/course/penetration-testing/", "Udemy"),

    # Agile / Management
    ("agile", "Agile Development Specialization", "https://www.coursera.org/specializations/agile-development", "Coursera"),
    ("scrum", "Scrum Master Certification", "https://www.udemy.com/course/agile-scrum-for-beginners/", "Udemy"),
    ("project management", "Google Project Management Certificate", "https://www.coursera.org/professional-certificates/google-project-management", "Coursera"),

    # A/B Testing & Analytics
    ("a/b testing", "A/B Testing by Google", "https://www.udemy.com/course/ab-testing/", "Udemy"),
    ("hypothesis testing", "Inferential Statistics", "https://www.coursera.org/learn/inferential-statistics-intro", "Coursera"),
    ("excel", "Excel for Data Analysis", "https://www.coursera.org/learn/excel-data-analysis", "Coursera"),

    # Blockchain
    ("blockchain", "Blockchain Basics", "https://www.coursera.org/learn/blockchain-basics", "Coursera"),
    ("solidity", "Ethereum and Solidity", "https://www.udemy.com/course/ethereum-and-solidity-the-complete-developers-guide/", "Udemy"),
]


def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db():
    """
    Initialize the database:
    - Create courses table if not exists
    - Seed with default course data
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Create courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill TEXT NOT NULL,
            course_name TEXT NOT NULL,
            course_url TEXT NOT NULL,
            platform TEXT NOT NULL
        )
    """)

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Seed data only if table is empty
    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany(
            "INSERT INTO courses (skill, course_name, course_url, platform) VALUES (?, ?, ?, ?)",
            COURSE_DATA
        )
        print(f"[DB] Seeded {len(COURSE_DATA)} course records.")

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")


def get_courses_for_skill(skill: str) -> list[dict]:
    """
    Fetch recommended courses for a given skill.
    Returns a list of course dicts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT course_name, course_url, platform FROM courses WHERE LOWER(skill) = LOWER(?)",
        (skill,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"course_name": row["course_name"], "course_url": row["course_url"], "platform": row["platform"]} for row in rows]


def get_all_skills_with_courses() -> list[str]:
    """Return all skill names that have course recommendations."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT LOWER(skill) FROM courses")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


# ============================================================
# USER AUTHENTICATION
# ============================================================

def _hash_password(password: str) -> str:
    """Hash a password with SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(full_name: str, email: str, password: str) -> dict:
    """
    Register a new user. Returns user dict or raises ValueError.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
            (full_name.strip(), email.strip().lower(), _hash_password(password)),
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {"id": user_id, "full_name": full_name.strip(), "email": email.strip().lower()}
    except sqlite3.IntegrityError:
        raise ValueError("An account with this email already exists.")
    finally:
        conn.close()


def verify_user(email: str, password: str) -> dict | None:
    """
    Verify login credentials. Returns user dict or None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, full_name, email FROM users WHERE email = ? AND password_hash = ?",
        (email.strip().lower(), _hash_password(password)),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "full_name": row["full_name"], "email": row["email"]}
    return None


def create_session(user_id: int) -> str:
    """
    Create a new session token for the user.
    """
    token = secrets.token_hex(32)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (user_id, token) VALUES (?, ?)",
        (user_id, token),
    )
    conn.commit()
    conn.close()
    return token


def get_user_by_session(token: str) -> dict | None:
    """
    Look up a user by their session token.
    """
    if not token:
        return None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT u.id, u.full_name, u.email FROM sessions s "
        "JOIN users u ON s.user_id = u.id WHERE s.token = ?",
        (token,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "full_name": row["full_name"], "email": row["email"]}
    return None


def delete_session(token: str):
    """Delete a session (logout)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()

