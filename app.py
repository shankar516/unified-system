# app.py  (ONLY background animation added; NO other functionality changed)
import re
import base64
from pathlib import Path

import streamlit as st
import plotly.express as px

from resume_parser import parse_resume
from ai_client import AIClient

# ✅ CSV-based auth
from auth_csv import register_user, verify_login

st.set_page_config(page_title="Resume Insight & Roadmap", layout="wide")

# =========================
# SESSION STATE INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "logged_user" not in st.session_state:
    st.session_state.logged_user = ""

if "history" not in st.session_state:
    st.session_state.history = ""
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "domain" not in st.session_state:
    st.session_state.domain = ""
if "resume_summary" not in st.session_state:
    st.session_state.resume_summary = ""
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "mcqs" not in st.session_state:
    st.session_state.mcqs = []
if "mcq_answers" not in st.session_state:
    st.session_state.mcq_answers = {}

if "skill_dist" not in st.session_state:
    st.session_state.skill_dist = []

if "roadmap_text" not in st.session_state:
    st.session_state.roadmap_text = ""
if "assistive_mode" not in st.session_state:
    st.session_state.assistive_mode = False
if "assist_chat" not in st.session_state:
    st.session_state.assist_chat = []

# ✅ Placement mode state
if "placement_mode" not in st.session_state:
    st.session_state.placement_mode = False
if "linkedin_url" not in st.session_state:
    st.session_state.linkedin_url = ""
if "placement_jobs_ai" not in st.session_state:
    st.session_state.placement_jobs_ai = ""   # markdown text output
if "placement_jobs_search" not in st.session_state:
    st.session_state.placement_jobs_search = ""  # markdown text output

# ✅ NEW (requested): job role input for option B
if "placement_search_role" not in st.session_state:
    st.session_state.placement_search_role = ""

