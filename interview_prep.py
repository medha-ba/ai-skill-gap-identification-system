"""
interview_prep.py — Personalized Interview Question Generator
Generates technical, improvement, scenario, and behavioral questions
based on the candidate's skill gap analysis results.
"""

import random


# ============================================================
# QUESTION BANKS — Organized by skill / category
# ============================================================

TECHNICAL_QUESTIONS = {
    # Python & Programming
    "python": [
        "Explain the difference between a list and a tuple in Python. When would you choose one over the other?",
        "How do Python decorators work? Can you write a simple example of a caching decorator?",
        "Explain the Global Interpreter Lock (GIL) in Python. How does it affect multithreading?",
        "What is the difference between `deepcopy` and `copy` in Python? When is each appropriate?",
        "How does memory management work in Python? Explain reference counting and garbage collection.",
        "What are Python generators and how do they differ from regular functions? Give a practical use case.",
        "Explain the MRO (Method Resolution Order) in Python's multiple inheritance.",
        "How would you optimize a Python script that processes a 10GB CSV file?",
    ],
    "java": [
        "Explain the difference between abstract classes and interfaces in Java.",
        "How does garbage collection work in the JVM? Describe different GC algorithms.",
        "What is the difference between `HashMap` and `ConcurrentHashMap`?",
        "Explain the Java Memory Model and the `volatile` keyword.",
        "How do you handle checked vs unchecked exceptions in Java?",
    ],
    "javascript": [
        "Explain the event loop in JavaScript. How does it handle asynchronous operations?",
        "What is the difference between `var`, `let`, and `const`? Explain hoisting.",
        "How do closures work in JavaScript? Provide a practical example.",
        "Explain prototypal inheritance in JavaScript versus classical inheritance.",
        "What are Promises and how do they differ from async/await?",
        "Explain the difference between `==` and `===` in JavaScript.",
    ],
    "typescript": [
        "What are generics in TypeScript and why are they useful?",
        "Explain the difference between `interface` and `type` in TypeScript.",
        "How does TypeScript's structural typing system work?",
        "What are utility types in TypeScript? Give examples of `Partial`, `Pick`, and `Omit`.",
    ],

    # Web Development
    "react": [
        "Explain the virtual DOM and how React's reconciliation algorithm works.",
        "What are React hooks? How do `useEffect` and `useCallback` differ?",
        "How would you optimize a React app that re-renders too frequently?",
        "Explain the Context API vs Redux. When would you use each?",
        "What are the key differences between controlled and uncontrolled components?",
    ],
    "angular": [
        "Explain Angular's dependency injection system and how providers work.",
        "What is the difference between `ngOnInit` and the constructor in Angular?",
        "How does change detection work in Angular? What is `OnPush` strategy?",
        "Explain the purpose of Angular modules and lazy loading.",
    ],
    "vue": [
        "Explain Vue's reactivity system. How does it track dependencies?",
        "What is the Composition API and how does it differ from the Options API?",
        "How does Vue's virtual DOM diffing algorithm work?",
    ],
    "nodejs": [
        "Explain the Node.js event loop and its different phases.",
        "How do you handle memory leaks in a Node.js application?",
        "What is the difference between `process.nextTick()` and `setImmediate()`?",
        "How would you design a streaming file upload in Node.js?",
    ],
    "html": [
        "What are semantic HTML elements and why do they matter for accessibility?",
        "Explain the difference between `<section>`, `<article>`, and `<div>`.",
        "How does the browser rendering pipeline work from HTML to pixels on screen?",
    ],
    "css": [
        "Explain the CSS Box Model. What is the difference between `content-box` and `border-box`?",
        "How does CSS Specificity work? Explain the cascade order.",
        "What is the difference between Flexbox and CSS Grid? When would you use each?",
        "How do CSS custom properties (variables) differ from Sass variables?",
    ],
    "rest api": [
        "Explain the differences between REST and GraphQL. When would you choose each?",
        "What are the key principles of RESTful API design?",
        "How do you implement pagination, filtering, and sorting in a REST API?",
        "Explain HTTP status codes: when would you use 201 vs 200, and 404 vs 400?",
    ],
    "graphql": [
        "What are GraphQL resolvers and how do they handle nested queries?",
        "How do you handle N+1 query problems in GraphQL?",
        "Explain the difference between queries, mutations, and subscriptions in GraphQL.",
    ],
    "django": [
        "Explain Django's ORM. How does it handle database migrations?",
        "What is Django middleware and how does the request/response cycle work?",
        "How would you optimize a slow Django query that joins multiple tables?",
    ],
    "flask": [
        "How does Flask's application context and request context work?",
        "Explain Blueprints in Flask and when you'd use them.",
        "How do you handle authentication in a Flask REST API?",
    ],
    "fastapi": [
        "How does FastAPI achieve its high performance compared to Flask/Django?",
        "Explain dependency injection in FastAPI and how it differs from Flask.",
        "How does FastAPI use Pydantic for request validation?",
    ],

    # Databases
    "sql": [
        "Explain the difference between INNER JOIN, LEFT JOIN, and CROSS JOIN with examples.",
        "What are database indexes? How do you decide which columns to index?",
        "Explain ACID properties in databases. Why are they important?",
        "What is the difference between a clustered and non-clustered index?",
        "How would you optimize a slow SQL query? Walk through your approach.",
        "Explain normalization vs denormalization. When would you denormalize?",
    ],
    "mongodb": [
        "When would you choose MongoDB over a relational database?",
        "Explain MongoDB's aggregation pipeline with a practical example.",
        "How does indexing work in MongoDB? What are compound indexes?",
    ],
    "postgresql": [
        "What are PostgreSQL's advantages over MySQL for complex queries?",
        "Explain JSONB data type in PostgreSQL and when you'd use it.",
        "How do you implement full-text search in PostgreSQL?",
    ],
    "redis": [
        "Explain Redis data structures and when to use each (strings, hashes, sets, sorted sets).",
        "How would you implement a caching strategy using Redis?",
        "What is Redis Pub/Sub and how does it compare to Kafka?",
    ],

    # Data Science & ML
    "machine learning": [
        "Explain the bias-variance tradeoff. How do you balance it in practice?",
        "What is the difference between bagging and boosting? Give algorithm examples.",
        "How do you handle class imbalance in a classification problem?",
        "Explain cross-validation and why simple train/test split is insufficient.",
        "What is regularization? Compare L1 (Lasso) and L2 (Ridge) regularization.",
        "How would you select features for a machine learning model?",
    ],
    "deep learning": [
        "Explain backpropagation and how gradients flow through a neural network.",
        "What is the vanishing gradient problem and how do LSTM/GRU solve it?",
        "Compare CNNs and Transformers for image classification tasks.",
        "Explain transfer learning and fine-tuning. When is each appropriate?",
        "What is batch normalization and why does it help training?",
    ],
    "nlp": [
        "Explain the Transformer architecture and the self-attention mechanism.",
        "What is the difference between BERT and GPT architectures?",
        "How do you handle out-of-vocabulary words in NLP models?",
        "Explain word embeddings (Word2Vec, GloVe) and their limitations.",
    ],
    "tensorflow": [
        "Explain the difference between eager execution and graph execution in TensorFlow.",
        "How do you use `tf.data` pipeline for efficient data loading?",
        "What is the role of `tf.GradientTape` in custom training loops?",
    ],
    "pytorch": [
        "How does PyTorch's autograd system track computations for backpropagation?",
        "Explain the difference between `nn.Module` and `nn.functional` in PyTorch.",
        "How do you implement a custom dataset and dataloader in PyTorch?",
    ],
    "pandas": [
        "What is the difference between `apply()`, `map()`, and `applymap()` in Pandas?",
        "How do you handle missing data in Pandas? Compare different strategies.",
        "Explain `groupby` and its split-apply-combine mechanism.",
    ],
    "scikit-learn": [
        "Explain scikit-learn's `Pipeline` and why it's important for production ML.",
        "How does `GridSearchCV` work for hyperparameter tuning?",
        "What is the difference between `fit_transform()` and `transform()` in scikit-learn?",
    ],
    "statistics": [
        "Explain the Central Limit Theorem and its importance in data science.",
        "What is the difference between Type I and Type II errors?",
        "How do you interpret a p-value? What are its common misunderstandings?",
        "Explain the difference between parametric and non-parametric tests.",
    ],
    "data analysis": [
        "Walk through your approach to exploratory data analysis on a new dataset.",
        "How do you identify and handle outliers in a dataset?",
        "Explain the difference between correlation and causation with an example.",
    ],
    "data visualization": [
        "What chart types are most effective for comparing distributions? Why?",
        "How do you design a dashboard for non-technical stakeholders?",
        "Explain the principles of effective data storytelling.",
    ],
    "feature engineering": [
        "How do you handle categorical variables with high cardinality?",
        "Explain feature scaling — when to use standardization vs normalization.",
        "How do you create time-based features for a time-series problem?",
    ],

    # Cloud & DevOps
    "aws": [
        "Explain the difference between EC2, Lambda, and ECS. When would you use each?",
        "How does AWS S3 ensure data durability and availability?",
        "Explain VPC networking — subnets, security groups, and NACLs.",
    ],
    "docker": [
        "Explain the difference between a Docker image and a container.",
        "How do multi-stage builds help reduce Docker image size?",
        "What is the difference between `COPY` and `ADD` in a Dockerfile?",
        "How do you manage persistent data in Docker containers?",
    ],
    "kubernetes": [
        "Explain the difference between a Deployment and a StatefulSet in Kubernetes.",
        "How does Kubernetes handle service discovery and load balancing?",
        "What is a Kubernetes Operator and when would you build one?",
    ],
    "ci/cd": [
        "Design a CI/CD pipeline for a microservices application. What stages would you include?",
        "How do you implement blue-green deployments vs canary deployments?",
        "What is infrastructure as code and how does it fit into CI/CD?",
    ],
    "git": [
        "Explain the difference between `git rebase` and `git merge`. When to use each?",
        "How do you resolve a merge conflict in Git?",
        "What is a Git branching strategy? Compare GitFlow vs trunk-based development.",
    ],
    "linux": [
        "How do you troubleshoot a Linux server that's running out of memory?",
        "Explain file permissions in Linux — what does `chmod 755` mean?",
        "What is the difference between a process and a thread in Linux?",
    ],
    "terraform": [
        "Explain Terraform state and why remote state backends are important.",
        "What is the difference between Terraform modules and workspaces?",
        "How do you handle secrets in Terraform configurations?",
    ],

    # Data Engineering
    "spark": [
        "Explain the difference between RDDs, DataFrames, and Datasets in Spark.",
        "How does Spark handle data partitioning and shuffling?",
        "What is the Catalyst Optimizer in Spark SQL?",
    ],
    "kafka": [
        "Explain Kafka's architecture — brokers, topics, partitions, and consumer groups.",
        "How does Kafka ensure message ordering and exactly-once delivery?",
        "What is the difference between Kafka and RabbitMQ?",
    ],
    "airflow": [
        "What is an Apache Airflow DAG and how do you handle dependencies between tasks?",
        "Explain Airflow's executor types (Local, Celery, Kubernetes).",
        "How do you handle failure retries and alerting in Airflow?",
    ],
    "etl": [
        "Walk through your approach to designing an ETL pipeline for a real-time data source.",
        "How do you handle schema evolution in an ETL pipeline?",
        "What is the difference between ETL and ELT? When would you use each?",
    ],

    # Cybersecurity
    "cybersecurity": [
        "Explain the OWASP Top 10 vulnerabilities and how to mitigate them.",
        "What is the difference between authentication and authorization?",
        "How would you implement a secure password storage system?",
    ],
    "penetration testing": [
        "Walk through the phases of a penetration test from reconnaissance to reporting.",
        "What is the difference between black-box and white-box penetration testing?",
        "Explain common privilege escalation techniques in Linux.",
    ],
    "network security": [
        "Explain the difference between IDS and IPS systems.",
        "How does TLS/SSL encryption work? Explain the handshake process.",
        "What is a zero-trust security model?",
    ],

    # Visualization Tools
    "tableau": [
        "How do you create calculated fields in Tableau? Give a complex example.",
        "Explain the difference between Tableau's live connection and extract mode.",
        "How do you optimize Tableau dashboard performance for large datasets?",
    ],
    "power bi": [
        "Explain DAX measures vs calculated columns in Power BI.",
        "How do you model star schema relationships in Power BI?",
        "What is row-level security (RLS) in Power BI and how do you implement it?",
    ],
    "excel": [
        "Explain VLOOKUP vs INDEX-MATCH. Why might you prefer one over the other?",
        "How do you create dynamic dashboards using pivot tables and slicers?",
        "What are array formulas in Excel and when are they useful?",
    ],

    # AI / GenAI
    "generative ai": [
        "Explain the difference between fine-tuning and prompt engineering for LLMs.",
        "What are the ethical concerns with generative AI and how would you address them?",
        "How does Retrieval-Augmented Generation (RAG) work?",
    ],
    "llm": [
        "Explain the attention mechanism in Transformers and its computational complexity.",
        "How do you evaluate the quality of an LLM's outputs?",
        "What is the difference between zero-shot, few-shot, and fine-tuned LLM approaches?",
    ],

    # Blockchain
    "blockchain": [
        "Explain the consensus mechanisms: Proof of Work vs Proof of Stake.",
        "What are smart contracts and how do they execute on the blockchain?",
    ],

    # Agile / Management
    "agile": [
        "Explain the Agile Manifesto principles and how they apply to software development.",
        "What is the difference between Scrum and Kanban?",
    ],
    "scrum": [
        "Explain the roles in Scrum — Product Owner, Scrum Master, and Dev Team.",
        "What happens in Sprint Planning, Daily Standup, and Sprint Retrospective?",
    ],
}

