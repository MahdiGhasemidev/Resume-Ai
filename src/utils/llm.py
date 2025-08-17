import os
import requests
import streamlit as st
import google.generativeai as genai
from prompts import (
    RESUME_YAML_SCHEMA,
    LLM_YAML_PARSE_PROMPT,
    RESUME_REVIEW_PROMPT,
    JOB_DESCRIPTION_REVIEW_PROMPT,
    REVIEW_OUTPUT_SCHEMA,
)
from utils.yaml import extract_yaml


WORKER_URL = os.getenv("CWORKERS_GEMINI")



@st.cache_resource
def call_llm(prompt):
    response = requests.post(
        WORKER_URL,
        json={"prompt": prompt},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    data = response.json()
    # نمایش کامل داده برای دیباگ
    print("Raw Worker response:", data)
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return ""

def parse_resume(resume_text, debug=False):
    parse_prompt = LLM_YAML_PARSE_PROMPT.format(
        resume_schema=RESUME_YAML_SCHEMA, resume_text=resume_text
    )
    resume_yaml = call_llm(parse_prompt)
    if debug:
        print("parse_resume output:", resume_yaml)
    return resume_yaml

def review_resume(resume_yaml, job_description=None, debug=False):
    if job_description:
        review_prompt = JOB_DESCRIPTION_REVIEW_PROMPT.format(
            resume_data=resume_yaml,
            job_description=job_description,
            review_output_schema=REVIEW_OUTPUT_SCHEMA,
        )
    else:
        review_prompt = RESUME_REVIEW_PROMPT.format(
            resume_data=resume_yaml, review_output_schema=REVIEW_OUTPUT_SCHEMA
        )

    review_response = call_llm(review_prompt)
    if debug:
        print("review_resume output:", review_response)
    return review_response
