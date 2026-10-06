import streamlit as st
from pdf_parser import parse_pdf_text
from ai_analyzer import get_ai_feedback

st.set_page_config(page_title="JobPulse AI", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #040b14;
}

.stApp {
    background: radial-gradient(circle at top left, rgba(30, 64, 175, 0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(14, 165, 233, 0.16), transparent 25%),
                linear-gradient(135deg, #020817 0%, #071120 45%, #0b1324 100%);
    color: #f8fbff;
}

[data-testid="stSidebar"] {
    background: rgba(6, 14, 28, 0.88);
    border-right: 1px solid rgba(148, 163, 184, 0.18);
}

.css-1d391kg, .css-1wrcr25 {
    background: rgba(15, 23, 42, 0.6) !important;
}

.kpi-card, .job-card, .panel, .profile-card {
    background: rgba(15, 23, 42, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 22px;
    padding: 1.2rem 1.3rem;
    box-shadow: 0 20px 40px rgba(14, 165, 233, 0.08);
    backdrop-filter: blur(10px);
    animation: floatIn 0.6s ease;
}

@keyframes floatIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

.big-title {
    background: linear-gradient(90deg, #f8fafc, #7dd3fc, #a78bfa);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    font-size: 2.8rem !important;
    font-weight: 900;
    letter-spacing: -0.06em;
}

.subtle {
    color: #9fb5c9;
    font-size: 1.03rem;
}

.metric {
    font-size: 2rem;
    font-weight: 800;
    color: white;
}

.metric-label {
    color: #94a3b8;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.stButton > button {
    border-radius: 14px !important;
    background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
    color: white !important;
    border: none !important;
    font-weight: 700;
    padding: 0.7rem 1.2rem;
    box-shadow: 0 12px 28px rgba(14, 165, 233, 0.28);
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 18px 36px rgba(139, 92, 246, 0.35);
}

div[data-baseweb="select"] > div {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 12px;
}

input, textarea {
    background: rgba(15, 23, 42, 0.8) !important;
    color: white !important;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
    border-radius: 12px !important;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #34d399, #22d3ee);
}

</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


def init_state():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "users" not in st.session_state:
        st.session_state.users = {
            "demo@jobpulse.ai": {
                "name": "Aarav Sharma",
                "password": "demo123",
                "role": "Python Developer",
                "location": "Bengaluru, India",
                "goal": "Full-stack and AI career growth",
                "bio": "Building impactful products and learning AI-powered systems.",
            }
        }
    if "jobs" not in st.session_state:
        st.session_state.jobs = [
            {
                "title": "AI Product Analyst",
                "company": "Astra Labs",
                "location": "Remote",
                "salary": "$95k - $120k",
                "match": 96,
                "skills": ["Python", "AI", "SQL", "Analytics"],
                "description": "Build AI workflows, dashboards, and product insight pipelines.",
            },
            {
                "title": "Python Backend Engineer",
                "company": "NovaStack",
                "location": "Pune",
                "salary": "$80k - $110k",
                "match": 92,
                "skills": ["Python", "FastAPI", "Docker", "SQL"],
                "description": "Develop secure REST APIs and scalable backend services.",
            },
            {
                "title": "Data & AI Analyst",
                "company": "BlueOrbit",
                "location": "Hyderabad",
                "salary": "$90k - $118k",
                "match": 89,
                "skills": ["Python", "Power BI", "AI", "Data"],
                "description": "Turn data into high-impact decisions for product and growth teams.",
            },
        ]
    if "skills" not in st.session_state:
        st.session_state.skills = {
            "Python": 92,
            "SQL": 84,
            "FastAPI": 76,
            "Machine Learning": 68,
            "Docker": 61,
            "Communication": 88,
        }
    if "resume_history" not in st.session_state:
        st.session_state.resume_history = []


init_state()


def login_register_ui():
    st.title("JobPulse AI")
    st.markdown("<div class='subtle'>Career intelligence, resume clarity, and smarter hiring outcomes.</div>", unsafe_allow_html=True)
    tabs = st.tabs(["Login", "Register"])

    with tabs[0]:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", use_container_width=True):
            user = st.session_state.users.get(email)
            if user and user["password"] == password:
                st.session_state.current_user = {"email": email, **user}
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with tabs[1]:
        name = st.text_input("Full name")
        email = st.text_input("Email address")
        password = st.text_input("Create password", type="password")
        role = st.text_input("Current role / target role")
        if st.button("Create account", use_container_width=True):
            if not name or not email or not password:
                st.warning("Please fill in all required fields.")
            else:
                st.session_state.users[email] = {
                    "name": name,
                    "password": password,
                    "role": role or "Career switcher",
                    "location": "Not specified",
                    "goal": "Grow faster in tech and AI roles",
                    "bio": "New to JobPulse, ready to grow and apply strategically.",
                }
                st.session_state.current_user = {"email": email, **st.session_state.users[email]}
                st.session_state.auth = True
                st.success("Account created successfully.")
                st.rerun()

    st.markdown("### Demo access")
    st.info("Use demo@jobpulse.ai / demo123 to explore the app instantly.")


if not st.session_state.auth:
    login_register_ui()
    st.stop()


user = st.session_state.current_user


def show_header():
    st.markdown(f"<div class='big-title'>Welcome back, {user['name']} 👋</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtle'>{user['role']} • {user['location']}</div>", unsafe_allow_html=True)
    st.markdown("---")


def render_dashboard():
    st.subheader("Career dashboard")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='kpi-card'><div class='metric-label'>Profile strength</div><div class='metric'>92%</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='kpi-card'><div class='metric-label'>Jobs matched</div><div class='metric'>18</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='kpi-card'><div class='metric-label'>Skills upgraded</div><div class='metric'>7</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='kpi-card'><div class='metric-label'>Applications sent</div><div class='metric'>11</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1.6, 1])
    with col_a:
        st.markdown("### Momentum overview")
        st.markdown("- Resume matching score on top target roles is trending upward.")
        st.markdown("- Python / SQL / AI skill stack is aligned with current hiring trends.")
        st.markdown("- Your strongest opportunities are in product, backend, and AI analyst roles.")
    with col_b:
        st.markdown("### Weekly growth")
        progress = 82
        st.progress(progress)
        st.caption(f"{progress}% of your 90-day roadmap completed")
    st.markdown("</div>", unsafe_allow_html=True)


def render_profile():
    st.subheader("Profile")
    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<div style='display:flex; justify-content:center; align-items:center; width:120px; height:120px; border-radius:50%; background:linear-gradient(135deg,#0ea5e9,#8b5cf6); color:white; font-size:2rem; font-weight:800; margin:auto;'>AA</div>", unsafe_allow_html=True)
    with col2:
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Role:** {user['role']}")
        st.write(f"**Location:** {user['location']}")
        st.write(f"**Goal:** {user['goal']}")
        st.write(f"**Bio:** {user['bio']}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_jobs():
    st.subheader("Available jobs")
    for job in st.session_state.jobs:
        with st.container():
            st.markdown("<div class='job-card'>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 1.2, 1])
            with col1:
                st.markdown(f"### {job['title']}")
                st.caption(f"{job['company']} • {job['location']}")
                st.write(job['description'])
                st.write("Skills: " + ", ".join(job['skills']))
            with col2:
                st.metric("Match", f"{job['match']}%")
                st.metric("Salary", job['salary'])
            with col3:
                if st.button("Apply", key=f"apply_{job['title']}"):
                    st.success(f"Saved application interest for {job['title']}.")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")


def render_skill_tracker():
    st.subheader("Skill tracker")
    skill_name = st.text_input("Add a new skill")
    if skill_name:
        if st.button("Add skill"):
            st.session_state.skills.setdefault(skill_name.strip(), 50)
            st.success(f"Added {skill_name.strip()} to your tracker.")

    for skill, level in list(st.session_state.skills.items()):
        st.markdown(f"**{skill}**")
        new_level = st.slider(f"Progress for {skill}", 0, 100, level, key=f"skill_{skill}")
        st.session_state.skills[skill] = new_level
        st.progress(new_level)
        st.markdown("---")


def render_resume_analyzer():
    st.subheader("Resume analyzer")
    col1, col2 = st.columns([1, 1])
    with col1:
        job_title = st.text_input("Target job title", value=user['role'])
        job_description = st.text_area("Job description", height=180, value="We are looking for a Python developer with FastAPI, SQL, Docker, analytics, and strong communication and project delivery skills.")
    with col2:
        resume_source = st.radio("How do you want to provide your resume?", ["Upload PDF", "Paste text"], horizontal=True)
        resume_text = ""
        if resume_source == "Upload PDF":
            uploaded = st.file_uploader("Upload resume", type=["pdf"])
            if uploaded is not None:
                resume_text = parse_pdf_text(uploaded.getvalue())
                if resume_text:
                    st.success("PDF parsed successfully.")
                else:
                    st.warning("This PDF could not be parsed. Please paste the text instead.")
        else:
            resume_text = st.text_area("Paste resume text", height=200)

    if st.button("Analyze my resume", use_container_width=True):
        if not job_title or not job_description or not resume_text:
            st.warning("Please add the job title, job description, and resume content.")
        else:
            with st.spinner("Running AI-powered analysis..."):
                feedback = get_ai_feedback(resume_text, job_title, job_description)
                source = feedback.get("source", "fallback")
                if source == "fallback":
                    st.info(feedback.get("status_message", "AI is temporarily unavailable, so offline analysis is being used."))
                else:
                    st.success("Gemini analysis completed successfully.")

                st.markdown("### Resume report")
                score = feedback.get("overall_score", 70)
                st.subheader(f"Overall match: {score}/100")
                st.progress(score)

                st.markdown("#### Strengths")
                for item in feedback.get("strengths", [])[:3]:
                    st.markdown(f"- {item}")

                st.markdown("#### Areas to improve")
                for item in feedback.get("areas_for_improvement", [])[:3]:
                    st.markdown(f"- {item}")

                kw = feedback.get("keyword_analysis", {})
                found = kw.get("found", [])
                missing = kw.get("missing", [])
                st.markdown("#### Keyword match")
                st.write(f"**Matched keywords:** {', '.join(found) if found else 'None'}")
                st.write(f"**Missing keywords:** {', '.join(missing) if missing else 'None'}")

                rewrite = feedback.get("suggested_rewrite", {})
                st.markdown("#### Suggested bullet rewrite")
                st.code(rewrite.get("improved", "No rewrite generated."), language="text")

                st.session_state.resume_history.append({
                    "job": job_title,
                    "score": score,
                    "timestamp": "Just now",
                })


def render_roadmap():
    st.subheader("Career roadmap")
    roadmap = [
        ("Week 1-2", "Refine resume keywords and role-specific bullets."),
        ("Week 3-4", "Build one advanced project with measurable outcomes."),
        ("Week 5-6", "Practice interview stories and system design basics."),
        ("Week 7-8", "Apply to 10 targeted roles and improve portfolio."),
    ]
    for period, item in roadmap:
        st.markdown(f"**{period}**: {item}")


nav = st.sidebar.radio("Navigation", ["Dashboard", "Resume Analyzer", "Available Jobs", "Skill Tracker", "Career Roadmap", "Profile"])

show_header()

if nav == "Dashboard":
    render_dashboard()
elif nav == "Resume Analyzer":
    render_resume_analyzer()
elif nav == "Available Jobs":
    render_jobs()
elif nav == "Skill Tracker":
    render_skill_tracker()
elif nav == "Career Roadmap":
    render_roadmap()
else:
    render_profile()

st.sidebar.markdown("---")
st.sidebar.subheader("Quick actions")
if st.sidebar.button("Log out"):
    st.session_state.auth = False
    st.session_state.current_user = None
    st.rerun()

st.sidebar.caption("Built for modern career growth and AI-first hiring.")

