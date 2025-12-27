from config.settings import llm
from prompts.schema_prompt import SQL_SCHEMA_PROMPT
from prompts.dashboard_prompt import DASHBOARD_SYSTEM_PROMPT as SYSTEM_PROMPT
import json

def run_dashboard_agent(user_question: str):
    prompt = f"""
        DATABASE CONTEXT (source of truth):

        {SQL_SCHEMA_PROMPT}

        USER REQUEST (high-level intent):
        "{user_question}"
        TASK:
        Break this request into 5–7 CXO dashboard questions that together explain:

        - What is happening?
        - Why is it happening?
        - Where are opportunities or risks?

        Make sure:
        - Each question is clearly measurable
        - Each question can be solved using tables in this schema
        - Questions are ordered logically (top-down story)

        OUTPUT FORMAT (IMPORTANT):
        questions:[
        "Question 1",
        "Question 2",
        "Question 3"
        ]
        """

    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ])
    print("Dashboard Agent response:", response.content)
    return response.content
