
import streamlit as st
import os
import requests
import json
from dotenv import load_dotenv

# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="FounderAI - AI Startup Co-Founder",
    page_icon="🚀",
    layout="wide"
)

def get_api_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    except Exception:
        return os.getenv("GEMINI_API_KEY")


API_KEY = get_api_key()
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ---------------------------------------------------------
# 2. AGENT DEFINITIONS
# ---------------------------------------------------------

AGENT_ROLES = [
    ("Startup Idea Analyst", "Evaluate the startup idea, problem, solution and value proposition."),
    ("Technology Agent", "Recommend technical architecture, tools and technology requirements."),
    ("Market Research Agent", "Analyze target customers, market opportunity and demand."),
    ("Competitor Agent", "Identify competitor categories, differentiation and competitive advantages."),
    ("Business Model Agent", "Recommend revenue streams, pricing and monetization."),
    ("Financial Agent", "Estimate startup costs, revenue potential and break-even considerations."),
    ("Marketing Agent", "Develop customer acquisition and go-to-market strategies."),
    ("Risk Assessment Agent", "Identify business risks, validation methods and mitigation strategies.")
]

# ---------------------------------------------------------
# 3. CUSTOM CSS
# ---------------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #f4f7fb;
}

.main-title {
    background: linear-gradient(120deg, #0d6efd, #153e90);
    padding: 30px;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 25px;
}

.main-title h1 {
    color: red;
}

.feature-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e5eaf2;
    margin-bottom: 15px;
}

.agent-title {
    color: #0d6efd;
    font-size: 19px;
    font-weight: bold;
}

div.stButton > button {
    background-color: #0d6efd;
    color: white;
    border-radius: 8px;
    font-weight: bold;
    min-height: 45px;
}

.footer {
    background-color: #153e90;
    color: white;
    text-align: center;
    padding: 20px;
    border-radius: 10px;
    margin-top: 35px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. HEADER
# ---------------------------------------------------------

st.markdown("""
<div class="main-title">
    <h1>🚀 FounderAI</h1>
    <h3>Your AI-Powered Startup Co-Founder</h3>
    <p>Transform your business idea into an actionable startup strategy.</p>
</div>
""", unsafe_allow_html=True)

st.write(
    "FounderAI uses specialized AI analysis to help entrepreneurs "
    "evaluate ideas, understand markets and develop business strategies."
)

# ---------------------------------------------------------
# 5. USER INPUT
# ---------------------------------------------------------

st.subheader("💡 Enter Your Startup Information")

col1, col2 = st.columns(2)

with col1:
    idea = st.text_area(
        "Describe your business idea",
        placeholder="Example: An online platform connecting farmers with customers.",
        height=120
    )

    target_customer = st.text_input(
        "Target Customers",
        placeholder="Example: Farmers, students, working professionals"
    )

with col2:
    budget = st.selectbox(
        "Initial Startup Budget",
        [
            "Below ₹10,000",
            "₹10,000 - ₹50,000",
            "₹50,000 - ₹1 Lakh",
            "₹1 Lakh - ₹5 Lakhs",
            "₹5 Lakhs - ₹10 Lakhs",
            "Above ₹10 Lakhs"
        ]
    )

    location = st.text_input(
        "Target Market / Location",
        placeholder="Example: Andhra Pradesh, India"
    )

mode = st.radio(
    "Choose Analysis Mode",
    ["Live Gemini AI", "Demonstration Mode"],
    horizontal=True
)

# ---------------------------------------------------------
# 6. GEMINI API FUNCTION
# ---------------------------------------------------------

def call_gemini(prompt):

    if not API_KEY:
        raise ValueError(
            "Gemini API key not found. Configure GEMINI_API_KEY "
            "in Streamlit Cloud Secrets."
        )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + MODEL
        + ":generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 7000,
            "responseMimeType": "application/json"
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=180
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Gemini API error ({response.status_code}): "
            f"{response.text[:1000]}"
        )

    result = response.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        data = json.loads(text)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        raise RuntimeError(
            "Gemini returned an invalid response. Please try again."
        )

    if not isinstance(data, dict):
        raise RuntimeError("Unexpected response format from Gemini.")

    return data

# ---------------------------------------------------------
# 7. BUILD AI PROMPT
# ---------------------------------------------------------