# ============================================================
# SCENARIO QUESTION TEMPLATES
# ============================================================

SCENARIO_TEMPLATES = {
    "Data Analyst": [
        "Your stakeholder reports that monthly revenue numbers don't match between two dashboards. How would you investigate and resolve the discrepancy?",
        "You're given a messy dataset with 40% missing values, duplicate records, and inconsistent date formats. Walk through your data cleaning strategy.",
        "A marketing team asks you to analyze the effectiveness of their latest campaign. What metrics would you choose and why?",
        "You discover that a key KPI has dropped 20% week-over-week. How do you investigate the root cause?",
    ],
    "ML Engineer": [
        "Your production ML model's accuracy has degraded by 15% over the past month. How do you diagnose and fix this?",
        "You need to deploy a model that processes 10,000 predictions per second. How would you architect the serving infrastructure?",
        "Your training pipeline takes 12 hours and the data science team wants to iterate faster. How would you optimize it?",
        "A model performs well on test data but poorly in production. What could cause this and how would you debug it?",
    ],
    "Web Developer": [
        "A client's e-commerce site is loading in 8 seconds. Walk through your approach to optimize it to under 2 seconds.",
        "You discover a critical XSS vulnerability in your production web application. How do you respond?",
        "Your web application needs to handle 50x traffic during a flash sale. How would you prepare?",
        "A user reports that the checkout process is broken on iOS Safari. How do you debug cross-browser issues?",
    ],
    "Data Engineer": [
        "Your ETL pipeline failed at 2 AM and downstream reports are delayed. Walk through your incident response.",
        "You need to migrate a 5TB PostgreSQL database to a data lake with zero downtime. How would you approach this?",
        "Data consumers report that some records arrive 24 hours late. How do you diagnose and fix the latency issue?",
        "Your Spark job is failing due to out-of-memory errors on a 2TB dataset. How do you optimize it?",
    ],
    "DevOps Engineer": [
        "A production deployment caused a 30-minute outage. How do you perform a post-mortem and prevent recurrence?",
        "You need to migrate 20 microservices from EC2 to Kubernetes with minimal downtime. Plan your approach.",
        "CPU usage on a production server suddenly spikes to 100%. Walk through your debugging process.",
        "Your CI/CD pipeline takes 45 minutes to complete. How would you optimize it to under 10 minutes?",
    ],
    "Data Scientist": [
        "A business stakeholder wants to predict customer churn. Walk through your complete ML project lifecycle.",
        "Your A/B test shows a 2% improvement with a p-value of 0.06. How do you advise the product team?",
        "You need to explain a complex ensemble model to non-technical executives. How do you approach this?",
        "Your model has high accuracy but the business team says it's not useful. What might be wrong?",
    ],
    "Frontend Developer": [
        "Users complain your React app is slow on mobile devices. How would you diagnose and fix performance issues?",
        "You need to implement real-time collaborative editing (like Google Docs) in the browser. Outline your approach.",
        "Your accessibility audit reveals 50 WCAG violations. How do you prioritize and fix them?",
    ],
    "Backend Developer": [
        "Your API endpoint has a p99 latency of 5 seconds. Walk through how you'd identify the bottleneck.",
        "You need to design a rate-limiting system for your API. What algorithms would you consider?",
        "A database migration needs to add a column to a table with 500M rows without downtime. How?",
    ],
    "Full Stack Developer": [
        "You're tasked with building a real-time notification system. Describe your architecture decisions.",
        "Your application needs to support both web and mobile. How do you design the API and frontend?",
        "A user reports intermittent 500 errors. Walk through your debugging approach across the full stack.",
    ],
    "Cybersecurity Analyst": [
        "You detect unusual outbound traffic from a production server at midnight. Walk through your incident response.",
        "A developer accidentally committed API keys to a public repository. What steps do you take immediately?",
        "You need to perform a security assessment of a new SaaS tool before company-wide deployment. What's your process?",
    ],
}