# =========================
# BACKGROUND (optional slideshow) + Light/Dark safe
# ✅ ONLY CHANGE: add simple animation to existing background
# =========================
def _b64_image(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return base64.b64encode(p.read_bytes()).decode("utf-8")

bg1 = _b64_image("assets/bg1.jpg")
bg2 = _b64_image("assets/bg2.jpg")
bg3 = _b64_image("assets/bg3.jpg")
has_bg = all([bg1, bg2, bg3])

if has_bg:
    st.markdown(
        f"""
        <style>
          .stApp {{ background: #0b1220; }}

          .app-bg {{
            position: fixed; inset: 0; z-index: -2;
            background-size: cover; background-position: center;

            /* ✅ existing slideshow */
            animation: bgSwap 18s infinite;

            /* ✅ NEW: make motion visible */
            will-change: transform;
          }}

          /* ✅ NEW: animate the background image movement */
          .app-bg {{
            animation: bgSwap 18s infinite, bgFloat 10s ease-in-out infinite;
          }}

          .app-bg::after {{
            content: ""; position: absolute; inset: 0;
            background:
              radial-gradient(circle at 20% 10%, rgba(59,130,246,0.28), transparent 45%),
              radial-gradient(circle at 80% 20%, rgba(16,185,129,0.22), transparent 45%),
              linear-gradient(180deg, rgba(0,0,0,0.45), rgba(0,0,0,0.60));

            /* ✅ NEW: subtle overlay drift */
            will-change: transform;
            animation: overlayDrift 7s ease-in-out infinite;
          }}

          @media (prefers-color-scheme: light) {{
            .stApp {{ background: #f5f7fb; }}
            .app-bg::after {{
              background:
                radial-gradient(circle at 20% 10%, rgba(59,130,246,0.18), transparent 45%),
                radial-gradient(circle at 80% 20%, rgba(16,185,129,0.14), transparent 45%),
                linear-gradient(180deg, rgba(255,255,255,0.70), rgba(255,255,255,0.82));
              animation: overlayDrift 7s ease-in-out infinite;
            }}
          }}

          @keyframes bgSwap {{
            0%   {{ background-image: url("data:image/jpeg;base64,{bg1}"); }}
            33%  {{ background-image: url("data:image/jpeg;base64,{bg2}"); }}
            66%  {{ background-image: url("data:image/jpeg;base64,{bg3}"); }}
            100% {{ background-image: url("data:image/jpeg;base64,{bg1}"); }}
          }}

          /* ✅ NEW: visible zoom+pan */
          @keyframes bgFloat {{
            0%   {{ transform: scale(1.02) translate(0px, 0px); }}
            50%  {{ transform: scale(1.07) translate(-18px, -10px); }}
            100% {{ transform: scale(1.02) translate(0px, 0px); }}
          }}

          /* ✅ NEW: overlay drift */
          @keyframes overlayDrift {{
            0%   {{ transform: translate(0px, 0px); }}
            50%  {{ transform: translate(16px, -12px); }}
            100% {{ transform: translate(0px, 0px); }}
          }}

          /* ✅ NEW: respect reduced motion */
          @media (prefers-reduced-motion: reduce) {{
            .app-bg, .app-bg::after {{ animation: none !important; }}
          }}
        </style>
        <div class="app-bg"></div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
          .stApp {
            background:
              radial-gradient(circle at 20% 10%, rgba(59,130,246,0.20), transparent 40%),
              radial-gradient(circle at 80% 20%, rgba(16,185,129,0.18), transparent 45%),
              radial-gradient(circle at 30% 90%, rgba(236,72,153,0.12), transparent 40%),
              linear-gradient(180deg, #070b14, #0b1220);

            /* ✅ NEW: simple background movement */
            background-size: 140% 140%;
            animation: bgPan 10s ease-in-out infinite;
          }

          @media (prefers-color-scheme: light) {
            .stApp {
              background:
                radial-gradient(circle at 20% 10%, rgba(59,130,246,0.16), transparent 45%),
                radial-gradient(circle at 80% 20%, rgba(16,185,129,0.12), transparent 50%),
                radial-gradient(circle at 30% 90%, rgba(236,72,153,0.10), transparent 45%),
                linear-gradient(180deg, #f5f7fb, #eef2f7);
              background-size: 140% 140%;
              animation: bgPan 10s ease-in-out infinite;
            }
          }

          @keyframes bgPan {
            0%   { background-position: 0% 0%; }
            50%  { background-position: 100% 60%; }
            100% { background-position: 0% 0%; }
          }

          @media (prefers-reduced-motion: reduce) {
            .stApp { animation: none !important; }
          }
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================
# CSS (keep your current UI)
# =========================
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.8rem; padding-bottom: 2.2rem; max-width: 1150px; }
      footer { visibility: hidden; }

      :root {
        --card-bg: rgba(255,255,255,0.07);
        --card-border: rgba(255,255,255,0.16);
        --shadow: 0 14px 40px rgba(0,0,0,0.35);
        --text: rgba(255,255,255,0.94);
        --muted: rgba(255,255,255,0.78);
        --chip-bg: rgba(255,255,255,0.10);
        --chip-border: rgba(255,255,255,0.16);
        --input-bg: rgba(255,255,255,0.10);
      }
      @media (prefers-color-scheme: light) {
        :root {
          --card-bg: rgba(255,255,255,0.94);
          --card-border: rgba(0,0,0,0.10);
          --shadow: 0 12px 30px rgba(0,0,0,0.12);
          --text: rgba(0,0,0,0.90);
          --muted: rgba(0,0,0,0.65);
          --chip-bg: rgba(0,0,0,0.04);
          --chip-border: rgba(0,0,0,0.10);
          --input-bg: rgba(255,255,255,1.0);
        }
      }
      .stApp, .stMarkdown, .stText, .stCaption, label, p, h1, h2, h3, h4, h5, h6 { color: var(--text) !important; }

      .hero { padding: 22px; border-radius: 22px; background: var(--card-bg); border: 1px solid var(--card-border);
              box-shadow: var(--shadow); backdrop-filter: blur(14px); margin-bottom: 16px; }
      .hero-title { font-size: 2.25rem; font-weight: 900; margin: 0; line-height: 1.08; }
      .grad { background: linear-gradient(90deg, rgba(59,130,246,1), rgba(16,185,129,1), rgba(236,72,153,1));
              -webkit-background-clip: text; background-clip: text; color: transparent !important; }
      .hero-sub { margin-top: 10px; font-size: 1.05rem; color: var(--muted) !important; }

      .chips { margin-top: 14px; display:flex; gap:10px; flex-wrap: wrap; }
      .chip { padding: 7px 12px; border-radius: 999px; background: var(--chip-bg); border: 1px solid var(--chip-border);
              font-size: 0.92rem; color: var(--text) !important; }

      .glass { padding: 22px; border-radius: 20px; background: var(--card-bg); border: 1px solid var(--card-border);
               box-shadow: var(--shadow); backdrop-filter: blur(14px); }
      .muted { color: var(--muted) !important; font-size: 0.95rem; }

      input, textarea { background: var(--input-bg) !important; color: var(--text) !important;
                        border: 1px solid var(--card-border) !important; border-radius: 12px !important; }

      .stButton>button { border-radius: 14px; padding: 0.74rem 1rem; font-weight: 650; }

      section[data-testid="stSidebar"] > div { background: var(--card-bg); border-right: 1px solid var(--card-border); backdrop-filter: blur(14px); }
      hr { opacity: 0.25; }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# HERO HEADER
# =========================
st.markdown(
    """
    <div class="hero">
      <div class="hero-title">
        <span>📄</span> <span class="grad">AI Resume Analyzer</span> & Career Roadmap
      </div>
      <div class="hero-sub">
        End-to-end pipeline: Local parsing (PDF/OCR) → Domain selection → LLM-generated MCQ test → Interview simulation → Personalized roadmap
      </div>
      <div class="chips">
        <div class="chip">🔍 PDFPlumber + Tesseract OCR</div>
        <div class="chip">🧠 Groq / xAI / OpenAI</div>
        <div class="chip">📝 Dynamic MCQs</div>
        <div class="chip">🎯 Interview Feedback</div>
        <div class="chip">🧭 Weekly Roadmap</div>
        <div class="chip">🔐 CSV Login</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# CENTER AUTH UI
# =========================
def auth_ui_center():
    left, center, right = st.columns([1, 1.45, 1])
    with center:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("### 🔐 User Authentication")
        st.markdown(
            '<div class="muted">Sign in to access resume analysis, domain-based assessments, and personalized learning roadmaps.</div>',
            unsafe_allow_html=True
        )
        st.write("")
        tab = st.radio("Choose", ["Login", "Register"], horizontal=True)

        if tab == "Register":
            ru = st.text_input("Username", placeholder="e.g., shankar")
            re_ = st.text_input("Email", placeholder="e.g., shankar@example.com")
            rp = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
            st.caption("Prototype authentication: stored locally in CSV with salted hashing.")
            if st.button("Create Account", use_container_width=True):
                ok, msg = register_user(ru, re_, rp)
                st.success(msg) if ok else st.error(msg)
        else:
            lu = st.text_input("Username", placeholder="Enter your username")
            lp = st.text_input("Password", type="password", placeholder="Enter your password")
            if st.button("Login", use_container_width=True):
                ok, msg = verify_login(lu, lp)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.logged_user = lu.strip()
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    auth_ui_center()
    st.stop()

# =========================
# SIDEBAR (POST-LOGIN)
# =========================
st.sidebar.success(f"Logged in as: {st.session_state.logged_user}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.logged_user = ""
    st.session_state.history = ""
    st.session_state.current_question = ""
    st.session_state.domain = ""
    st.session_state.resume_summary = ""
    st.session_state.resume_text = ""
    st.session_state.mcqs = []
    st.session_state.mcq_answers = {}
    st.session_state.skill_dist = []
    st.session_state.roadmap_text = ""
    st.session_state.assistive_mode = False
    st.session_state.assist_chat = []
    st.session_state.placement_mode = False
    st.session_state.linkedin_url = ""
    st.session_state.placement_jobs_ai = ""
    st.session_state.placement_jobs_search = ""
    st.session_state.placement_search_role = ""
    st.rerun()

# =========================
# SIDEBAR CONFIG
# =========================
st.sidebar.title("Configuration")
provider = st.sidebar.radio("Select AI Provider", ["Groq", "xAI (Grok)", "OpenAI (GPT)"])

if provider == "xAI (Grok)":
    api_key_label = "Enter xAI API Key (starts with 'xai-...')"
    provider_code = "xai"
elif provider == "Groq":
    api_key_label = "Enter Groq API Key (starts with 'gsk_...')"
    provider_code = "groq"
else:
    api_key_label = "Enter OpenAI API Key (starts with 'sk-...')"
    provider_code = "openai"

api_key = st.sidebar.text_input(api_key_label, type="password")
if api_key:
    api_key = api_key.strip()

st.sidebar.markdown("---")
st.sidebar.info(
    "**Privacy Note**: \n"
    "1. **Extraction**: Happens LOCALLY on your machine using Tesseract/PDFPlumber.\n"
    "2. **Analysis**: Extracted text is sent to the selected AI provider (Groq, xAI, or OpenAI) for processing."
)

# =========================
# Sidebar: Assistive + Placement buttons
# =========================
st.sidebar.markdown("---")
st.sidebar.subheader("Assistive Mode")
st.sidebar.caption("Ask questions and get help while learning (like a built-in tutor).")
if st.sidebar.button("Enter Assistive Mode", use_container_width=True, disabled=(not bool(api_key))):
    st.session_state.assistive_mode = True
    st.session_state.placement_mode = False
    if not st.session_state.assist_chat:
        st.session_state.assist_chat = [{"role": "assistant", "content": "Assistive mode is enabled. Ask what you want to learn and I will teach step-by-step."}]
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Placement / Job Links")
st.sidebar.caption("Job suggestions + employability search list.")
if st.sidebar.button("Open Placement Mode", use_container_width=True, disabled=(not bool(api_key))):
    st.session_state.placement_mode = True
    st.session_state.assistive_mode = False
    st.rerun()

# =========================
# Skill chart helper
# =========================
def render_skill_pie(skill_dist):
    fig = px.pie(skill_dist, names="skill", values="weight", hole=0.55, hover_data=["category", "weight"])
    fig.update_traces(textposition="inside", textinfo="percent")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=460)
    st.plotly_chart(fig, use_container_width=True)

# =========================
# Assistive Mode helpers
# =========================
_LINK_INTENT_RE = re.compile(r"\b(link|links|resource|resources|youtube|video|docs|documentation|official)\b", re.IGNORECASE)
def user_wants_links(text: str) -> bool:
    return bool(_LINK_INTENT_RE.search(text or ""))

def strip_urls(text: str) -> str:
    if not text:
        return text
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

def assistive_mode_ui(ai: AIClient):
    st.markdown("## Assistive Mode")
    st.caption("Context-aware help using your resume/domain/roadmap when available.")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Exit Assistive Mode", use_container_width=True):
            st.session_state.assistive_mode = False
            st.rerun()
    with c2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.assist_chat = [{"role": "assistant", "content": "Chat cleared. Tell me what you want to learn and I will teach step-by-step."}]
            st.rerun()

    for m in st.session_state.assist_chat:
        with st.chat_message("assistant" if m["role"] == "assistant" else "user"):
            st.markdown(m["content"])

    user_msg = st.chat_input("Ask anything about your roadmap, concepts, projects, interview prep...")
    if user_msg:
        st.session_state.assist_chat.append({"role": "user", "content": user_msg})
        allow_links = user_wants_links(user_msg)
        ctx = {"domain": st.session_state.domain, "resume_summary": st.session_state.resume_summary, "roadmap_text": st.session_state.roadmap_text}
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = ai.assistive_tutor(
                    user_message=user_msg,
                    context=ctx,
                    chat_history=st.session_state.assist_chat,
                    allow_links=allow_links
                )
                if not allow_links:
                    reply = strip_urls(reply)
                st.markdown(reply)
        st.session_state.assist_chat.append({"role": "assistant", "content": reply})
        st.rerun()

# =========================
# Placement Mode UI
# =========================
def placement_mode_ui(ai: AIClient):
    st.markdown("## Placement Mode")
    st.caption("Connect LinkedIn (optional) + generate job suggestions.")

    top1, top2 = st.columns([1, 1])
    with top1:
        if st.button("Exit Placement Mode", use_container_width=True):
            st.session_state.placement_mode = False
            st.rerun()
    with top2:
        if st.button("Clear Placement Results", use_container_width=True):
            st.session_state.placement_jobs_ai = ""
            st.session_state.placement_jobs_search = ""
            st.rerun()

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("LinkedIn (optional)")
    st.caption("Paste your LinkedIn profile URL to personalize suggestions.")
    linkedin_raw = st.text_input(
        "LinkedIn Profile URL",
        value=st.session_state.linkedin_url,
        placeholder="https://www.linkedin.com/in/your-profile"
    ).strip()

    if linkedin_raw and not linkedin_raw.startswith(("http://", "https://")):
        linkedin_raw = "https://" + linkedin_raw

    st.session_state.linkedin_url = linkedin_raw
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("Target Domain (required)")
    st.session_state.domain = st.text_input(
        "Enter your target domain for job suggestions",
        value=st.session_state.domain,
        placeholder="e.g., Data Scientist / Python Developer / RTL Design Engineer"
    ).strip()
    st.markdown("</div>", unsafe_allow_html=True)

    resume_for_jobs = ""
    if st.session_state.resume_text and len(st.session_state.resume_text) > 50:
        resume_for_jobs = st.session_state.resume_text
    elif st.session_state.resume_summary and len(st.session_state.resume_summary) > 50:
        resume_for_jobs = st.session_state.resume_summary

    can_generate = bool(st.session_state.domain) and bool(resume_for_jobs)

    st.write("")
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("A) AI Suggested Jobs (Resume + Target Domain)")
    st.caption("Generates job titles + skills gap + keywords to search.")

    if st.button("Generate AI Job Suggestions", use_container_width=True, disabled=not can_generate):
        with st.spinner("Generating suggestions..."):
            st.session_state.placement_jobs_ai = ai.generate_job_suggestions(
                resume_text=resume_for_jobs,
                domain=st.session_state.domain,
                linkedin_url=st.session_state.linkedin_url
            )

    if not can_generate:
        st.caption("To enable: analyze a resume (or have resume summary available) AND enter a target domain.")

    if st.session_state.placement_jobs_ai:
        st.markdown(st.session_state.placement_jobs_ai)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("B) Employability Search List (Search Queries + Filters)")
    st.caption("Builds search queries and filters for job portals.")

    st.session_state.placement_search_role = st.text_input(
        "Job Role to Search (required for B)",
        value=st.session_state.placement_search_role,
        placeholder="e.g., FPGA Engineer / Data Analyst / Embedded Developer"
    ).strip()

    location = st.text_input("Preferred Location (optional)", placeholder="Chennai / Bangalore / Remote").strip()
    exp = st.text_input("Experience Level (optional)", placeholder="Fresher / 1-3 yrs / 3-5 yrs").strip()

    can_generate_b = can_generate and bool(st.session_state.placement_search_role)

    if st.button("Generate Search-based Job List", use_container_width=True, disabled=not can_generate_b):
        with st.spinner("Building search list..."):
            st.session_state.placement_jobs_search = ai.generate_employability_search_list(
                resume_text=resume_for_jobs,
                domain=st.session_state.domain,
                location=location,
                experience_level=exp,
                search_role=st.session_state.placement_search_role
            )

    if not can_generate_b:
        st.caption("To enable B: ensure resume + domain are available AND enter 'Job Role to Search'.")

    if st.session_state.placement_jobs_search:
        st.markdown(st.session_state.placement_jobs_search)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# MAIN APP
# =========================
def main():
    if not api_key:
        st.warning(f"Please enter your {provider} API Key in the sidebar to proceed.")
        return

    try:
        ai = AIClient(api_key, provider=provider_code)
    except Exception as e:
        st.error(f"Error initializing AI Client: {e}")
        return

    if st.session_state.assistive_mode:
        assistive_mode_ui(ai)
        return
    if st.session_state.placement_mode:
        placement_mode_ui(ai)
        return

    st.header("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload PDF or Image", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        if st.button("Analyze Resume"):
            with st.spinner("Extracting text and analyzing..."):
                file_text = parse_resume(uploaded_file)

                if len(file_text) < 50:
                    st.error("Could not extract sufficient text. Try a clearer image or text-based PDF.")
                else:
                    try:
                        st.success("Resume Parsed Successfully!")
                        st.session_state.resume_text = file_text

                        analysis = ai.analyze_resume(file_text)
                        st.markdown(analysis)

                        st.session_state.resume_summary = analysis

                        with st.spinner("Generating skill chart..."):
                            st.session_state.skill_dist = ai.generate_skill_distribution(resume_text=file_text, max_skills=10)

                        st.info("Based on the analysis, please confirm your target domain below.")
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

    if st.session_state.skill_dist:
        st.subheader("Skill Distribution (from Resume)")
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        render_skill_pie(st.session_state.skill_dist)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.header("2. Domain & Interview")

    st.session_state.domain = st.text_input("Target Domain (e.g., Python Developer, Data Scientist)", value=st.session_state.domain)

    st.subheader("MCQ Test (Generated from Resume + Domain)")
    if st.session_state.domain and st.session_state.resume_text:
        col1, col2 = st.columns([1, 1])
        with col1:
            num_q = st.number_input("Number of MCQs", min_value=5, max_value=20, value=8, step=1)
        with col2:
            if st.button("Generate MCQ Test"):
                with st.spinner("Generating MCQs..."):
                    try:
                        st.session_state.mcqs = ai.generate_mcqs(st.session_state.domain, st.session_state.resume_text, num_questions=int(num_q))
                        st.session_state.mcq_answers = {}
                        st.success("MCQs generated. Answer and submit below.")
                    except Exception as e:
                        st.error(f"MCQ generation failed: {e}")

        if st.session_state.mcqs:
            st.write("### Answer the MCQs (answers are hidden until submission)")
            for i, q in enumerate(st.session_state.mcqs):
                st.markdown(f"**Q{i+1}. {q.get('question','')}**")
                opts = q.get("options", [])
                if not isinstance(opts, list) or len(opts) != 4:
                    st.error("Invalid MCQ format received (options must be 4). Regenerate.")
                    break

                selected = st.radio(
                    label=f"Select an option for Q{i+1}",
                    options=list(range(4)),
                    format_func=lambda idx: opts[idx],
                    index=st.session_state.mcq_answers.get(i, 0),
                    key=f"mcq_{i}"
                )
                st.session_state.mcq_answers[i] = int(selected)

            if st.button("Submit MCQ Test"):
                correct = 0
                results = []
                for i, q in enumerate(st.session_state.mcqs):
                    ans_idx = int(q.get("answer_index", -1))
                    user_idx = int(st.session_state.mcq_answers.get(i, -1))
                    is_correct = (user_idx == ans_idx)
                    if is_correct:
                        correct += 1
                    results.append((i, is_correct, user_idx, ans_idx, q.get("explanation", "")))

                total = len(st.session_state.mcqs)
                st.markdown(f"## Score: {correct}/{total}")
                st.write("### Review")
                for (i, is_correct, user_idx, ans_idx, expl) in results:
                    q = st.session_state.mcqs[i]
                    opts = q.get("options", [])
                    st.markdown(f"**Q{i+1}. {q.get('question','')}**")
                    st.write(f"Your answer: {opts[user_idx] if 0 <= user_idx < 4 else 'N/A'}")
                    st.write(f"Correct answer: {opts[ans_idx] if 0 <= ans_idx < 4 else 'N/A'}")
                    st.write(f"Explanation: {expl}")
                    st.markdown("---")
    else:
        st.caption("Upload and analyze a resume (Step 1) and enter a domain to generate MCQs.")

    if st.session_state.domain:
        if st.button("Start Interview / Next Question"):
            with st.spinner("Thinking..."):
                question = ai.generate_interview_question(st.session_state.domain, st.session_state.history)
                st.session_state.current_question = question

        if st.session_state.current_question:
            st.subheader("Question:")
            st.info(st.session_state.current_question)
            answer = st.text_area("Your Answer:")
            if st.button("Submit Answer"):
                with st.spinner("Evaluating..."):
                    feedback = ai.evaluate_answer(st.session_state.current_question, answer, st.session_state.domain)
                    st.write("### Feedback:")
                    st.write(feedback)
                    st.session_state.history += f"\nQ: {st.session_state.current_question}\nA: {answer}\nFeedback: {feedback}\n"
                    st.session_state.current_question = ""
                    st.success("Answer recorded. Click 'Start Interview / Next Question' to continue.")

    st.divider()
    st.header("3. Generate Roadmap")

    if st.session_state.domain and st.session_state.resume_summary:
        if st.button("Generate Career Roadmap"):
            with st.spinner("Creating roadmap..."):
                roadmap = ai.generate_roadmap(st.session_state.domain, st.session_state.resume_summary)
                st.session_state.roadmap_text = roadmap
                st.markdown("### Your Personalized Roadmap")
                st.markdown(roadmap)

        if st.session_state.roadmap_text:
            st.write("")
            if st.button("Enter Assistive Mode (Tutor)", use_container_width=True):
                st.session_state.assistive_mode = True
                st.session_state.placement_mode = False
                if not st.session_state.assist_chat:
                    st.session_state.assist_chat = [{"role": "assistant", "content": "Tutor mode enabled. Tell me which week/topic you want, and I will teach step-by-step."}]
                st.rerun()
    else:
        st.caption("Complete the previous steps to generate a roadmap.")

if __name__ == "__main__":
    main()
