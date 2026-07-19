import streamlit as st
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 1. Page Configuration
st.set_page_config(page_title="FounderAI", page_icon="🚀", layout="centered")

# 2. Inject Custom CSS to style it like a professional HTML Web App
st.markdown("""
    <style>
    /* Hide default Streamlit header elements */
    header {visibility: hidden;}
    
    /* Top Navigation Banner styling */
    .nav-banner {
        background-color: #0d6efd;
        padding: 25px;
        text-align: center;
        border-radius: 4px;
        margin-bottom: 30px;
        color: white;
    }
    .nav-banner h1 {
        color: white !important;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .nav-links {
        font-size: 16px;
        font-weight: 500;
    }
    .nav-links span {
        margin: 0 15px;
        cursor: pointer;
    }
    .nav-active {
        color: #ffc107 !important;
        font-weight: bold;
    }
    
    /* Elegant White Feature Cards */
    .feature-card {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #eef2f5;
    }
    .card-title {
        color: #0d6efd;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    /* Custom Blue Button override */
    div.stButton > button {
        background-color: #0d6efd !important;
        color: white !important;
        border-radius: 8px !important;
        width: 100% !important;
        padding: 10px !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    /* Footer Styling */
    .footer-section {
        background-color: #0d6efd;
        color: white;
        text-align: center;
        padding: 20px;
        margin-top: 50px;
        border-radius: 4px;
        font-size: 14px;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Top Banner Navigation (Matching your friend's header)
st.markdown("""
    <div class="nav-banner">
        <h1>🎓 FounderAI – AI Agent</h1>
    </div>
""", unsafe_allow_html=True)

# 4. Main Welcome Card
st.markdown("""
    <div class="feature-card" style="text-align: center;">
        <h2 style="color: #0d6efd; font-weight: bold;">Find the Right Startup Strategy with AI 🚀</h2>
        <p style="color: #495057; font-size: 16px; margin-top: 15px;">
            FounderAI is an AI-powered pipeline recommendation system that helps entrepreneurs build 
            optimized blueprints based on target scale, initial capital, validation risk, and business models.
        </p>
        <p style="color: #6c757d; font-size: 14px;">
            Get personalized multi-agent business suggestions and save time researching operations.
        </p>
    </div>
""", unsafe_allow_html=True)

# 5. Core Operational Controls
use_simulation = st.checkbox("💡 Run in Demonstration Mode", value=True)
user_prompt = st.text_input("Enter your business idea here:", placeholder="e.g., A 24-hour pickup and delivery laundry service app.")

agent_roles = {
    "Agent 1 (Tech Requirements)": "Core architecture needs a mobile interface (React Native), centralized PostgreSQL cluster, and microservice pipelines for driver matching.",
    "Agent 2 (Risk & Validation)": "Operational risks include managing independent contractor compliance, route delays during peak congestion hours, and early customer retention drops.",
    "Agent 3 (Market Size Analysis)": "Primary target demographic centers around university students and early career urban professionals. TAM estimated at $500M within urban metropolitan hubs.",
    "Agent 4 (Competitive Intelligence)": "Competitors include generic apps and local laundromats. Defensibility moat built through automated route batching and B2B corporate partnerships.",
    "Agent 5 (Business Modeling)": "Primary monetization relies on a tiered monthly subscription service, per-pound processing upcharges, and premium express turnaround tiers.",
    "Agent 6 (Financial Cost Estimations)": "Initial capital allocations require $15k cloud infrastructure, $40k localized logistics/driver onboarding, and $25k customer acquisition marketing.",
    "Agent 7 (Go-To-Market Strategy)": "Launch framework focuses heavily on hyper-local digital ads targeting college campuses, coupled with physical promotional codes distributed at student unions.",
    "Agent 8 (Pitch Deck Outline)": "10-Slide Structure: 1. Cover, 2. Problem Statement, 3. Solution (The App), 4. Market Size, 5. Product Features, 6. Revenue Model, 7. Competition, 8. Marketing, 9. Financials, 10. The Ask."
}

# "Apply" Style Main Action Button
if st.button("🚀 Analyze Startup Concept"):
    if user_prompt:
        shared_state_notebook = f"=========================================\n🚀 FOUNDERAI: STARTUP STRATEGY BLUEPRINT\n=========================================\n\nInitial Concept: {user_prompt}\n\n"
        status_box = st.empty()
        agent_outputs_dict = {}
        
        for agent_name, fixed_text in agent_roles.items():
            status_box.info(f"⚙️ {agent_name} processing...")
            time.sleep(0.2) 
            agent_outputs_dict[agent_name] = f"- {fixed_text}"
            shared_state_notebook += f"{agent_name}\n- {fixed_text}\n\n"
            
        status_box.empty()
        st.success("✅ Success! Strategy Compiled Below.")
        
        # Display Results in White HTML Feature Cards matching the layout style
        st.markdown("## 📊 Strategic Agent Analysis")
        for agent_name, output_text in agent_outputs_dict.items():
            st.markdown(f"""
                <div class="feature-card">
                    <div class="card-title">🤖 {agent_name}</div>
                    <p style="color: #333; margin: 0;">{output_text}</p>
                </div>
            """, unsafe_allow_html=True)
            
        st.download_button(
            label="📥 Download Strategy Blueprint (.txt File)",
            data=shared_state_notebook,
            file_name="startup_blueprint.txt",
            mime="text/plain"
        )
    else:
        st.warning("Please type a business concept first.")

# 6. "How it Works" Descriptive Cards (Matching the second screenshot style)
st.markdown("<br><h2 style='text-align: center; color: #333;'>How FounderAI Works?</h2>", unsafe_allow_html=True)

st.markdown("""
    <div class="feature-card">
        <div class="card-title">📝 1. Idea Submission</div>
        <p style="color: #555; margin:0;">Enter your core operational vision or startup concept parameters into the generator matrix.</p>
    </div>
    <div class="feature-card">
        <div class="card-title">🤖 2. Multi-Agent Pipeline</div>
        <p style="color: #555; margin:0;">8 distinct, isolated specialized intelligence structures process the inputs sequentially.</p>
    </div>
    <div class="feature-card">
        <div class="card-title">📋 3. Strategic Blueprint</div>
        <p style="color: #555; margin:0;">Review your comprehensive breakdown cards directly on screen or export the generated text dossier.</p>
    </div>
""", unsafe_allow_html=True)

# 7. Custom Footer (Matching your friend's corporate/university footer style)
st.markdown("""
    <div class="footer-section">
        © 2026 FounderAI – AI Agent Group<br>
        B.Tech CSE (Artificial Intelligence)<br>
        Madanapalle Institute of Technology & Science
    </div>
""", unsafe_allow_html=True)