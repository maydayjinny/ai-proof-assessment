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

AI-RESISTANCE STRATEGIES — use a DIFFERENT strategy for each of the 3 assessments. Choose from the full menu below. Each strategy entry explains what it is, why it resists AI, and concrete design signals you must embed in the assessment.

════════════════════════════════════════════════════════════
CATEGORY A: PERSONAL CONTEXT AND LIVED EXPERIENCE
════════════════════════════════════════════════════════════

A1. PERSONAL AUTHENTIC NARRATIVE
   What it is: The student documents, analyzes, or reflects critically on something rooted in their own irreplaceable lived experience — a specific encounter, relationship, community context, or personal history that AI cannot invent or approximate.
   Why it resists AI: AI produces generically plausible content but cannot access a specific person's sensory memory, community, emotional history, or local context. Any AI-generated response is immediately detectable as hollow generalization (University of Chicago, UMN).
   Design signals: Require the student to name specific real people (with appropriate anonymization if needed), dates, places, or events they personally witnessed. Ask them to explain how this experience complicated, confirmed, or transformed a course concept. Reject responses that could apply to "any student anywhere."

A2. COMMUNITY-BASED AND FIELD OBSERVATION
   What it is: Students conduct structured observations, interviews, or service-learning experiences in a real-world community or professional setting, then analyze their findings through course frameworks.
   Why it resists AI: AI has no access to the student's physical environment or the people in it. Observations are timestamped to the present moment. Analysis must connect specific, locally-gathered data to theory — a synthesis AI cannot fabricate (UChicago, UMN).
   Design signals: Require students to submit raw field notes alongside their analysis. Ask them to identify one moment of genuine surprise or contradiction in what they observed, and explain what it reveals that course readings did not anticipate.

A3. HYPER-LOCAL AND CURRENT EVENT ANALYSIS
   What it is: Students independently locate a current event, news item, local policy decision, or real-world case from the present week or month, then analyze it using course concepts. No two students may use the same source.
   Why it resists AI: Prompt-sharing is structurally impossible because each student's source is unique. AI cannot locate a current event on the student's behalf and submit it without the student first finding it themselves. The recency requirement also defeats AI training data cutoffs (Yale Poorvu Center).
   Design signals: Require students to state the date, source, and URL of their chosen item at the top of the submission. Ask them to explain why they chose this particular event and what it reveals that a more famous or generic example would not.

════════════════════════════════════════════════════════════
CATEGORY B: PROCESS VISIBILITY AND EVIDENCE TRAILS
════════════════════════════════════════════════════════════

B1. SCAFFOLDED MULTI-STAGE PROCESS PORTFOLIO
   What it is: A large assignment is broken into required stages — exploratory brainstorm, annotated draft, instructor or peer feedback round, revised draft, and final reflection — each of which is graded and time-stamped (UChicago, UMN, Princeton McGraw Center).
   Why it resists AI: AI generates polished endpoints instantly; it cannot fabricate the authentic messiness of real thinking over time. The revision must demonstrably respond to specific feedback given between stages. Instructors assess growth, metacognitive awareness, and the quality of revision decisions — not just the final product.
   Design signals: Require a revision memo with each new draft explaining what changed, why, and what feedback drove the change. Use Google Docs version history or tracked changes to verify the document evolved over time. Grade the quality of revision reasoning, not just the final text.

B2. ANNOTATED BIBLIOGRAPHY WITH REFLECTIVE RATIONALE
   What it is: Students build a bibliography over time, but each entry requires a substantial annotation explaining not just what the source says, but why the student chose it, what it adds that other sources do not, and how it connects to their emerging argument.
   Why it resists AI: The rationale for source selection is deeply personal and iterative. AI can produce generic summaries but cannot explain why a specific student made a specific intellectual choice at a specific moment in their thinking process (UMN).
   Design signals: Require students to explain at least one source they initially planned to include but ultimately rejected, and why. Ask them to identify the moment their argument shifted based on a source they found.

