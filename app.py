import os
import json
import re
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv

# -------------------- Configuration --------------------
load_dotenv()

st.set_page_config(
    page_title="FounderAI | Startup Co-Founder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

AGENT_ROLES = {
    "Tech Requirements": "Define the MVP, core features, suggested architecture, data needs, integrations, and a realistic build sequence.",
    "Risk & Validation": "Identify the riskiest assumptions, legal/operational/privacy risks, and low-cost experiments to validate demand.",
    "Market Analysis": "Describe likely customer segments, their pain points, market-sizing approach, and what evidence is still needed. Do not invent precise TAM figures.",
    "Competitive Intelligence": "Map competitor categories, alternatives customers use today, differentiation opportunities, and defensibility. Do not invent named competitors.",
    "Business Model": "Recommend pricing hypotheses, revenue streams, cost drivers, and an initial business model to test.",
    "Financial Planning": "Create clearly labelled rough cost/revenue assumptions, key unit economics, break-even logic, and the variables that most affect viability. Never present estimates as verified facts.",
    "Go-To-Market Strategy": "Suggest a focused launch niche, positioning, acquisition channels, first 10-customer experiment, and 30-day launch actions.",
    "Pitch Deck & Execution": "Create a concise pitch-deck outline and a prioritized 30/60/90-day execution roadmap with measurable milestones.",
}

AGENT_ICONS = {
    "Tech Requirements": "🛠️",
    "Risk & Validation": "🛡️",
    "Market Analysis": "📊",
    "Competitive Intelligence": "🔎",
    "Business Model": "💼",
    "Financial Planning": "💰",
    "Go-To-Market Strategy": "📣",
    "Pitch Deck & Execution": "🎯",
}


# -------------------- Helpers --------------------
def get_api_key():
    """Read key from Streamlit secrets first, then environment."""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("GEMINI_API_KEY", "")


def extract_json(text):
    """Handle JSON returned with or without Markdown code fences."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def generate_with_gemini(idea, audience, location, budget, model):
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY was not found. Add it to Streamlit Secrets or your local .env file."
        )

    agent_instructions = "\n".join(
        f'{i+1}. "{name}": {description}'
        for i, (name, description) in enumerate(AGENT_ROLES.items())
    )

    prompt = f"""
You are FounderAI, a careful startup advisory system. Analyze the user-provided
startup concept and return practical, specific, beginner-friendly advice.

STARTUP INPUT
Idea: {idea}
Target customer: {audience or "Not specified; infer a plausible initial segment and label it as an assumption"}
Location/market: {location or "Not specified"}
Available starting budget: {budget or "Not specified"}

Create one output for each of these eight specialist roles:
{agent_instructions}

Return ONLY valid JSON, with exactly these eight keys:
{json.dumps(list(AGENT_ROLES.keys()))}

Each value must be a useful Markdown string with:
- What this means for this specific idea
- 3-5 practical recommendations
- Important assumptions or unknowns
- At least one concrete next action

Rules:
- Do not reuse a laundry-service example unless the user's idea is about laundry.
- Do not fabricate market statistics, competitor names, citations, customer interviews,
  revenue, or financial facts.
- Clearly label financial numbers as illustrative assumptions, and use the user's
  stated currency/location when possible. If no budget is provided, avoid pretending
  an exact budget is known.
- Prefer low-cost validation before building a full product.
- Be honest about uncertainty. Avoid guaranteed-success language.
- Keep each specialist output concise but substantive (roughly 100-160 words).
"""

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.35,
            "responseMimeType": "application/json",
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=90)
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not reach Gemini: {exc}") from exc

    if response.status_code != 200:
        try:
            details = response.json().get("error", {}).get("message", response.text)
        except ValueError:
            details = response.text
        raise RuntimeError(f"Gemini API error ({response.status_code}): {details}")

    try:
        data = response.json()
        generated_text = data["candidates"][0]["content"]["parts"][0]["text"]
        result = extract_json(generated_text)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RuntimeError("Gemini returned an unexpected response. Please retry.") from exc

    if not isinstance(result, dict):
        raise RuntimeError("The AI response was not a valid JSON object.")

    missing = [name for name in AGENT_ROLES if not isinstance(result.get(name), str)]
    if missing:
        raise RuntimeError("The AI response was incomplete. Missing: " + ", ".join(missing))

    return {name: result[name].strip() for name in AGENT_ROLES}


def build_demo_outputs(idea, audience, location, budget):
    """Transparent offline demo; these are templates, not AI-generated findings."""
    outputs = {}
    context = f"Concept: **{idea}**\n\n"
    if audience:
        context += f"Target customer: **{audience}**\n\n"
    if location:
        context += f"Initial market: **{location}**\n\n"
    if budget:
        context += f"Available budget: **{budget}**\n\n"

    templates = {
        "Tech Requirements": "Start with the smallest testable MVP rather than a full platform.\n\n- Define the one core user problem and primary user journey.\n- Build only the feature needed to test that journey.\n- Choose a simple Python/API/database stack appropriate to the prototype.\n- Track basic usage and feedback from the first testers.\n\n**Unknowns:** Required integrations, expected usage, security needs, and technical constraints.\n\n**Next action:** Write a one-page MVP feature list and sketch the user journey.",
        "Risk & Validation": "The largest early risk is building before confirming that customers experience this problem often enough to pay for a solution.\n\n- List the three assumptions most critical to success.\n- Test the problem with a short survey or landing-page experiment.\n- Offer a manual or concierge version before automating everything.\n- Check applicable privacy, consumer, licensing, and operational requirements.\n\n**Unknowns:** Willingness to pay, trust, frequency of need, and delivery cost.\n\n**Next action:** Design one low-cost experiment that could disprove the idea.",
        "Market Analysis": "Begin with a narrow customer segment rather than claiming a large total addressable market.\n\n- Define the first customer by need, location, and current workaround.\n- Estimate the reachable market from a count of target customers multiplied by a realistic spend assumption.\n- Separate total market, serviceable market, and the first reachable niche.\n- Validate assumptions using public data and customer research.\n\n**Unknowns:** Verified customer counts, demand frequency, and actual spending.\n\n**Next action:** Identify one initial niche and collect evidence for its size.",
        "Competitive Intelligence": "Competition includes direct products, indirect services, spreadsheets, manual processes, and doing nothing.\n\n- List the alternatives a customer uses today.\n- Compare price, convenience, trust, speed, and quality.\n- Find one underserved use case where the concept can be meaningfully better.\n- Avoid relying on features alone as a long-term moat.\n\n**Unknowns:** Local competitors, customer switching costs, and competitor pricing.\n\n**Next action:** Build a comparison table of five verified alternatives.",
        "Business Model": "Treat pricing as a hypothesis that must be tested with real customers.\n\n- Select the person or organization that receives value and pays.\n- Test one simple primary revenue model first.\n- Identify variable costs per transaction or customer.\n- Consider a paid pilot before introducing multiple plans.\n\n**Unknowns:** Price sensitivity, repeat usage, churn, and willingness to pay.\n\n**Next action:** Draft two pricing options and test them with target users.",
        "Financial Planning": "Build a simple assumption-driven model before making investment decisions.\n\n- Separate one-time setup costs from monthly operating costs.\n- Estimate contribution per sale: price minus variable cost.\n- Estimate break-even volume: fixed monthly costs divided by contribution per sale.\n- Create conservative, base, and optimistic scenarios.\n\n**Unknowns:** Actual acquisition cost, conversion, retention, and operating expenses.\n\n**Next action:** Create a spreadsheet with editable assumptions. No figures are verified until supported by quotes or data.",
        "Go-To-Market Strategy": "Launch in one small segment where feedback and customer access are manageable.\n\n- Write a one-sentence value proposition.\n- Choose one primary acquisition channel to test.\n- Recruit a small pilot group and measure activation and repeat use.\n- Collect objections and improve the offer before scaling promotion.\n\n**Unknowns:** Best channel, acquisition cost, and referral potential.\n\n**Next action:** Plan a 2-week pilot with a clear success metric.",
        "Pitch Deck & Execution": "A concise pitch should connect the problem, customer evidence, solution, business model, and execution plan.\n\n- Slides: Problem, target customer, solution, product demo, market approach, alternatives, business model, validation evidence, roadmap, and team/ask.\n- First 30 days: validate the problem and interview or survey target users.\n- Days 31-60: test an MVP or manual pilot.\n- Days 61-90: evaluate usage, retention, costs, and whether to iterate.\n\n**Unknowns:** Evidence of demand, traction, and delivery feasibility.\n\n**Next action:** Define one measurable milestone for the next 30 days.",
    }
    for name, body in templates.items():
        outputs[name] = context + body
    return outputs


def make_blueprint(idea, audience, location, budget, outputs, mode):
    lines = [
        "# FounderAI — Startup Strategy Blueprint",
        f"Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        f"Analysis mode: {mode}",
        "",
        "## Startup inputs",
        f"- Idea: {idea}",
        f"- Target customer: {audience or 'Not specified'}",
        f"- Initial market: {location or 'Not specified'}",
        f"- Available budget: {budget or 'Not specified'}",
        "",
        "> Note: This is AI-assisted planning, not verified market research, legal advice, or a guarantee of business success. Validate assumptions before investing.",
        "",
    ]
    for name, content in outputs.items():
        lines.extend([f"## {name}", content, ""])
    return "\n".join(lines)


# -------------------- Styling --------------------
st.markdown(
    """
    <style>
    header {visibility: hidden;}
    .main .block-container {padding-top: 1.5rem; max-width: 1150px;}
    .hero {
        background: linear-gradient(120deg, #0d47a1, #0d6efd);
        padding: 28px 24px; border-radius: 16px; color: white;
        text-align: center; margin-bottom: 20px;
    }
    .hero h1 {color: white !important; margin: 0 0 8px 0;}
    .hero p {color: #eaf2ff; margin: 0;}
    .info-card {
        border: 1px solid #e5eaf2; border-radius: 13px;
        padding: 17px 18px; background: var(--secondary-background-color);
        margin-bottom: 10px;
    }
    .small-muted {color: #718096; font-size: 0.9rem;}
    div.stButton > button[kind="primary"] {
        background: #0d6efd; border: 0; font-weight: 650;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- Interface --------------------
st.markdown(
    """
    <div class="hero">
      <h1>🚀 FounderAI</h1>
      <p>Your AI-powered startup co-founder — turn an idea into a testable action plan.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ Analysis settings")
    mode = st.radio(
        "Choose analysis mode",
        ["Live Gemini AI", "Demonstration mode"],
        index=0 if get_api_key() else 1,
        help="Live mode uses your Gemini API key. Demonstration mode uses clearly labelled offline templates.",
    )
    model = st.selectbox(
        "Gemini model",
        ["gemini-3.8-flash", "gemini-2.0-flash"],
        index=0,
        disabled=(mode != "Live Gemini AI"),
    )
    st.caption("Keep API keys in Streamlit Secrets or a local .env file. Never paste keys into app.py.")
    st.divider()
    st.caption("FounderAI • AI Startup Strategy Assistant")

st.subheader("💡 Describe your startup idea")
st.write("Provide a little context so the analysis can be more relevant.")

with st.form("startup_form"):
    idea = st.text_area(
        "Business idea *",
        placeholder="Example: An app that helps small farmers rent nearby agricultural equipment...",
        height=105,
    )
    col1, col2 = st.columns(2)
    with col1:
        audience = st.text_input(
            "Target customers",
            placeholder="e.g. small farmers, college students, local retailers",
        )
        location = st.text_input(
            "Initial market / location",
            placeholder="e.g. Andhra Pradesh, India",
        )
    with col2:
        budget = st.text_input(
            "Available starting budget",
            placeholder="e.g. ₹50,000 or not decided",
        )
        st.markdown(
            '<div class="small-muted">Tip: You can leave optional fields blank. '
            'The report will label missing information as assumptions.</div>',
            unsafe_allow_html=True,
        )
    submitted = st.form_submit_button(
        "🚀 Generate Startup Blueprint",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not idea.strip():
        st.warning("Please enter your startup idea before generating the analysis.")
    else:
        try:
            with st.spinner("FounderAI is preparing the specialist analysis..."):
                if mode == "Live Gemini AI":
                    outputs = generate_with_gemini(
                        idea.strip(), audience.strip(), location.strip(), budget.strip(), model
                    )
                    result_mode = f"Live Gemini AI ({model})"
                else:
                    outputs = build_demo_outputs(
                        idea.strip(), audience.strip(), location.strip(), budget.strip()
                    )
                    result_mode = "Demonstration mode (offline templates)"

            st.session_state["founderai_result"] = {
                "idea": idea.strip(),
                "audience": audience.strip(),
                "location": location.strip(),
                "budget": budget.strip(),
                "outputs": outputs,
                "mode": result_mode,
            }
            st.success("Startup blueprint generated successfully.")
        except Exception as exc:
            st.error(str(exc))
            if mode == "Live Gemini AI":
                st.info(
                    "You can switch to Demonstration mode for an offline review demo. "
                    "Do not describe demo output as live AI-generated analysis."
                )

# -------------------- Results --------------------
result = st.session_state.get("founderai_result")
if result:
    st.divider()
    st.header("📊 Your Startup Strategy Dashboard")
    st.markdown(f"**Startup idea:** {result['idea']}")
    st.caption(f"Mode: {result['mode']}")

    if result["mode"].startswith("Demonstration"):
        st.info(
            "Demonstration output: these are offline planning templates tailored with your inputs, "
            "not live Gemini responses or verified market research."
        )

    c1, c2, c3 = st.columns(3)
    c1.metric("Specialist perspectives", "8")
    c2.metric("Analysis sections", "8")
    c3.metric("Status", "Generated")

    st.subheader("🤖 Specialist analysis")
    for name, content in result["outputs"].items():
        with st.expander(f"{AGENT_ICONS[name]}  {name}", expanded=(name == "Market Analysis")):
            st.markdown(content)

    blueprint = make_blueprint(
        result["idea"], result["audience"], result["location"], result["budget"],
        result["outputs"], result["mode"]
    )
    st.download_button(
        "📥 Download complete startup blueprint (.md)",
        data=blueprint,
        file_name="FounderAI_Startup_Blueprint.md",
        mime="text/markdown",
        use_container_width=True,
    )

st.divider()
st.subheader("How FounderAI works")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 1. 📝 Idea input")
    st.write("Describe the problem, customer, market, and available resources.")
with col2:
    st.markdown("### 2. 🤖 Specialist analysis")
    st.write("Eight specialist perspectives produce structured, idea-specific recommendations.")
with col3:
    st.markdown("### 3. 📋 Action blueprint")
    st.write("Review the outputs and export a practical plan for further validation.")

st.markdown(
    """
    <div style="background:#0d47a1;color:white;text-align:center;padding:18px;border-radius:12px;margin-top:28px;">
      <strong>FounderAI — AI Startup Co-Founder</strong><br>
      B.Tech CSE (Artificial Intelligence) • Madanapalle Institute of Technology & Science
    </div>
    """,
    unsafe_allow_html=True,
        )
