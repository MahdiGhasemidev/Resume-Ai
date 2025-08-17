import streamlit as st
import yaml
from utils.pdf import extract_text_from_pdf
from utils.llm import parse_resume, review_resume
from resume_formatter import format_resume

def ensure_dict(obj):
    if isinstance(obj, dict):
        return obj
    return {}

def ensure_session_state_keys():
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = {}
    if 'review_data' not in st.session_state:
        st.session_state.review_data = {}
    if 'current_section' not in st.session_state:
        st.session_state.current_section = 0
    if 'sections' not in st.session_state:
        st.session_state.sections = []

def main():
    st.title(":page_facing_up: Resume Parser and Reviewer")
    st.sidebar.markdown(
        ":brain: ResumeAI is an advanced tool that leverages the power of Large Language Models (LLMs) to analyze and improve resumes."
    )

    ensure_session_state_keys()

    with st.sidebar:
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
        job_description = st.text_area("Enter job description (optional)").strip()

        if st.button("Run Analysis", use_container_width=True):
            if uploaded_file is not None:
                resume_text = extract_text_from_pdf(uploaded_file)
                st.subheader("Extracted Resume Text")
                st.text_area("Resume Text Preview", resume_text, height=200)

                # Parse resume
                with st.spinner("Parsing resume... [Step 1 of 2]"):
                    resume_yaml_raw = parse_resume(resume_text, debug=True)
                    st.subheader("Raw parse_resume YAML Output")
                    st.code(resume_yaml_raw, language="yaml")
                    resume_data = ensure_dict(yaml.safe_load(resume_yaml_raw) if resume_yaml_raw else {})

                if not resume_data:
                    st.warning("Warning: Resume parsing returned empty output.")

                # Review resume
                with st.spinner("Reviewing resume... [Step 2 of 2]"):
                    review_yaml_raw = review_resume(resume_data, job_description, debug=True)
                    st.subheader("Raw review_resume YAML Output")
                    st.code(review_yaml_raw, language="yaml")
                    review_data = ensure_dict(yaml.safe_load(review_yaml_raw) if review_yaml_raw else {})

                if not review_data:
                    st.warning("Warning: Resume review returned empty output.")

                # Ensure sections exist
                st.session_state.resume_data = resume_data
                st.session_state.review_data = review_data
                st.session_state.sections = list(resume_data.keys()) if resume_data else ["No Sections Found"]
                st.session_state.current_section = 0

                # Fill missing review sections with empty dicts
                for section in st.session_state.sections:
                    if section not in st.session_state.review_data:
                        st.session_state.review_data[section] = {
                            "impact_level": "Low",
                            "revision_suggestion": [],
                            "revised_content": ""
                        }

                display_analysis()
                return

    if st.session_state.sections:
        display_analysis()
    else:
        st.info("Please upload a resume and run the analysis to view results.")

def display_analysis():
    ensure_session_state_keys()

    if not st.session_state.sections:
        st.info("No sections to display.")
        return

    if st.session_state.current_section >= len(st.session_state.sections):
        st.session_state.current_section = 0

    col1, col2, col3 = st.columns([3, 1, 3])
    with col1:
        if st.button("⬅️", use_container_width=True) and st.session_state.current_section > 0:
            st.session_state.current_section -= 1
    with col2:
        page_number = f"{st.session_state.current_section + 1}/{len(st.session_state.sections)}"
        st.button(f"**{page_number}**", use_container_width=True)
    with col3:
        if st.button("➡️", use_container_width=True) and st.session_state.current_section < len(st.session_state.sections) - 1:
            st.session_state.current_section += 1

    current_section = st.session_state.sections[st.session_state.current_section]

    revision_suggestion_placeholder = st.empty()
    col1, col2 = st.columns(2)

    resume_data = ensure_dict(st.session_state.resume_data)
    review_data = ensure_dict(st.session_state.review_data)

    with col1:
        st.info(":x: **Original**")
        current_section_data = resume_data.get(current_section, "")
        st.info(format_resume({current_section: current_section_data}))

    with col2:
        st.success(":white_check_mark: **Revised**")
        current_review_data = ensure_dict(review_data.get(current_section, {}))
        impact_level = current_review_data.get('impact_level', "Low")
        revision_suggestion = current_review_data.get('revision_suggestion', [])
        revised_content = current_review_data.get('revised_content', "")
        st.success(format_resume({current_section: revised_content}))

    with revision_suggestion_placeholder.expander("Revision Suggestions", expanded=True):
        if impact_level == "Low":
            st.info(f"Impact Level: {impact_level}")
        elif impact_level == "Medium":
            st.warning(f"Impact Level: {impact_level}")
        elif impact_level == "High":
            st.error(f"Impact Level: {impact_level}")

        if isinstance(revision_suggestion, str):
            st.markdown(f"- {revision_suggestion}")
        elif isinstance(revision_suggestion, list):
            for suggestion in revision_suggestion:
                st.markdown(f"- {suggestion}")

if __name__ == "__main__":
    main()