B3. COMMONPLACE BOOK OR CURATED READING JOURNAL
   What it is: Students maintain a structured reading journal throughout the course, recording significant quotes, their own interpretive glosses, connections between readings, and evolving questions — submitted in installments, not all at once (University of Chicago).
   Why it resists AI: The journal accumulates over the full course. Entries must connect to specific class discussions, guest speakers, or prior entries, creating a traceable intellectual timeline that AI cannot retroactively fabricate.
   Design signals: Require each entry to reference something specific from that week's class discussion or a classmate's comment. Ask students to track how their central question for the course has evolved from week 1 to the present.

B4. SCREEN RECORDING OR PROCESS DOCUMENTATION VIDEO
   What it is: Students record their screen (using free tools like OBS Studio or Loom) while they work through a problem, draft an argument, or debug code — narrating their reasoning in real time.
   Why it resists AI: A screen recording captures genuine cognitive process: hesitations, false starts, backtracking, and real-time decision-making. AI cannot produce a recording of a student's screen because the student's screen does not exist in AI's environment.
   Design signals: Require at least one visible moment where the student changes direction, makes an error, or expresses genuine uncertainty. Ask them to narrate their reasoning aloud as they work, not just describe what they did after the fact.

════════════════════════════════════════════════════════════
CATEGORY C: ORAL, LIVE, AND RECORDED SELF-EXPLANATION
════════════════════════════════════════════════════════════

C1. RECORDED VIDEO EXPLANATION (STUDENT ON CAMERA)
   What it is: The student records a video of themselves — appearing on camera — explaining their reasoning, walking through their work, responding to a prompt, or teaching a concept to a hypothetical audience (MIT Sloan, Yale).
   Why it resists AI: A student's face, voice, accent, hesitations, and spontaneous reasoning are irreplaceable. Research consistently shows that live or recorded oral explanation reveals whether understanding is surface-level or deep in ways written work cannot. AI can write a script but cannot appear on camera as the student.
   Design signals: Require the student's face to be visible throughout. Include at least one element of spontaneity: an unseen follow-up prompt revealed only in the final minutes of the video prompt, or a requirement to respond in real time to a question posed mid-video. Free tools: Loom (free tier), Google Drive video upload, YouTube (unlisted).

C2. CONVERSATIONAL EXAM (SMALL GROUP ORAL, SCALABLE)
   What it is: Students meet in small groups (3-5 students per session) with the instructor or TA for a live 20-30 minute conversation about their submitted work. Each student is asked to explain, defend, and extend their reasoning spontaneously (George Washington University research, NYU Stern).
   Why it resists AI: Real-time reasoning, defense of specific decisions, and responses to novel follow-up questions cannot be faked. Research from GWU shows this format scales to classes of 60+ students in just two days of sessions while achieving high validity. Students who did not genuinely engage with their work are immediately identifiable.
   Design signals: Prepare 3-5 follow-up questions per student based on their actual submitted work. Include at least one question that asks the student to apply their argument to a scenario not mentioned in their submission. Grade on reasoning quality and intellectual honesty, not just correctness.

C3. ASYNCHRONOUS PODCAST OR AUDIO ESSAY
   What it is: Students record an audio essay or podcast episode (5-10 minutes) in which they develop and defend an argument using course concepts, addressing a specific audience (e.g., a skeptic, a policymaker, a peer who missed the unit).
   Why it resists AI: Audio requires the student's own voice, pacing, and real-time verbal reasoning. The audience-awareness dimension — adapting argument to a specific listener — requires genuine judgment that AI cannot supply without the student's own intellectual positioning (Yale Poorvu Center).
   Design signals: Require the student to state at the start who their imagined audience is and what they assume that audience already knows. Include one moment where the student acknowledges a counterargument and responds to it directly. Free tools: Audacity, Spotify for Podcasters (Anchor), SoundCloud free tier.

════════════════════════════════════════════════════════════
CATEGORY D: SOCIAL, COLLABORATIVE, AND ACCOUNTABLE LEARNING
════════════════════════════════════════════════════════════