def build_prompt(idea, target_customer, budget, location):

    agent_instructions = "\n".join(
        [
            f"{i}. {name}: {description}"
            for i, (name, description) in enumerate(AGENT_ROLES, 1)
        ]
    )

    return f"""
You are FounderAI, an expert AI startup advisory system.

Analyze the following startup concept:

BUSINESS IDEA: {idea}
TARGET CUSTOMERS: {target_customer}
INITIAL BUDGET: {budget}
TARGET LOCATION: {location}

Perform eight distinct specialist analyses.

SPECIALIST AGENTS:
{agent_instructions}

IMPORTANT RULES:
1. Make every analysis specific to the submitted idea.
2. Do not invent verified market statistics.
3. Clearly label financial figures as illustrative estimates.
4. Explain assumptions behind recommendations.
5. Give practical suggestions suitable for the stated budget.
6. Provide useful, actionable recommendations.

Return ONLY valid JSON in this structure:

{{
    "Startup Idea Analyst": "Detailed analysis...",
    "Technology Agent": "Detailed analysis...",
    "Market Research Agent": "Detailed analysis...",
    "Competitor Agent": "Detailed analysis...",
    "Business Model Agent": "Detailed analysis...",
    "Financial Agent": "Detailed analysis...",
    "Marketing Agent": "Detailed analysis...",
    "Risk Assessment Agent": "Detailed analysis...",
    "Executive Summary": "Overall startup recommendation...",
    "Estimated Startup Cost": "Illustrative cost estimate...",
    "Revenue Strategy": "Revenue strategy...",
    "Top Recommendations": [
        "Recommendation 1",
        "Recommendation 2",
        "Recommendation 3"
    ]
}}
"""

# ---------------------------------------------------------
# 8. DEMONSTRATION MODE
# ---------------------------------------------------------

def build_demo_results(idea):

    results = {}

    demo_texts = [
        "Evaluate the problem being solved, the proposed solution and the value proposition. Validate customer demand before investing.",
        "Consider a scalable application architecture with a Python backend, database and secure API integration.",
        "Identify customer segments, conduct surveys and investigate local demand. Treat market size as unverified until researched.",
        "Compare direct and indirect competitors. Differentiate through pricing, convenience and customer experience.",
        "Consider subscriptions, transaction fees and premium services depending on the business model.",
        "Prepare an initial budget, monthly expense plan and conservative revenue forecast. Validate assumptions before spending.",
        "Start with a focused customer segment, social media campaigns, partnerships and referral programs.",
        "Potential risks include weak demand, competition, cash flow and operational challenges. Test the idea with a small pilot."
    ]

    for (name, _), text in zip(AGENT_ROLES, demo_texts):
        results[name] = (
            f"Illustrative analysis for '{idea}'. {text}"
        )

    results["Executive Summary"] = (
        "This is a demonstration analysis. Conduct customer interviews, "
        "validate demand and test a minimum viable product before investing."
    )

    results["Estimated Startup Cost"] = (
        "Prepare a detailed budget based on actual vendor quotations. "
        "No verified cost estimate is available in demonstration mode."
    )

    results["Revenue Strategy"] = (
        "Test suitable revenue models with potential customers before selecting one."
    )

    results["Top Recommendations"] = [
        "Validate the problem with potential customers.",
        "Build a small minimum viable product.",
        "Measure customer interest before scaling."
    ]

    return results

# ---------------------------------------------------------
# 9. BLUEPRINT GENERATOR
# ---------------------------------------------------------

def make_blueprint(idea, target, budget, location, outputs, mode):

    report = f"""
# FOUNDERAI - STARTUP STRATEGY BLUEPRINT

## Startup Concept
{idea}

## Target Customers
{target}

## Initial Budget
{budget}

## Target Location
{location}

## Analysis Mode
{mode}

---

"""

    for name, _ in AGENT_ROLES:
        report += f"\n## {name}\n\n"
        report += str(outputs.get(name, "No analysis available."))
        report += "\n\n"

    for key in [
        "Executive Summary",
        "Estimated Startup Cost",
        "Revenue Strategy"
    ]:
        report += f"\n## {key}\n\n"
        report += str(outputs.get(key, "Not available."))
        report += "\n\n"

    report += "\n## Top Recommendations\n\n"

    recommendations = outputs.get("Top Recommendations", [])

    if isinstance(recommendations, list):
        for item in recommendations:
            report += f"- {item}\n"
    else:
        report += str(recommendations)

    report += "\n\nGenerated by FounderAI - AI Startup Co-Founder.\n"

    return report

# ---------------------------------------------------------
# 10. SESSION STATE
# ---------------------------------------------------------

if "founderai_results" not in st.session_state:
    st.session_state["founderai_results"] = None