# ============================================================
# BEHAVIORAL QUESTION TEMPLATES (role-aware)
# ============================================================

BEHAVIORAL_TEMPLATES = {
    "default": [
        "Tell me about a time you had to learn a new technology quickly to meet a project deadline.",
        "Describe a situation where you disagreed with a teammate's technical approach. How did you handle it?",
        "Give an example of a time when you had to prioritize multiple competing tasks. How did you decide?",
        "Tell me about a project that failed. What did you learn and how did it change your approach?",
        "Describe a time you had to explain a complex technical concept to a non-technical stakeholder.",
        "Tell me about a time you identified and fixed a bug that others had missed.",
        "Describe a situation where you had to advocate for a better technical solution against pushback.",
        "Give an example of when you mentored or helped a colleague grow their skills.",
    ],
    "Data Analyst": [
        "Tell me about a time your data analysis led to a significant business decision.",
        "Describe a situation where the data contradicted the stakeholder's assumptions. How did you handle it?",
    ],
    "ML Engineer": [
        "Describe a time when a model you built didn't perform as expected. How did you iterate?",
        "Tell me about a time you had to make trade-offs between model accuracy and deployment constraints.",
    ],
    "Data Scientist": [
        "Tell me about a time you communicated statistical findings to non-technical stakeholders.",
        "Describe a project where you had to choose between model interpretability and performance.",
    ],
    "Web Developer": [
        "Describe a time you improved the user experience based on data or feedback.",
        "Tell me about a challenging responsive design problem you solved.",
    ],
    "DevOps Engineer": [
        "Tell me about a critical production incident you resolved. What was your process?",
        "Describe a time you improved system reliability or reduced deployment frequency.",
    ],
}