D1. STRUCTURED PEER REVIEW WITH NAMED ACCOUNTABILITY
   What it is: Each student provides substantive written feedback on a specific named classmate's actual submission, then revises their own work in response to the feedback they received — with both the feedback given and the revision response graded (UMN, UChicago).
   Why it resists AI: Generic AI responses are obviously mismatched when the task requires engaging with a specific peer's actual argument, data, or creative choice. Students must quote or reference at least two specific ideas from the peer's real submission. Social accountability is inherently human.
   Design signals: Require students to quote directly from their peer's work at least twice. Ask them to identify one specific strength and one specific gap in the peer's argument, grounded in course vocabulary. Then require the original author to write a 200-word response explaining what they will and will not change based on the feedback, and why.

D2. SOCRATIC SEMINAR OR FISHBOWL DISCUSSION (ASYNCHRONOUS VERSION)
   What it is: Students participate in a structured asynchronous discussion where each contribution must directly respond to and build on a specific prior post — not post independently — creating a visible chain of intellectual dialogue (UMN, UChicago with social annotation tools).
   Why it resists AI: Each student's post is constrained by what the previous student actually wrote. AI cannot predict the specific content of a classmate's post and generate a contextually appropriate response in advance. The cumulative chain makes generic responses immediately obvious.
   Design signals: Require each post to begin by quoting the specific sentence from the prior post being engaged. Prohibit agreement-only responses: each post must add a new dimension, challenge an assumption, or introduce new evidence. Grade based on how substantively the student moves the collective argument forward.

D3. COLLABORATIVE SYNTHESIS WITH INDIVIDUAL ACCOUNTABILITY
   What it is: A small group collaborates to produce a shared artifact (analysis, proposal, annotated resource map), but each member submits an individual written reflection explaining their specific contribution, the decisions they pushed for or against, and what they learned from the collaborative process that they could not have learned alone.
   Why it resists AI: The individual reflection must describe specific real interactions with named group members. AI cannot fabricate the actual dynamics of a real collaboration. The "what I pushed for and why it was contested" element requires genuine engagement with the group process (UChicago).
   Design signals: Require each student to identify one decision the group made differently than they would have alone, and explain what changed their thinking. Ask them to describe one moment of genuine productive disagreement and how it was resolved.

D4. SOCIAL ANNOTATION OF A SHARED TEXT
   What it is: Students annotate a shared course reading using a social annotation tool (Hypothesis is free), with each annotation required to add interpretive value — a question, a connection to another text, a personal response, a challenge — and to engage with at least two classmates' prior annotations (UChicago, Yale).
   Why it resists AI: Social annotation is a real-time, public, conversational act. Annotations must respond to specific things classmates wrote in specific locations of the text. AI cannot participate in a live annotation session on behalf of a student without the student being present.
   Design signals: Require at least 5 original annotations and 3 substantive responses to classmates' annotations. Original annotations should include at least one genuine question the student cannot yet answer, and one connection to their own experience or a prior course reading.

════════════════════════════════════════════════════════════
CATEGORY E: DYNAMIC, PERSONALIZED, AND UNPREDICTABLE PROMPTS
════════════════════════════════════════════════════════════

E1. UNIQUE SEED VARIABLE (PERSONALIZED PROMPT ARCHITECTURE)
   What it is: Each student receives or self-generates a unique input variable — a randomly assigned real company, a specific zip code, a data set from their own neighborhood, a news headline published on their birthday — that makes identical AI outputs structurally impossible (Yale, Duke).
   Why it resists AI: When no two students share the same prompt, AI cannot generate a usable generic response. Prompt-sharing is structurally prevented because a peer's seed variable is useless to another student. This is one of the highest-resistance strategies in the research literature.
   Design signals: Build the "seed" directly into the assignment instructions: "Your assigned company is [randomly drawn from a list]" or "Use census data for the zip code where you grew up." Require students to state their unique variable at the top of every submission. Vary the seed list each semester to prevent reuse from prior cohorts.

E2. REAL-TIME DATA COLLECTION AND ANALYSIS
   What it is: Students collect their own original data — a survey they designed and administered, field measurements, a series of their own observations over time, or publicly available real-time data they pulled themselves — and analyze it using course frameworks.
   Why it resists AI: AI cannot collect real data. The data is unique to the student's moment of collection, their chosen method, and their specific population or environment. Analysis must be grounded in data the AI has never seen (MIT Sloan framework, FACT framework).
   Design signals: Require students to submit their raw data or data collection instrument alongside the analysis. Ask them to identify at least one finding that surprised them and explain what they would have predicted before collecting data. Require a brief methodology section explaining when, where, and how they collected the data.

