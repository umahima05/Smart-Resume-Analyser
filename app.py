"""
app.py — Smart Resume Analyser
================================
UI built with Streamlit — Sky Blue & White Clean Minimal Theme
PDF text extraction using PyPDF2.
Analysis using analyser.py (pure Python logic).

Run with:  streamlit run app.py
"""

import streamlit as st
import PyPDF2
import io
from analyser import ResumeAnalyser, JOB_PROFILES

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Resume Analyser",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# CUSTOM CSS — Sky Blue & White Theme
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Page background ── */
    .stApp {
        background-color: #F0F4FF;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a237e 0%, #283593 60%, #3949ab 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e8eaf6 !important;
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #5c6bc0 !important;
    }

    /* ── Main title ── */
    .main-title {
        font-size: 2.6rem;
        font-weight: 900;
        color: #1a237e;
        letter-spacing: -1px;
        margin-bottom: 0.2rem;
    }
    .main-title span { color: #4361ee; }
    .subtitle {
        color: #5c6bc0;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* ── Score box ── */
    .score-box {
        background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
        border-radius: 20px;
        padding: 2rem 1.5rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 24px rgba(67,97,238,0.35);
    }
    .score-label {
        font-size: 0.8rem; color: #c5cae9;
        letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 0.4rem;
    }
    .score-num {
        font-size: 5rem; font-weight: 900; color: #ffffff; line-height: 1;
    }
    .score-denom { font-size: 0.85rem; color: #90caf9; margin-top: 0.2rem; }
    .grade-badge {
        display: inline-block;
        background: rgba(255,255,255,0.18);
        border: 1.5px solid rgba(255,255,255,0.35);
        color: #ffffff; font-size: 1rem; font-weight: 700;
        padding: 5px 20px; border-radius: 30px; margin-top: 0.75rem;
    }
    .score-meta { font-size: 0.78rem; color: #90caf9; margin-top: 0.6rem; }

    /* ── Skill tags ── */
    .skill-found {
        display: inline-block; background: #e8f5e9; color: #1b5e20;
        padding: 5px 13px; border-radius: 20px; font-size: 13px;
        margin: 3px; border: 1px solid #a5d6a7; font-weight: 500;
    }
    .skill-miss {
        display: inline-block; background: #ffebee; color: #b71c1c;
        padding: 5px 13px; border-radius: 20px; font-size: 13px;
        margin: 3px; border: 1px solid #ef9a9a; font-weight: 500;
    }
    .skill-bonus {
        display: inline-block; background: #e3f2fd; color: #0d47a1;
        padding: 5px 13px; border-radius: 20px; font-size: 13px;
        margin: 3px; border: 1px solid #90caf9; font-weight: 500;
    }

    /* ── Section badges ── */
    .section-yes {
        display: inline-block; background: #e8f5e9; color: #1b5e20;
        padding: 6px 16px; border-radius: 10px; font-size: 13px;
        font-weight: 600; border: 1px solid #a5d6a7; margin: 3px 0;
    }
    .section-no {
        display: inline-block; background: #ffebee; color: #b71c1c;
        padding: 6px 16px; border-radius: 10px; font-size: 13px;
        font-weight: 600; border: 1px solid #ef9a9a; margin: 3px 0;
    }

    /* ── Progress bars ── */
    .stProgress > div > div {
        background: linear-gradient(90deg, #4361ee, #7209b7) !important;
        border-radius: 10px !important;
    }
    .stProgress > div {
        background: #e8eaf6 !important; border-radius: 10px !important;
    }

    /* ── Button ── */
    .stButton > button {
        background: linear-gradient(135deg, #4361ee, #3a0ca3) !important;
        color: white !important; border: none !important;
        border-radius: 12px !important; padding: 0.65rem 2rem !important;
        font-size: 1rem !important; font-weight: 700 !important;
        width: 100% !important; box-shadow: 0 4px 15px rgba(67,97,238,0.35) !important;
    }
    .stButton > button:hover { opacity: 0.9 !important; }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: #ffffff !important;
        border: 2px dashed #90caf9 !important;
        border-radius: 14px !important;
    }
    [data-testid="stFileUploader"] * {
        color: #1a237e !important;
    }
    [data-testid="stFileUploader"] section {
        background: #e8f0fe !important;
        border: none !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploader"] section > div {
        background: #e8f0fe !important;
        color: #1a237e !important;
    }
    [data-testid="stFileUploader"] button {
        background: #4361ee !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] div {
        color: #1a237e !important;
        font-weight: 500 !important;
    }
    [data-testid="stFileUploaderFileName"] {
        color: #1a237e !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }
    [data-testid="stFileUploaderFileData"] {
        background: #f0f4ff !important;
        border: 1px solid #c5cae9 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetric"] {
        background: #ffffff; border: 1.5px solid #c5cae9;
        border-radius: 12px; padding: 0.75rem 1rem;
        box-shadow: 0 2px 8px rgba(67,97,238,0.06);
    }
    [data-testid="stMetricLabel"] { color: #3949ab !important; font-weight: 600 !important; }
    [data-testid="stMetricValue"] { color: #1a237e !important; font-weight: 800 !important; }

    /* ── Headings ── */
    h3 { color: #1a237e !important; font-weight: 800 !important; }
    h4 { color: #283593 !important; font-weight: 700 !important; }

    /* ── Keyword tag ── */
    .kw-tag {
        display: inline-block; background: #e8eaf6; color: #283593;
        padding: 4px 12px; border-radius: 20px; font-size: 13px;
        margin: 3px; border: 1px solid #c5cae9; font-weight: 500;
    }

    /* ── Feature cards ── */
    .feature-card {
        background: #ffffff; border: 1.5px solid #c5cae9;
        border-radius: 16px; padding: 1.5rem; text-align: center;
        box-shadow: 0 2px 12px rgba(67,97,238,0.07);
    }
    .feature-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .feature-title { font-size: 1rem; font-weight: 700; color: #1a237e; margin-bottom: 0.3rem; }
    .feature-desc { font-size: 0.85rem; color: #5c6bc0; }

    .contact-yes { color: #2e7d32; font-weight: 600; font-size: 14px; }
    .contact-no  { color: #c62828; font-weight: 600; font-size: 14px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# HELPER: Extract text from PDF
# ─────────────────────────────────────────────────────────
def extract_text_from_pdf(uploaded_file) -> str:
    text = ""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        st.error(f"Could not read PDF: {e}")
    return text.strip()


# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    selected_role = st.selectbox(
        "🎯 Target Job Role",
        list(JOB_PROFILES.keys()),
        help="Select the role you are applying for."
    )
    st.divider()
    st.markdown("### 📊 Score Weights")
    st.markdown("""
| Component       | Max |
|-----------------|-----|
| Skills Match    | 40  |
| Sections        | 25  |
| Content Quality | 20  |
| Contact Info    | 10  |
| Length          | 5   |
    """)
    st.divider()
    st.markdown("### 🎓 Grade Scale")
    st.markdown("""
| Score    | Grade |
|----------|-------|
| 85+      | A 🟢  |
| 70–84    | B 🔵  |
| 55–69    | C 🟡  |
| 40–54    | D 🟠  |
| Below 40 | F 🔴  |
    """)
    st.divider()
    st.markdown("""
    <div style='color:#9fa8da;font-size:0.78rem;text-align:center'>
    Smart Resume Analyser<br>Minor Project
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="main-title">📄 Smart <span>Resume</span> Analyser</div>
<div class="subtitle">Upload your resume PDF · Get instant score · Skill gap analysis · Actionable feedback</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────────────────────
up_col, btn_col = st.columns([3, 1])
with up_col:
    uploaded_file = st.file_uploader(
        "📂 Upload Resume (PDF only)",
        type=["pdf"],
        help="Upload a text-based PDF for best results."
    )
with btn_col:
    st.markdown("<br>", unsafe_allow_html=True)
    analyse_btn = st.button("🔍 Analyse Resume")


# ─────────────────────────────────────────────────────────
# ANALYSIS RESULTS
# ─────────────────────────────────────────────────────────
if analyse_btn:
    if not uploaded_file:
        st.warning("⚠️ Please upload a PDF resume first.")
        st.stop()

    with st.spinner("📖 Extracting text from PDF..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    if len(resume_text) < 50:
        st.error("❌ Could not extract enough text. Please use a text-based PDF, not a scanned image.")
        st.stop()

    with st.spinner("🔎 Analysing your resume..."):
        analyser = ResumeAnalyser(resume_text, selected_role)
        result   = analyser.run()

    scores   = result["scores"]
    skills   = result["skills"]
    sections = result["sections"]
    contact  = result["contact"]
    content  = result["content"]
    feedback = result["feedback"]
    keywords = result["keywords"]

    st.markdown("""
    <div style="
        background:#e8f5e9; border:1.5px solid #2e7d32;
        border-left:6px solid #2e7d32; border-radius:14px;
        padding:16px 22px; display:flex; align-items:center; gap:14px; margin-bottom:1rem;
    ">
        <span style="font-size:1.5rem">✅</span>
        <span style="color:#1b5e20; font-size:15px; font-weight:700;">
            Analysis complete! Scroll down to see your results.
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # ── SCORE + BREAKDOWN ────────────────────────────────
    grade_emoji = {"A":"🟢","B":"🔵","C":"🟡","D":"🟠","F":"🔴"}.get(scores["grade"],"")
    sc_col, bk_col = st.columns([1, 2])

    with sc_col:
        st.markdown(f"""
        <div class="score-box">
            <div class="score-label">Overall Score</div>
            <div class="score-num">{scores["total"]}</div>
            <div class="score-denom">out of 100</div>
            <div class="grade-badge">{grade_emoji} Grade {scores["grade"]}</div>
            <div class="score-meta">{result['word_count']} words &nbsp;·&nbsp; {selected_role}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📞 Contact Info")
        for item, found in contact.items():
            if found:
                st.markdown(f'<div class="contact-yes">✅ &nbsp;{item}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="contact-no">❌ &nbsp;{item}</div>', unsafe_allow_html=True)

    with bk_col:
        st.markdown("#### 📊 Score Breakdown")
        for label, val in scores["breakdown"].items():
            pct = int(val["score"] / val["max"] * 100)
            ca, cb = st.columns([3, 1])
            with ca:
                st.markdown(f"<span style='color:#1a237e;font-weight:600;font-size:14px'>{label}</span>", unsafe_allow_html=True)
            with cb:
                st.markdown(f"<span style='color:#4361ee;font-weight:700;font-size:14px'>{val['score']}/{val['max']}</span>", unsafe_allow_html=True)
            st.progress(pct / 100)
            st.markdown("")

    st.markdown("---")

    # ── SKILLS ───────────────────────────────────────────
    st.markdown("### 🛠️ Skills Analysis")
    st.markdown(f"<span style='color:#1a237e;font-weight:700;font-size:15px'>Match: {skills['match_pct']}% &nbsp;({len(skills['found_required'])}/{skills['total_required']} required skills found)</span>", unsafe_allow_html=True)
    st.progress(skills["match_pct"] / 100)
    st.markdown("<br>", unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown("<div style='color:#1b5e20;font-weight:700;font-size:14px;margin-bottom:8px'>✅ Found Skills</div>", unsafe_allow_html=True)
        if skills["found_required"]:
            st.markdown(" ".join(f'<span class="skill-found">✓ {s}</span>' for s in skills["found_required"]), unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#888'>None found</span>", unsafe_allow_html=True)

    with s2:
        st.markdown("<div style='color:#b71c1c;font-weight:700;font-size:14px;margin-bottom:8px'>❌ Missing Skills</div>", unsafe_allow_html=True)
        if skills["missing_required"]:
            st.markdown(" ".join(f'<span class="skill-miss">✗ {s}</span>' for s in skills["missing_required"]), unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#2e7d32;font-weight:600'>None missing — great!</span>", unsafe_allow_html=True)

    with s3:
        st.markdown("<div style='color:#0d47a1;font-weight:700;font-size:14px;margin-bottom:8px'>⭐ Bonus Skills</div>", unsafe_allow_html=True)
        if skills["found_bonus"]:
            st.markdown(" ".join(f'<span class="skill-bonus">+ {s}</span>' for s in skills["found_bonus"]), unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#888'>No bonus skills found</span>", unsafe_allow_html=True)

    st.markdown("---")

    # ── SECTIONS + CONTENT ───────────────────────────────
    sec_col, con_col = st.columns(2)

    with sec_col:
        st.markdown("### 📋 Resume Sections")
        for sec, found in sections.items():
            cls = "section-yes" if found else "section-no"
            icon = "✓" if found else "✗"
            st.markdown(f'<div style="margin:5px 0"><span class="{cls}">{icon} &nbsp;{sec}</span></div>', unsafe_allow_html=True)

    with con_col:
        st.markdown("### ✍️ Content Quality")
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Action Verbs",  len(content["impact_verbs"]))
        with m2: st.metric("Quantified",    content["quantifications"])
        with m3: st.metric("Weak Phrases",  len(content["weak_phrases"]))
        st.markdown("<br>", unsafe_allow_html=True)
        if content["impact_verbs"]:
            st.markdown("<span style='color:#1a237e;font-weight:600;font-size:13px'>Action verbs found:</span>", unsafe_allow_html=True)
            st.markdown(" ".join(f"`{v}`" for v in content["impact_verbs"]))
        if content["weak_phrases"]:
            st.markdown("<span style='color:#b71c1c;font-weight:600;font-size:13px'>Weak phrases detected:</span>", unsafe_allow_html=True)
            st.markdown(" ".join(f"`{p}`" for p in content["weak_phrases"]))

    st.markdown("---")

    # ── FEEDBACK ─────────────────────────────────────────
    st.markdown("### 💡 Feedback & Suggestions")

    FEEDBACK_STYLES = {
        "Critical": {
            "bg": "#fff0f0", "border": "#e53935", "left": "#e53935",
            "badge_bg": "#e53935", "badge_color": "#ffffff",
            "text": "#7f0000", "icon": "🔴"
        },
        "Warning": {
            "bg": "#fffbf0", "border": "#f9a825", "left": "#f9a825",
            "badge_bg": "#f9a825", "badge_color": "#ffffff",
            "text": "#5f3800", "icon": "🟡"
        },
        "Good": {
            "bg": "#f0fff4", "border": "#2e7d32", "left": "#2e7d32",
            "badge_bg": "#2e7d32", "badge_color": "#ffffff",
            "text": "#1b3a1f", "icon": "🟢"
        },
        "Tip": {
            "bg": "#f0f4ff", "border": "#1565c0", "left": "#1565c0",
            "badge_bg": "#1565c0", "badge_color": "#ffffff",
            "text": "#0d2a6e", "icon": "🔵"
        },
    }

    for tip_type, tip_msg in feedback:
        key = "Critical" if "Critical" in tip_type else \
              "Warning"  if "Warning"  in tip_type else \
              "Good"     if "Good"     in tip_type else "Tip"
        s = FEEDBACK_STYLES[key]
        label = tip_type.replace("🔴 ","").replace("🟡 ","").replace("🟢 ","").replace("🔵 ","")
        st.markdown(f"""
        <div style="
            background:{s['bg']};
            border:1.5px solid {s['border']};
            border-left:5px solid {s['left']};
            border-radius:12px;
            padding:14px 18px;
            margin-bottom:10px;
            display:flex;
            align-items:flex-start;
            gap:14px;
        ">
            <span style="font-size:1.3rem;margin-top:1px">{s['icon']}</span>
            <div>
                <span style="
                    background:{s['badge_bg']};
                    color:{s['badge_color']};
                    font-size:11px;font-weight:700;
                    padding:2px 10px;border-radius:20px;
                    letter-spacing:0.8px;text-transform:uppercase;
                    display:inline-block;margin-bottom:5px;
                ">{label}</span>
                <div style="color:{s['text']};font-size:14px;font-weight:600;line-height:1.6">
                    {tip_msg}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── KEYWORDS + TEXT ───────────────────────────────────
    kw_col, txt_col = st.columns([1, 2])
    with kw_col:
        st.markdown("### 🔑 Top Keywords")
        st.markdown(
            " ".join(f'<span class="kw-tag">{w} <b style="color:#4361ee">{c}x</b></span>' for w, c in keywords),
            unsafe_allow_html=True
        )
    with txt_col:
        st.markdown("### 📝 Extracted Text")
        with st.expander("Click to view extracted text from PDF"):
            st.text_area("", resume_text, height=220, disabled=True)

    st.markdown("---")
    st.markdown("<div style='text-align:center;color:#9fa8da;font-size:0.82rem'>Smart Resume Analyser · Minor Project · Built with Python & Streamlit</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# LANDING STATE
# ─────────────────────────────────────────────────────────
else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="
        background: #e8f0fe;
        border: 1.5px solid #4361ee;
        border-left: 6px solid #4361ee;
        border-radius: 14px;
        padding: 18px 22px;
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 1rem;
    ">
        <span style="font-size:1.8rem">&#128070;</span>
        <span style="color:#1a237e; font-size:15px; font-weight:600; line-height:1.6;">
            Upload your resume PDF, select a job role from the sidebar, and click
            <span style="color:#4361ee; font-weight:800;">Analyse Resume</span> to get started.
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    cards = [
        ("📤", "Upload PDF",       "Upload your resume as a PDF. Text is extracted automatically using PyPDF2."),
        ("🔍", "Instant Analysis", "Skills matched, sections detected, content quality evaluated — all in seconds."),
        ("📊", "Score & Feedback", "See your score, grade, missing skills, and tips to improve your resume."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], cards):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;color:#9fa8da;font-size:0.82rem'>Smart Resume Analyser · Minor Project · Built with Python & Streamlit</div>", unsafe_allow_html=True)
