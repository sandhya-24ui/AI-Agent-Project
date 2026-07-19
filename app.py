import streamlit as st
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="FounderAI", page_icon="🚀", layout="wide")
st.title("🚀 FounderAI: 8-Agent Startup Blueprint")
st.write("Your business idea is sequentially analyzed through an assembly line of 8 specialized AI agents.")

use_simulation = st.checkbox("💡 Run in Demonstration Mode (Bypasses Google API Key Verification errors)", value=True)

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

if st.button("Generate Complete Strategy"):
    if user_prompt:
        shared_state_notebook = f"=========================================\n🚀 FOUNDERAI: STARTUP STRATEGY BLUEPRINT\n=========================================\n\nInitial Startup Concept: {user_prompt}\n\n-----------------------------------------\n"
        status_box = st.empty()
        
        if use_simulation:
            for agent_name, fixed_text in agent_roles.items():
                status_box.info(f"⚙️ {agent_name} is processing data matrix...")
                time.sleep(0.3) 
                shared_state_notebook += f"👔 {agent_name} Report\n- {fixed_text}\n\n"
        else:
            if not api_key or api_key.strip() == "":
                st.error("❌ API key empty! Please check your .env file or enable Demonstration Mode above.")
                st.stop()
                
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key.strip()}"
            headers = {"Content-Type": "application/json"}
            
            for agent_name, instruction in agent_roles.items():
                status_box.info(f"⚙️ {agent_name} is requesting remote server analysis...")
                full_prompt = f"Role context: {instruction}\n\nAnalyze this business concept: {user_prompt}\n\nContext:\n{shared_state_notebook}"
                payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
                
                try:
                    response = requests.post(url, headers=headers, json=payload)
                    response_data = response.json()
                    
                    if 'candidates' in response_data:
                        agent_output = response_data['candidates'][0]['content']['parts'][0]['text']
                        agent_output = agent_output.replace('•', '-').replace('▪', '-').replace('◦', '-')
                        shared_state_notebook += f"👔 {agent_name} Report\n{agent_output}\n\n"
                    else:
                        error_msg = response_data.get('error', {}).get('message', 'Billing/Project activation required.')
                        st.error(f"❌ Google Server Response: {error_msg}")
                        st.stop()
                except Exception as e:
                    st.error(f"Network error during {agent_name}: {str(e)}")
                    st.stop()
                    
        status_box.empty()
        st.success("✅ Success! Your multi-agent dossier has compiled.")
        
        # Display the blueprint directly on screen
        st.subheader("📄 Your Generated Startup Dossier Blueprint")
        st.markdown(shared_state_notebook)
        
        st.markdown("---")
        
        # ADDED DOWNLOAD ACTION HOOK FOR THE CLIENT:
        st.download_button(
            label="📥 Download Strategy Blueprint (.txt File)",
            data=shared_state_notebook,
            file_name="startup_strategy_blueprint.txt",
            mime="text/plain"
        )
        
    else:
        st.warning("Please type a business concept first.")