E3. CASE STUDY ASSIGNED ON THE DAY (IN-CLASS OR TIMED RELEASE)
   What it is: The specific case, scenario, or data set students must analyze is revealed only at the moment the assessment begins — either in class or as a timed-release online task — preventing advance preparation or AI pre-generation (MIT Sloan, Stanford AIWG).
   Why it resists AI: If students cannot access the prompt in advance, they cannot pre-generate an AI response. Real-time analysis of an unseen case requires genuine internalized knowledge and adaptive reasoning. Partial AI assistance is still possible, but the time constraint and specificity of the newly revealed case sharply limit its usefulness.
   Design signals: Design 2-3 parallel versions of the case (different companies, different countries, different time periods) and randomly assign them so no sharing is possible. Include at least one element that requires connecting the case to specific content from recent class sessions — content that AI cannot access.

════════════════════════════════════════════════════════════
CATEGORY F: CRITICAL AI ENGAGEMENT AND METALITERACY
════════════════════════════════════════════════════════════

F1. EVALUATE, CRITIQUE, AND IMPROVE AN AI OUTPUT
   What it is: The student is given an actual AI-generated response to the assignment prompt and tasked with identifying its factual errors, conceptual shallowness, missing nuance, and unstated assumptions — then rewriting a section with genuine depth (Duke, Yale, UMN).
   Why it resists AI: This strategy turns AI into the object of assessment rather than the tool that avoids it. Identifying what is wrong or shallow in an AI response requires deep course knowledge. Students cannot simply ask AI to evaluate itself meaningfully without genuine disciplinary grounding.
   Design signals: Generate the AI response yourself before assigning it, so you know its specific errors. Require students to identify at least two errors or gaps that only a student who did the readings would catch. Ask them to explain what a human expert in this field would add that the AI did not. Include a rubric criterion for "evidence of genuine subject expertise beyond the AI output."

F2. AI AUDIT WITH DOCUMENTED INTERACTION LOG
   What it is: Students are permitted — or required — to use AI as part of their process, but must submit a complete, annotated log of every prompt they used, every output they received, every edit they made to the AI output, and a final reflection on what the AI got right, wrong, and what they had to add themselves (Duke, Princeton, MIT Sloan).
   Why it resists AI: The documentation requirement transforms AI use from a shortcut into a metacognitive exercise. A student who used AI uncritically will produce a log that reveals shallow engagement. A student who genuinely learned will produce a log showing meaningful dialogue, critical rejection of AI outputs, and evidence of their own intellectual contribution.
   Design signals: Require the log to be submitted alongside the final work. Grade the log on: quality of prompts, evidence of critical evaluation of AI outputs, specificity of edits made, and depth of final reflection. The reflection must answer: "What does this work now contain that the AI could not supply?"

F3. CONCEPT MAP WITH VERBAL DEFENSE
   What it is: Students create a visual concept map — a diagram showing relationships between course concepts, evidence, and their own argument — and then record a 3-5 minute video (or participate in a brief live conversation) walking through their map and explaining the logic of each connection (UChicago, Yale).
   Why it resists AI: Concept mapping requires genuine relational understanding — knowing not just what concepts mean, but how and why they connect in a specific argument. The verbal defense of the map requires the student to explain their own thinking in real time. AI can generate a map, but it cannot explain why this student made these specific connection choices.
   Design signals: Require at least one connection in the map that the student cannot find explicitly stated in the course readings — a connection they inferred or synthesized themselves. During the defense, ask the student to identify which connection they are least confident about and why.

════════════════════════════════════════════════════════════
CATEGORY G: MULTIMODAL AND EMBODIED PRODUCTION
════════════════════════════════════════════════════════════

G1. INFOGRAPHIC OR VISUAL ARGUMENT WITH PROCESS RATIONALE
   What it is: Students create a visual artifact — an infographic, annotated diagram, illustrated argument, or data visualization — that communicates a course concept or argument to a specific non-expert audience, accompanied by a written rationale explaining their design choices (Duke, UMN).
   Why it resists AI: While AI can generate generic visuals, it cannot make the specific design choices a student makes for a specific argument aimed at a specific audience. The design rationale — explaining why this visual, this layout, this color, this level of simplification — requires genuine decision-making that exposes the student's understanding.
   Design signals: Require the student to identify their target audience and explain two specific design choices they made with that audience in mind. Ask them to describe one element they cut and why cutting it made the argument stronger. Free tools: Canva (free tier), Google Slides.