# ============================================================
# IMPROVEMENT QUESTION TEMPLATES
# ============================================================

IMPROVEMENT_TEMPLATES = [
    "You listed {skill} as a required skill but it's not on your resume. How familiar are you with it and what's your plan to develop this skill?",
    "If asked to work on a {skill}-based project tomorrow, how would you ramp up quickly?",
    "{skill} is critical for this role. What resources or strategies would you use to build proficiency?",
    "Can you describe any indirect experience you have with {skill}, even if it wasn't a primary skill?",
    "How would you approach a task requiring {skill} given your current skill set?",
    "What aspects of {skill} do you find most challenging, and how would you overcome them?",
    "If you were to build a personal project to learn {skill}, what would you create?",
]


# ============================================================
# EXPERIENCE LEVEL ADJECTIVES
# ============================================================

DIFFICULTY_MAP = {
    "entry": {
        "prefix": "As a junior candidate",
        "depth": "foundational",
    },
    "mid": {
        "prefix": "For a mid-level role",
        "depth": "intermediate",
    },
    "senior": {
        "prefix": "As a senior engineer",
        "depth": "advanced / system-design",
    },
}


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_interview_questions(
    job_role: str,
    matched_skills: list[str],
    missing_skills: list[str],
    match_percentage: float,
    experience_level: str = "mid",
) -> dict:
    """
    Generate a personalized interview preparation set.

    Args:
        job_role: Target job role
        matched_skills: Skills the candidate has
        missing_skills: Skills the candidate is missing
        match_percentage: Skill match percentage (0-100)
        experience_level: "entry", "mid", or "senior"

    Returns:
        Dict with technical_questions, improvement_questions,
        scenario_questions, and behavioral_questions.
    """
    experience_level = experience_level.lower().strip()
    if experience_level not in DIFFICULTY_MAP:
        experience_level = "mid"

    diff = DIFFICULTY_MAP[experience_level]

    # ----- 1. Technical Questions (5) — from matched/strong skills -----
    technical_questions = []
    matched_lower = [s.lower() for s in matched_skills]

    # Collect all matching questions from the bank
    candidate_tech_qs = []
    for skill in matched_lower:
        if skill in TECHNICAL_QUESTIONS:
            for q in TECHNICAL_QUESTIONS[skill]:
                candidate_tech_qs.append({"skill": skill, "question": q})

    # If not enough from matched skills, add from the role's general skills
    if len(candidate_tech_qs) < 5:
        all_skills = matched_lower + [s.lower() for s in missing_skills]
        for skill in all_skills:
            if skill in TECHNICAL_QUESTIONS and skill not in matched_lower:
                for q in TECHNICAL_QUESTIONS[skill]:
                    candidate_tech_qs.append({"skill": skill, "question": q})

    random.shuffle(candidate_tech_qs)
    seen = set()
    for item in candidate_tech_qs:
        if len(technical_questions) >= 5:
            break
        if item["question"] not in seen:
            seen.add(item["question"])
            technical_questions.append({
                "skill": item["skill"],
                "question": item["question"],
                "difficulty": experience_level,
            })

    # ----- 2. Improvement Questions (3) — from missing skills -----
    improvement_questions = []
    missing_lower = [s.lower() for s in missing_skills]

    selected_missing = missing_lower[:6] if len(missing_lower) > 6 else missing_lower
    random.shuffle(selected_missing)

    for i, skill in enumerate(selected_missing[:3]):
        template = IMPROVEMENT_TEMPLATES[i % len(IMPROVEMENT_TEMPLATES)]
        improvement_questions.append({
            "skill": skill,
            "question": template.format(skill=skill.title()),
        })

    # If fewer than 3 missing skills, pad with generic ones
    while len(improvement_questions) < 3 and missing_lower:
        skill = random.choice(missing_lower)
        tmpl = random.choice(IMPROVEMENT_TEMPLATES)
        q = tmpl.format(skill=skill.title())
        if not any(iq["question"] == q for iq in improvement_questions):
            improvement_questions.append({"skill": skill, "question": q})

    # ----- 3. Scenario Questions (2) — role-specific -----
    scenario_questions = []
    role_scenarios = SCENARIO_TEMPLATES.get(job_role, [])

    if not role_scenarios:
        # Fallback: pick from any role
        all_scenarios = []
        for scenes in SCENARIO_TEMPLATES.values():
            all_scenarios.extend(scenes)
        role_scenarios = all_scenarios

    random.shuffle(role_scenarios)
    for q in role_scenarios[:2]:
        scenario_questions.append({"question": q})

    # ----- 4. Behavioral Questions (2) — role + default mix -----
    behavioral_questions = []
    role_behavioral = BEHAVIORAL_TEMPLATES.get(job_role, [])
    default_behavioral = BEHAVIORAL_TEMPLATES.get("default", [])

    all_behavioral = role_behavioral + default_behavioral
    random.shuffle(all_behavioral)

    seen_b = set()
    for q in all_behavioral:
        if len(behavioral_questions) >= 2:
            break
        if q not in seen_b:
            seen_b.add(q)
            behavioral_questions.append({"question": q})

    return {
        "job_role": job_role,
        "experience_level": experience_level,
        "match_percentage": match_percentage,
        "total_questions": len(technical_questions) + len(improvement_questions) + len(scenario_questions) + len(behavioral_questions),
        "technical_questions": technical_questions,
        "improvement_questions": improvement_questions,
        "scenario_questions": scenario_questions,
        "behavioral_questions": behavioral_questions,
    }