if "founderai_idea" not in st.session_state:
    st.session_state["founderai_idea"] = ""

if "founderai_mode" not in st.session_state:
    st.session_state["founderai_mode"] = ""

# ---------------------------------------------------------
# 11. ANALYZE STARTUP
# ---------------------------------------------------------

if st.button("🚀 Analyze Startup Concept", use_container_width=True):

    if not idea.strip():
        st.warning("Please enter your startup business idea.")

    else:
        try:
            if mode == "Live Gemini AI":

                with st.spinner(
                    "FounderAI is preparing the specialist analysis..."
                ):
                    prompt = build_prompt(
                        idea.strip(),
                        target_customer.strip(),
                        budget,
                        location.strip()
                    )

                    outputs = call_gemini(prompt)

                st.session_state["founderai_results"] = outputs
                st.session_state["founderai_mode"] = "Live Gemini AI"
                st.session_state["founderai_idea"] = idea.strip()

                st.success("Live Gemini analysis completed successfully!")

            else:

                outputs = build_demo_results(idea.strip())

                st.session_state["founderai_results"] = outputs
                st.session_state["founderai_mode"] = (
                    "Demonstration Mode — simulated examples"
                )
                st.session_state["founderai_idea"] = idea.strip()

                st.info(
                    "Demonstration Mode is active. These are illustrative "
                    "examples, not live AI-generated results."
                )

        except Exception as exc:

            st.error(f"FounderAI could not complete the analysis: {exc}")

            st.caption(
                "Check your Gemini API key, model availability, quota "
                "and Streamlit app logs."
            )

# ---------------------------------------------------------
# 12. DISPLAY RESULTS
# ---------------------------------------------------------

if st.session_state["founderai_results"]:

    outputs = st.session_state["founderai_results"]

    result_idea = st.session_state["founderai_idea"]
    result_mode = st.session_state["founderai_mode"]

    st.divider()

    st.header("📊 Startup Intelligence Dashboard")

    st.write(f"**Business Idea:** {result_idea}")

    if result_mode.startswith("Demonstration"):
        st.warning(
            "Demonstration output — illustrative examples only."
        )
    else:
        st.success("Live AI-generated analysis")

    st.subheader("🎯 Executive Summary")

    st.markdown(
        str(outputs.get("Executive Summary", "Not available."))
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Estimated Startup Cost")
        st.write(
            outputs.get(
                "Estimated Startup Cost",
                "Not available."
            )
        )

    with col2:
        st.subheader("📈 Revenue Strategy")
        st.write(
            outputs.get(
                "Revenue Strategy",
                "Not available."
            )
        )

    st.divider()

    st.subheader("🤖 Eight Specialist Agents")

    for index, (name, _) in enumerate(AGENT_ROLES, start=1):

        with st.expander(
            f"Agent {index}: {name}",
            expanded=(index == 1)
        ):
            st.write(
                outputs.get(
                    name,
                    "No analysis available."
                )
            )

    st.divider()

    st.subheader("⭐ Top Recommendations")

    recommendations = outputs.get("Top Recommendations", [])

    if isinstance(recommendations, list):
        for item in recommendations:
            st.markdown(f"- {item}")
    else:
        st.write(recommendations)

    # Download blueprint

    blueprint = make_blueprint(
        result_idea,
        target_customer,
        budget,
        location,
        outputs,
        result_mode
    )

    st.download_button(
        label="📥 Download Startup Blueprint",
        data=blueprint,
        file_name="FounderAI_Startup_Blueprint.md",
        mime="text/markdown",
        use_container_width=True
    )

# ---------------------------------------------------------
# 13. HOW IT WORKS
# ---------------------------------------------------------

st.divider()

st.header("How FounderAI Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💡 1. Idea Submission")
    st.write(
        "Enter your startup concept, target customers, budget and location."
    )

with col2:
    st.markdown("### 🤖 2. AI Analysis")
    st.write(
        "Eight specialized perspectives analyze the business idea using Gemini."
    )

with col3:
    st.markdown("### 📋 3. Strategy Blueprint")
    st.write(
        "Review the generated recommendations and download the startup report."
    )

# ---------------------------------------------------------
# 14. FOOTER
# ---------------------------------------------------------

st.markdown("""
<div class="footer">
    <strong>© 2026 FounderAI - AI Agent</strong><br>
    B.Tech CSE (Artificial Intelligence)<br>
    Madanapalle Institute of Technology & Science
</div>
""", unsafe_allow_html=True)
            