G2. CREATIVE TRANSLATION ACROSS REGISTERS OR FORMATS
   What it is: Students take a course concept, argument, or finding and translate it into a radically different format: a short op-ed for a specific publication, a letter to a policymaker, a dialogue between two historical figures, a set of instructions for a child, or a scene in a short play — with a reflective memo explaining the translation choices made.
   Why it resists AI: AI can produce generic versions of any format. What it cannot produce is a specific student's intellectual positioning: which aspects of the concept they prioritized, which analogies felt authentic to their own thinking, and why they chose this particular recipient or format over alternatives. The memo makes that thinking explicit and gradable.
   Design signals: Require the memo to identify at least one concept that was very difficult to translate and explain the compromise the student made. Ask them to explain what is inevitably lost in this translation and what is unexpectedly gained.

G3. HANDWRITTEN IN-CLASS OR TIMED RESPONSE (WITH REFLECTION)
   What it is: Students complete a handwritten response, diagram, or problem-solving task in class or under timed online conditions, then follow up asynchronously with a typed reflection on their own handwritten work — extending, correcting, or complicating what they wrote in the moment (UMN, NMU CTL).
   Why it resists AI: Handwriting is physically attributable to the student. The timed constraint prevents AI assistance. The subsequent reflection — which must engage with the actual content of the handwritten work — creates a two-part artifact that AI cannot fully replicate. This format also provides instructors with a natural baseline sample of each student's unassisted writing.
   Design signals: Scan or photograph handwritten work and upload it alongside the typed reflection. Require the reflection to quote or directly reference at least two specific things written in the handwritten portion. Ask students to identify one thing they would revise with more time and explain what they now think more clearly.

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
          You have probably spent more time than you would like wondering whether the work 
          your students submitted was actually theirs. That frustration is real, and you are 
          not alone.
        </p>
        <p>
          But here is the shift that changes everything: <strong>AI in the classroom is not 
          a plagiarism problem. It is a pedagogy problem.</strong> If an AI can complete your 
          assessment better than your students can, the assessment may not have been measuring 
          real thinking in the first place.
        </p>
        <p>
          The goal is not to ban AI or catch cheaters. It is to design learning experiences 
          so authentic, so rooted in each student's own thinking and context, that doing the 
          work <em>is</em> the learning, and shortcuts simply do not apply.
        </p>
        <p>
          In under 2 minutes, describe your course and what you want students to genuinely 
          demonstrate. We will generate <strong>3 AI-resistant assessment alternatives</strong>, 
          each with ready-to-use student instructions you can copy straight into your syllabus.
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
    st.markdown('<div class="field-hint">What should students know or be able to do by the end of the course? Feel free to copy and paste your course objectives from your syllabus, or explain in a few sentences.</div>', unsafe_allow_html=True)
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
                        max_tokens=4000,
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
        (function() {
            function scrollUp() {
                window.scrollTo({top: 0, behavior: 'instant'});
                try {
                    window.parent.document.querySelector('section.main')
                        .scrollTo({top: 0, behavior: 'instant'});
                } catch(e) {}
                try {
                    window.parent.document.querySelector('.main')
                        .scrollTo({top: 0, behavior: 'instant'});
                } catch(e) {}
            }
            scrollUp();
            setTimeout(scrollUp, 100);
            setTimeout(scrollUp, 300);
        })();
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
                            {"role": "system", "content": "You are an expert higher education assessment designer who writes detailed, practical, ready-to-use assessment materials. You use the most effective learning theories, instructional design strategies, and frameworks."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.95,
                        max_tokens=4000,
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
                            {"role": "system", "content": "You are an expert higher education assessment designer who writes detailed, practical, ready-to-use assessment materials. You use the most effective learning theories, instructional design strategies, and frameworks."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.95,
                        max_tokens=4000,
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
