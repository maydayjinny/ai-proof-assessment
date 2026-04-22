import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ── Page config ──────────────────────────────────────
st.set_page_config(
    page_title="AI-Resistant Assessment Generator",
    page_icon="🎓",
    layout="wide",
)

# ── Session state init ───────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "input"
if "results" not in st.session_state:
    st.session_state.results = None
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

# ── Custom CSS ───────────────────────────────────────
# FIX #3: Increased base font-size from 16px → 18.4px (×1.15)
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Source+Sans+3:wght@300;400;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    font-size: 18.4px; /* +15% from 16px */
  }

  /* Constrain wide layout to a comfortable reading width */
  .block-container {
    max-width: 860px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
  }

  /* ── Hero ── */
  .hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 20px;
    padding: 2.8rem 2.5rem 2.2rem 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
  }
  .hero h1 {
    font-family: 'Playfair Display', serif;
    color: #e2c97e;
    font-size: 2.2rem;
    margin-bottom: 0.6rem;
    line-height: 1.2;
  }
  .hero-intro {
    color: #c8d0e8;
    font-size: 1.08rem;
    line-height: 1.8;
    max-width: 640px;
    margin: 0 auto;
  }
  .hero-intro strong {
    color: #e2c97e;
  }

  /* ── Section headers ── */
  .section-header {
    font-family: 'Playfair Display', serif;
    color: #0f3460;
    font-size: 1.55rem;
    font-weight: 800;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.45rem;
    border-bottom: 2.5px solid #e2c97e;
    letter-spacing: -0.01em;
  }

  /* ── Required box: removed border/background to eliminate the blank box look ── */
  /* FIX #6: removed the border and background from required-box so no empty rounded box appears */
  .required-box {
    padding: 0;
    margin-bottom: 1.5rem;
    background: transparent;
    border: none;
  }

  /* FIX #7: Larger field labels */
  .field-label {
    font-size: 1.25rem;   /* was 1.08rem */
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0.15rem;
    margin-top: 1rem;
    letter-spacing: -0.01em;
  }
  .field-label:first-child {
    margin-top: 0;
  }
  .field-hint {
    color: #666;
    font-size: 0.92rem;
    margin-top: 0.15rem;
    margin-bottom: 0.6rem;
    font-style: italic;
    line-height: 1.5;
  }

  /* ── Output card ── */
  .output-card {
    background: #f8f7f4;
    border-left: 5px solid #e2c97e;
    border-radius: 0 16px 16px 0;
    padding: 1.6rem 1.8rem 1.4rem 1.8rem;
    margin-bottom: 1.8rem;
    box-shadow: 0 2px 12px rgba(15,52,96,0.07);
  }
  .output-card h3 {
    font-family: 'Playfair Display', serif;
    color: #0f3460;
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
  }
  .output-meta {
    font-size: 0.95rem;
    color: #444;
    margin-bottom: 0.4rem;
    line-height: 1.65;
  }

  /* FIX #4: Renamed strategy pill and restyled for faculty-friendly look */
  .ai-resistance-block {
    background: #fff8e6;
    border: 1.5px solid #e2c97e;
    border-radius: 10px;
    padding: 1rem 1.2rem 0.85rem 1.2rem;
    margin: 0.8rem 0 1rem 0;
  }
  .ai-resistance-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #7a6010;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
  }
  .ai-resistance-strategy {
    font-size: 1rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0.4rem;
  }
  .ai-resistance-explanation {
    font-size: 0.93rem;
    color: #555;
    line-height: 1.65;
  }

  .instructions-box {
    background: #fff;
    border: 1.5px solid #0f346025;
    border-top: 3px solid #0f3460;
    border-radius: 8px;
    padding: 1.3rem 1.6rem;
    margin-top: 1rem;
  }
  .inst-section-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #0f3460;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 1rem 0 0.35rem 0;
  }
  .inst-section-title:first-child {
    margin-top: 0;
  }
  .copy-label {
    background: #e2c97e;
    color: #1a1a2e;
    font-size: 0.74rem;
    font-weight: 700;
    padding: 0.22rem 0.7rem;
    border-radius: 4px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 0.9rem;
    display: inline-block;
  }
  .grading-tip {
    background: #f0f7ff;
    border-left: 3px solid #4a90d9;
    border-radius: 0 6px 6px 0;
    padding: 0.65rem 1rem;
    margin-top: 1rem;
    font-size: 0.93rem;
    color: #2c5282;
  }
  .option-tag {
    display: inline-block;
    background: #e2c97e22;
    color: #7a6010;
    border: 1px solid #e2c97e;
    border-radius: 20px;
    padding: 0.15rem 0.85rem;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 0.6rem;
  }
  .results-header {
    background: linear-gradient(135deg, #0f3460, #1a1a2e);
    border-radius: 14px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.8rem;
    text-align: center;
  }
  .results-header h2 {
    font-family: 'Playfair Display', serif;
    color: #e2c97e;
    margin: 0 0 0.3rem 0;
    font-size: 1.75rem;
  }
  .results-header p {
    color: #a8b2d8;
    margin: 0;
    font-size: 1rem;
  }

  /* Instruction list items */
  .inst-list li {
    margin-bottom: 0.55rem;
    line-height: 1.7;
    font-size: 0.97rem;
    color: #333;
  }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ════════════════════════════════════════════════════

# Strategy → faculty-friendly explanation mapping
STRATEGY_EXPLANATIONS = {
    "personal": (
        "Personal / Local Context",
        "This strategy requires students to draw on their own lived experiences, community, or real-time environment — material that is uniquely theirs and impossible for AI to generate authentically. It shifts the assessment from abstract knowledge recall to genuine personal synthesis, which is both harder to fake and more educationally meaningful."
    ),
    "process": (
        "Process Documentation",
        "By capturing a student's thinking over time through drafts, journals, or portfolios, this strategy makes the intellectual journey visible. AI can produce a polished endpoint, but it cannot fabricate the authentic messiness of real learning. Instructors can evaluate growth, revision, and metacognition — not just a final product."
    ),
    "oral": (
        "Oral / Live Component",
        "Live or recorded self-explanation forces students to demonstrate understanding in the moment, without a script they can hand off to AI. Spontaneous follow-up questions and real-time reasoning reveal depth (or its absence) in ways no written submission can match."
    ),
    "collaborative": (
        "Collaborative Accountability",
        "Peer critique and group work with individual deliverables create social accountability that AI cannot replicate. Students must respond to specific classmates' ideas and defend their own thinking in context — a layer of authenticity that requires genuine engagement."
    ),
    "dynamic": (
        "Unpredictable / Dynamic Prompts",
        "When prompts include real-time data, randomly assigned variables, or in-class reveals, AI cannot prepare a polished response in advance. This strategy turns the element of surprise into an assessment feature, rewarding adaptive thinking over rehearsed outputs."
    ),
}

def detect_strategy_key(strategy_text):
    """Map the model's strategy label to one of our explanation keys."""
    s = strategy_text.lower()
    if any(k in s for k in ["personal", "local", "community", "experience", "real-time"]):
        return "personal"
    if any(k in s for k in ["process", "portfolio", "draft", "journal", "reflection"]):
        return "process"
    if any(k in s for k in ["oral", "live", "viva", "presentation", "recorded"]):
        return "oral"
    if any(k in s for k in ["collaborat", "peer", "group"]):
        return "collaborative"
    if any(k in s for k in ["unpredictable", "dynamic", "random", "in-class", "reveal"]):
        return "dynamic"
    return None


def build_prompt(data):
    tools_str = ", ".join(data.get("available_tools", [])) or "Not specified"
    optional_lines = ""
    if data.get("num_students"):
        optional_lines += f"- Number of Students: {data['num_students']}\n"
    if data.get("grading_mode"):
        optional_lines += f"- Grading Mode: {data['grading_mode']}\n"
    if data.get("current_assessment"):
        optional_lines += f"\nCURRENT ASSESSMENT (what the professor currently uses):\n{data['current_assessment']}\n"
    if tools_str != "Not specified":
        optional_lines += f"\nALLOWED TOOLS FOR STUDENTS: {tools_str}\n"

    scope_line = ""
    if data.get("assessment_scope"):
        scope_line = f"- Assessment Scope and Time Investment: {data['assessment_scope']}\n"

    return f"""You are a leading expert in online higher education pedagogy and evidence-based assessment design.
A professor teaching a FULLY ONLINE course needs 3 creative, AI-resistant assessment alternatives.

REQUIRED COURSE INFORMATION:
- Subject / Topic: {data['subject']}
- Course Level: {data['level']}
- Course-Level Objectives: {data['learning_objectives']}
- Assessment Goals: {data['assessment_goal']}
{scope_line}{optional_lines}

CRITICAL CONSTRAINTS — every assessment MUST follow ALL of these:

1. ONLINE & ASYNCHRONOUS ONLY. No in-person meetings, no physical labs, no hybrid components. Every step must be completable from a student's home computer.

2. GENUINELY AI-RESISTANT. It must require something AI cannot fabricate: the student's own lived experience, their face/voice on camera, traceable peer responses to a specific classmate's real work, or a personalized prompt variable that is unique to each student.

3. DEEP COGNITIVE ENGAGEMENT. Target Bloom's upper levels: analysis, synthesis, evaluation, creation. No recall, no simple summary tasks.

4. COMPLETABLE WITH FREE TOOLS ONLY. When recommending specific tools, ONLY suggest tools that are 100% free for students with no paywall. Approved free tools include:
   - Video recording & sharing: Loom (free tier), YouTube (unlisted), Google Drive video upload, Zoom (record locally), OBS Studio
   - Audio: Audacity, Anchor (Spotify for Podcasters), SoundCloud (free tier)
   - Documents & collaboration: Google Docs, Google Slides, Google Jamboard, Padlet (free tier), Miro (free tier)
   - Discussion: course discussion board
   - Annotation: Hypothesis (free), Google Docs comments
   - Presentation: Google Slides, Canva (free tier)
   Do NOT mention Flip, VoiceThread, Adobe products, Kaltura, or any tool that requires institutional licensing or paid subscription.

5. NEVER USE THE TERM "LMS". Instead write "our course website", "the course discussion board", "the assignment submission page", or "our course platform" depending on context.

6. DETAILED AND SPECIFIC OUTPUT. Every field must be thorough and complete — not brief placeholders. Students reading the instructions should have zero ambiguity about what to do.

AI-RESISTANCE STRATEGIES (use a different one for each of the 3 assessments):
- Personal/authentic experience: student documents, analyzes, or reflects on their own real lived context — something AI cannot invent
- Process + evidence trail: multiple drafts, timestamped entries, or screen recordings that prove thinking happened over time
- Recorded self-explanation: video or audio where the student explains reasoning in their own unrepeatable voice/face
- Asynchronous peer accountability: structured peer review where each student's contribution responds to a specific peer's real work, making generic AI responses obvious
- Dynamic/personalized prompt: each student receives a unique variable (their own collected data, a randomly assigned case, a current event they must locate themselves) making identical AI outputs impossible

FORMAT — output EXACTLY this structure with EXACT labels. Do not add or remove any labels:

###ASSESSMENT_START###
TITLE: [Specific, engaging, course-relevant title — not generic]
TYPE: [e.g., Video Reflection / Annotated Portfolio / Peer Critique / Personalized Case Analysis]
AI-RESISTANCE STRATEGY: [Name the strategy in 3-6 words]
OVERVIEW FOR PROFESSOR: [3-4 sentences: what students do step by step, why it resists AI specifically, what cognitive skills it develops, and why it suits an online environment]
###STUDENT_INSTRUCTIONS_START###
PURPOSE: [Write 4-5 warm, motivating, learner-centered sentences addressed directly to the student. Start with "This assignment invites you to..." or "In this assignment, you will...". Explain (1) what skill or understanding they will build, (2) why it matters in their field or future career, (3) how this activity will concretely benefit them as a learner and professional. Be specific to the course subject — not generic. Make students feel genuinely excited and valued.]
OVERVIEW: [Write 3-4 sentences addressed directly to the student. Give a clear, concrete picture of exactly what this assignment involves: what they will create or produce, what intellectual task they are doing, what they will submit, and any key constraints like length or format. This should answer "what exactly am I doing and what do I turn in?" with zero ambiguity.]
STEP 1: [Full, friendly, detailed instruction. Include the specific action, any recommended free tool, approximate time or length, and what good looks like. Do not use fragments.]
STEP 2: [Equally detailed next action.]
STEP 3: [Equally detailed next action.]
STEP 4: [Equally detailed next action.]
STEP 5: [Final step — specify exactly what to submit, in what format, and where on the course website/platform to submit it.]
###STUDENT_INSTRUCTIONS_END###
GRADING TIP: [2-3 sentences: what to look for when grading, one signal that distinguishes genuine student work from AI-generated work, and one efficiency tip for grading at scale online]
###ASSESSMENT_END###

Generate exactly 3 assessments. Each must be substantially different in TYPE and STRATEGY.
Each PURPOSE must be 4-5 full sentences. Each OVERVIEW must be 3-4 full sentences. Each STEP must be a complete, detailed sentence.
Do not add any text outside the ### markers above."""


def parse_assessments(raw_text):
    """Split raw output into individual assessment blocks using ###ASSESSMENT_START### markers."""
    blocks = []
    parts = raw_text.split("###ASSESSMENT_START###")
    for part in parts[1:]:
        end_idx = part.find("###ASSESSMENT_END###")
        chunk = part[:end_idx].strip() if end_idx != -1 else part.strip()
        if chunk:
            blocks.append(chunk)
    return blocks


def extract_field(block, start_label, end_labels):
    """
    Extract content after 'start_label:' up to the first matching end_label.
    Handles both 'LABEL: inline text' and 'LABEL:\\nmultiline text' patterns.
    end_labels should be full label strings like 'FOCUS', 'STEP 1', etc.
    """
    # Try matching 'LABEL:' at start of a line or inline
    import re
    pattern = re.compile(r'(?:^|\n)' + re.escape(start_label) + r':\s*', re.IGNORECASE)
    m = pattern.search(block)
    if not m:
        return ""
    content_start = m.end()
    end_idx = len(block)
    for el in end_labels:
        ep = re.compile(r'\n' + re.escape(el) + r'[:\s]', re.IGNORECASE)
        em = ep.search(block, content_start)
        if em and em.start() < end_idx:
            end_idx = em.start()
    return block[content_start:end_idx].strip()


def extract_between(block, start_marker, end_marker):
    si = block.find(start_marker)
    ei = block.find(end_marker)
    if si == -1 or ei == -1:
        return ""
    return block[si + len(start_marker):ei].strip()


def extract_steps(block):
    """
    Extract all STEP N: lines from a block, returning a list of step text strings.
    Handles multi-line steps: content continues until the next STEP or end of block.
    """
    import re
    # Find all step positions
    step_pattern = re.compile(r'(?:^|\n)STEP\s*\d+\s*:\s*', re.IGNORECASE)
    matches = list(step_pattern.finditer(block))
    if not matches:
        # Fallback: try "Step N:" at start of lines
        step_pattern = re.compile(r'(?:^|\n)Step\s*\d+\s*:\s*', re.IGNORECASE)
        matches = list(step_pattern.finditer(block))
    steps = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(block)
        text = block[start:end].strip()
        # Remove trailing blank lines
        text = re.sub(r'\n\s*\n.*', '', text, flags=re.DOTALL).strip()
        if text:
            steps.append(text)
    return steps


def render_assessment(block, idx):
    title    = extract_field(block, "TITLE", ["TYPE", "AI-RESISTANCE"])
    atype    = extract_field(block, "TYPE", ["AI-RESISTANCE", "OVERVIEW"])
    strategy = extract_field(block, "AI-RESISTANCE STRATEGY", ["OVERVIEW FOR PROFESSOR", "###STUDENT"])
    overview = extract_field(block, "OVERVIEW FOR PROFESSOR", ["###STUDENT_INSTRUCTIONS_START###", "PURPOSE"])
    grading  = extract_field(block, "GRADING TIP", ["###ASSESSMENT_END###"])

    student_block = extract_between(block, "###STUDENT_INSTRUCTIONS_START###", "###STUDENT_INSTRUCTIONS_END###")

    purpose = extract_field(student_block, "PURPOSE", ["OVERVIEW", "FOCUS", "STEP 1", "STEP1"])
    overview_section = extract_field(student_block, "OVERVIEW", ["STEP 1", "STEP1", "INSTRUCTIONS"])
    # Fallback to FOCUS for backward compatibility
    if not overview_section:
        overview_section = extract_field(student_block, "FOCUS", ["STEP 1", "STEP1", "INSTRUCTIONS"])
    steps   = extract_steps(student_block)

    # Fallback: if student_block extraction failed, try from main block
    if not purpose:
        purpose = extract_field(block, "PURPOSE", ["OVERVIEW", "FOCUS", "STEP 1"])
    if not overview_section:
        overview_section = extract_field(block, "OVERVIEW", ["STEP 1", "INSTRUCTIONS"])
    if not steps:
        steps = extract_steps(block)

    # Build AI-resistance block
    strategy_key = detect_strategy_key(strategy)
    if strategy_key and strategy_key in STRATEGY_EXPLANATIONS:
        strategy_name, strategy_edu = STRATEGY_EXPLANATIONS[strategy_key]
    else:
        strategy_name = strategy.split(":")[0].strip() if ":" in strategy else strategy[:80]
        strategy_edu  = strategy

    # ── Card header ──
    st.markdown(f"""
    <div style="background:#f8f7f4; border-left:5px solid #e2c97e; border-radius:0 16px 16px 0;
                padding:1.6rem 1.8rem 0.8rem 1.8rem; margin-bottom:0;
                box-shadow:0 2px 12px rgba(15,52,96,0.07);">
      <span style="display:inline-block; background:#e2c97e22; color:#7a6010;
                   border:1px solid #e2c97e; border-radius:20px; padding:0.15rem 0.85rem;
                   font-size:0.82rem; font-weight:700; margin-bottom:0.6rem;">Option {idx}</span>
      <div style="font-family:'Playfair Display',serif; color:#0f3460; font-size:1.35rem;
                  font-weight:800; margin-bottom:0.4rem;">{title or f"Assessment Option {idx}"}</div>
      <div style="font-size:0.95rem; color:#444; margin-bottom:0.3rem; line-height:1.65;">
        <strong>Type:</strong> {atype}
      </div>
      <div style="font-size:0.95rem; color:#444; line-height:1.65; margin-bottom:0.6rem;">{overview}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── AI-resistance block ──
    st.markdown(f"""
    <div style="background:#fff8e6; border:1.5px solid #e2c97e;
                border-top:none; border-radius:0 0 10px 10px;
                padding:1rem 1.2rem 0.9rem 1.2rem; margin-bottom:0.7rem;
                box-shadow:0 2px 8px rgba(15,52,96,0.05);">
      <div style="font-size:0.78rem; font-weight:700; color:#7a6010; letter-spacing:0.09em;
                  text-transform:uppercase; margin-bottom:0.3rem;">🛡️ Why Is This AI-Resistant?</div>
      <div style="font-size:1rem; font-weight:700; color:#1a1a2e; margin-bottom:0.35rem;">
        Strategy: {strategy_name}
      </div>
      <div style="font-size:0.93rem; color:#555; line-height:1.65;">{strategy_edu}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sample Student Instructions box — ONE call, all content inline ──
    purpose_safe  = purpose.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    overview_safe = overview_section.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    steps_html   = "".join(
        f'<li style="margin-bottom:0.65rem; line-height:1.75; color:#222; font-size:1rem;">'
        f'{s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</li>'
        for s in steps
    )
    if not steps_html:
        steps_html = '<li style="color:#999;">Steps not generated — please regenerate.</li>'

    st.markdown(f"""
    <div style="background:#fff; border:1.5px solid rgba(15,52,96,0.15);
                border-top:3px solid #0f3460; border-radius:8px;
                padding:1.5rem 1.8rem 1.6rem 1.8rem; margin-bottom:0.7rem;">

      <div style="background:#e2c97e; color:#1a1a2e; font-size:0.78rem; font-weight:700;
                  padding:0.3rem 0.9rem; border-radius:5px; letter-spacing:0.06em;
                  text-transform:uppercase; margin-bottom:1.4rem; display:inline-block;">
        Sample Student Instructions
      </div>

      <div style="font-size:0.78rem; font-weight:700; color:#0f3460; letter-spacing:0.1em;
                  text-transform:uppercase; margin-bottom:0.45rem; margin-top:0.2rem;">Purpose</div>
      <p style="color:#222; font-size:1rem; line-height:1.8; margin:0 0 1.3rem 0;">{purpose_safe}</p>

      <div style="font-size:0.78rem; font-weight:700; color:#0f3460; letter-spacing:0.1em;
                  text-transform:uppercase; margin-bottom:0.45rem;">Overview</div>
      <p style="color:#222; font-size:1rem; line-height:1.8; margin:0 0 1.3rem 0;">{overview_safe}</p>

      <div style="font-size:0.78rem; font-weight:700; color:#0f3460; letter-spacing:0.1em;
                  text-transform:uppercase; margin-bottom:0.7rem;">Step-by-Step Instructions</div>
      <ol style="margin:0; padding-left:1.5rem; color:#222;">
        {steps_html}
      </ol>

    </div>
    """, unsafe_allow_html=True)

    # ── Grading tip ──
    st.markdown(f"""
    <div style="background:#f0f7ff; border-left:3px solid #4a90d9; border-radius:0 6px 6px 0;
                padding:0.7rem 1.1rem; margin-bottom:2.2rem;
                font-size:0.95rem; color:#2c5282; line-height:1.65;">
      <strong>💡 Grading Tip:</strong> {grading}
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════
#  PAGE: INPUT
# ════════════════════════════════════════════════════

def show_input_page():

    # Hero
    st.markdown("""
    <div class="hero">
      <h1>🎓 AI-Resistant Assessment Generator</h1>
      <div class="hero-intro">
        <p>
          You have probably felt it: the essay that sounds polished but hollow, the analysis
          that hits every talking point but reveals nothing about the student who "wrote" it.
          <strong>You are not imagining it.</strong>
        </p>
        <p>
          AI did not just change how students cheat. It exposed how many of our assessments
          were never really measuring thinking in the first place.
        </p>
        <p>
          This tool helps you rebuild. In under 2 minutes, describe your course and what you
          want students to <em>actually</em> demonstrate, and we will generate <strong>3 research-backed,
          AI-resistant assessment alternatives</strong>, each with ready-to-use student instructions
          you can copy straight into your syllabus.
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── REQUIRED FIELDS ──────────────────────────────
    st.markdown('<div class="section-header">Required Information</div>', unsafe_allow_html=True)

    # FIX #6: removed the wrapping required-box div (no more empty rounded box)

    # Subject
    st.markdown('<div class="field-label">Subject or Topic of the Course</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-hint">Describe the subject in plain language, not just a course code. For example, write "Introduction to Psychology" rather than "PSYC 101".</div>', unsafe_allow_html=True)
    subject = st.text_input(
        "subject_hidden",
        placeholder="e.g., Introduction to Sociology / Urban Planning and Sustainability / Business Ethics",
        label_visibility="collapsed"
    )

    # Course Level
    st.markdown('<div class="field-label">Course Level</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-hint">Select the level closest to your course. This shapes the cognitive complexity of the suggested assessments.</div>', unsafe_allow_html=True)
    level = st.selectbox(
        "level_hidden",
        ["Undergraduate: Introductory (100-200 level)",
         "Undergraduate: Intermediate (200-300 level)",
         "Undergraduate: Advanced (300-400 level)",
         "Graduate: Master's level",
         "Graduate: Doctoral level",
         "Professional / Executive Education"],
        label_visibility="collapsed"
    )

    # Course-Level Objectives
    st.markdown('<div class="field-label">Course-Level Objectives</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-hint">What should students know or be able to do by the end of the course? These are your Course LOs, not specific to any one assignment.</div>', unsafe_allow_html=True)
    learning_objectives = st.text_area(
        "lo_hidden",
        placeholder="e.g., Students will be able to identify and apply major sociological theories to analyze social institutions and everyday life...",
        height=110,
        label_visibility="collapsed"
    )

    # Assessment Goals
    st.markdown('<div class="field-label">Assessment Goals</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-hint">What do you want this specific assessment to measure or reveal? Focus on the skills and thinking you are trying to evaluate, not just the content topic.</div>', unsafe_allow_html=True)
    assessment_goal = st.text_area(
        "ag_hidden",
        placeholder="e.g., I want to assess whether students can apply theory to a real-world case they have not encountered before, not just recall definitions...",
        height=100,
        label_visibility="collapsed"
    )

    # Assessment Scope
    st.markdown('<div class="field-label">Assessment Scope and Time Investment</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-hint">How much time and weight should this assessment carry? Knowing this helps generate something appropriately sized for your course.</div>', unsafe_allow_html=True)
    assessment_scope = st.selectbox(
        "scope_hidden",
        [
            "Not sure yet / flexible",
            "Quick knowledge check (15-30 minutes, low stakes)",
            "Formative assessment (in-progress check, not heavily graded)",
            "Summative assessment (end-of-unit or final, heavily weighted)",
            "Major project (multi-week, high stakes)",
            "In-class activity (synchronous, 30-60 minutes)",
            "Take-home assignment (1-3 days to complete)",
        ],
        label_visibility="collapsed"
    )

    # ── OPTIONAL FIELDS ──────────────────────────────
    st.markdown('<div class="section-header">Optional: More Context</div>', unsafe_allow_html=True)
    st.markdown("These fields help tailor the output further, but are not required to generate results.", unsafe_allow_html=True)
    st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="field-label">Number of Students</div>', unsafe_allow_html=True)
        st.markdown('<div class="field-hint">Larger classes benefit from rubric-based or peer-reviewed formats.</div>', unsafe_allow_html=True)
        num_students = st.number_input(
            "ns_hidden",
            min_value=0, max_value=1000, value=0, step=1,
            label_visibility="collapsed"
        )

    with col2:
        st.markdown('<div class="field-label">Grading Mode</div>', unsafe_allow_html=True)
        st.markdown('<div class="field-hint">Individual vs. group work significantly changes which formats work best.</div>', unsafe_allow_html=True)
        grading_mode = st.selectbox(
            "gm_hidden",
            ["Not specified", "Individual", "Group", "Mix of Individual and Group"],
            label_visibility="collapsed"
        )

    st.markdown('<div class="field-label">Current Assessment You Want to Replace</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-hint">If you share what you currently use, the suggestions will be meaningfully different rather than just variations on the same format.</div>', unsafe_allow_html=True)
    current_assessment = st.text_area(
        "ca_hidden",
        placeholder="e.g., A 1,500-word essay where students pick a sociological concept and explain it with examples from a textbook chapter...",
        height=100,
        label_visibility="collapsed"
    )

    TOOL_OPTIONS = [
        "Internet Research (general)",
        "Academic Databases (e.g., JSTOR, PubMed)",
        "AI Writing Tools (e.g., ChatGPT, Claude)",
        "AI for brainstorming and outlining only",
        "Peer Discussion and Collaboration",
        "Physical Lab Equipment",
        "Field Observations and Site Visits",
        "Interviews with Real People",
        "Course Textbook and Lecture Notes Only",
        "Calculators and Statistical Software",
        "Design Tools (e.g., Canva, Figma)",
        "No restrictions: open book and open tool",
        "Strictly closed: no outside resources",
    ]

    st.markdown('<div class="field-label">Allowed Tools and Resources</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-hint">Select all tools students are permitted to use. If something is missing, add it in the field below.</div>', unsafe_allow_html=True)
    selected_tools = st.multiselect(
        "tools_hidden",
        TOOL_OPTIONS,
        default=[],
        label_visibility="collapsed"
    )

    st.markdown('<div class="field-label">Other Allowed Tool Not Listed Above</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-hint">Type in any tool not covered by the options above.</div>', unsafe_allow_html=True)
    custom_tool = st.text_input(
        "ct_hidden",
        placeholder="e.g., GIS software, a specific dataset, oral dictation tools...",
        label_visibility="collapsed"
    )

    all_tools = selected_tools + ([custom_tool.strip()] if custom_tool.strip() else [])

    # ── Generate Button ───────────────────────────────
    st.markdown("")
    generate_btn = st.button("✨  Generate 3 AI-Resistant Assessments", type="primary", use_container_width=True)

    if generate_btn:
        missing = []
        if not subject.strip():              missing.append("Subject or Topic")
        if not learning_objectives.strip():  missing.append("Course-Level Objectives")
        if not assessment_goal.strip():      missing.append("Assessment Goals")

        if missing:
            st.error(f"⚠️ Please fill in the required fields: **{', '.join(missing)}**")
        else:
            with st.spinner("Designing your assessments. This usually takes 20 to 40 seconds."):
                try:
                    form_data = {
                        "subject":             subject.strip(),
                        "level":               level,
                        "learning_objectives": learning_objectives.strip(),
                        "assessment_goal":     assessment_goal.strip(),
                        "assessment_scope":    assessment_scope,
                        "num_students":        num_students if num_students > 0 else None,
                        "grading_mode":        grading_mode if grading_mode != "Not specified" else None,
                        "current_assessment":  current_assessment.strip() or None,
                        "available_tools":     all_tools,
                    }
                    prompt = build_prompt(form_data)
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert higher education assessment designer who writes detailed, practical, ready-to-use assessment materials."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.82,
                        max_tokens=6000,
                    )
                    raw_output = response.choices[0].message.content
                    st.session_state.results   = raw_output
                    st.session_state.form_data = form_data
                    st.session_state.page      = "results"
                    st.rerun()

                except Exception as e:
                    err_msg = str(e)
                    if "api_key" in err_msg.lower() or "authentication" in err_msg.lower():
                        st.error("🔑 Invalid API key. Please check the OPENAI_API_KEY value at the top of streamlit_app.py.")
                    elif "quota" in err_msg.lower() or "billing" in err_msg.lower():
                        st.error("💳 OpenAI usage limit reached. Please check your OpenAI account billing.")
                    else:
                        st.error(f"❌ Something went wrong: {err_msg}")

    st.markdown("""
    <div style="text-align:center; color:#bbb; font-size:0.82rem; margin-top:3rem; padding-top:1rem; border-top:1px solid #eee;">
      AI-Resistant Assessment Generator · Powered by OpenAI GPT-3.5
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════
#  PAGE: RESULTS
# ════════════════════════════════════════════════════

def show_results_page():
    # Scroll to top when results page loads
    st.markdown("""
    <script>
        window.scrollTo(0, 0);
        // Also try via parent (Streamlit iframe)
        try { window.parent.scrollTo(0, 0); } catch(e) {}
    </script>
    """, unsafe_allow_html=True)

    fd = st.session_state.form_data
    st.markdown(f"""
    <div class="results-header">
      <h2>📚 Your 3 AI-Resistant Assessment Options</h2>
      <p>Generated for: <strong style="color:#e2c97e;">{fd.get('subject','')}</strong> &nbsp;·&nbsp; {fd.get('level','')}</p>
    </div>
    """, unsafe_allow_html=True)

    col_back, col_regen = st.columns(2)
    with col_back:
        if st.button("← Back to Form", use_container_width=True):
            st.session_state.page = "input"
            st.rerun()
    with col_regen:
        if st.button("🔄 Generate New Options (same inputs)", type="primary", use_container_width=True):
            with st.spinner("Generating new alternatives..."):
                try:
                    prompt = build_prompt(st.session_state.form_data)
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert higher education assessment designer who writes detailed, practical, ready-to-use assessment materials."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.95,
                        max_tokens=6000,
                    )
                    st.session_state.results = response.choices[0].message.content
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    st.markdown("Each option below includes **student-ready instructions** you can copy and paste directly into your syllabus or LMS.")
    st.markdown("")

    raw    = st.session_state.results
    blocks = parse_assessments(raw)

    if blocks:
        for i, block in enumerate(blocks[:3], 1):
            render_assessment(block, i)
    else:
        st.markdown(raw)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Form (edit inputs)", use_container_width=True):
            st.session_state.page = "input"
            st.rerun()
    with col2:
        if st.button("🔄 Regenerate New Options", type="primary", use_container_width=True):
            with st.spinner("Generating new alternatives..."):
                try:
                    prompt = build_prompt(st.session_state.form_data)
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert higher education assessment designer who writes detailed, practical, ready-to-use assessment materials."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.95,
                        max_tokens=6000,
                    )
                    st.session_state.results = response.choices[0].message.content
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    st.caption("Results are AI-generated suggestions. Please review and adapt to your course context and institutional policies.")
    st.markdown("""
    <div style="text-align:center; color:#bbb; font-size:0.82rem; margin-top:2rem; padding-top:1rem; border-top:1px solid #eee;">
      AI-Resistant Assessment Generator · Powered by OpenAI GPT-3.5
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════
#  ROUTER
# ════════════════════════════════════════════════════

if st.session_state.page == "input":
    show_input_page()
else:
    show_results_page()
