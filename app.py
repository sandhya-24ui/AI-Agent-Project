            if mode == "Live Gemini AI":
                with st.spinner(
                    "FounderAI is preparing the specialist analysis. "
                    "Gemini may take up to a few minutes..."
                ):
                    prompt = build_prompt(
                        idea.strip(),
                        target_customer.strip(),
                        budget.strip(),
                        location.strip(),
                    )
                    outputs = call_gemini(prompt)
                st.session_state["founderai_results"] = outputs
                st.session_state["founderai_mode"] = "Live Gemini AI"
                st.session_state["founderai_idea"] = idea.strip()
                st.success("Live Gemini analysis completed successfully.")
            else:
                outputs = build_demo_results(idea.strip())
                st.session_state["founderai_results"] = outputs
                st.session_state["founderai_mode"] = "Demonstration Mode — simulated examples"
                st.session_state["founderai_idea"] = idea.strip()
                st.info(
                    "Demonstration Mode is active. The following outputs are "
                    "illustrative examples, not live AI-generated analysis."
                )

        except Exception as exc:
            st.error(f"FounderAI could not complete the analysis: {exc}")
            st.caption(
                "Check the Streamlit app logs and Gemini API model availability. "
                "You can use Demonstration Mode for an offline review demo."
            )

# ---------------------------------------------------------
# Display saved results and blueprint download
# ---------------------------------------------------------
if st.session_state.get("founderai_results"):
    outputs = st.session_state["founderai_results"]
    result_idea = st.session_state.get("founderai_idea", idea)
    result_mode = st.session_state.get("founderai_mode", "Unknown")

    st.divider()
    st.subheader("📊 Specialist Analysis")
    st.caption(f"Concept: {result_idea}")
    if result_mode.startswith("Demonstration"):
        st.warning(
            "DEMONSTRATION OUTPUT — These are illustrative examples, "
            "not live AI-generated results."
        )
    else:
        st.success("Live AI-generated analysis")

    for index, (name, _) in enumerate(AGENT_ROLES, start=1):
        with st.container(border=True):
            st.markdown(
                f'<div class="agent-title">🤖 Agent {index}: {name}</div>',
                unsafe_allow_html=True,
            )
            st.write(outputs.get(name, "No analysis available."))

    blueprint = make_blueprint(
        result_idea,
        target_customer,
        budget,
        location,
        outputs,
        result_mode,
    )
    st.download_button(
        "📥 Download Startup Blueprint (.md)",
        data=blueprint,
        file_name="founderai_startup_blueprint.md",
        mime="text/markdown",
        use_container_width=True,
    )

# ---------------------------------------------------------
# How it works and footer
# ---------------------------------------------------------
st.divider()
st.subheader("How FounderAI Works")
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown("### 1. 💡 Idea submission")
    st.write("Describe the startup concept, target customer, budget, and market.")
with col_b:
    st.markdown("### 2. 🤖 Specialist analysis")
    st.write("Eight defined specialist perspectives analyze the business concept.")
with col_c:
    st.markdown("### 3. 📋 Strategy blueprint")
    st.write("Review the analysis and export a structured startup blueprint.")

st.markdown(
    """
    <div style="text-align:center; padding:22px 8px; margin-top:20px;
                background:#0d6efd; color:white; border-radius:10px;">
      <strong>© 2026 FounderAI — AI Agent</strong><br>
      B.Tech CSE (Artificial Intelligence)<br>
      Madanapalle Institute of Technology & Science
    </div>
    """,
    unsafe_allow_html=True,
)
