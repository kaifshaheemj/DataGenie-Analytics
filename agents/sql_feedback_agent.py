from config.settings import llm
from prompts.schema_prompt import SQL_SCHEMA_PROMPT
from prompts.sql_fallback_prompt import SQL_FALLBACK_SYSTEM

def run_sql_feedback_agent(question, sql, error):
    prompt = f"""
        QUESTION:
        {question}

        FAILED SQL:
        {sql}

        ERROR / ISSUE:
        {error}

        SCHEMA:
        {SQL_SCHEMA_PROMPT}

        Fix the SQL and return JSON only.
        """

    resp = llm.invoke([
        {"role": "system", "content": SQL_FALLBACK_SYSTEM},
        {"role": "user", "content": prompt}
    ])

    return resp.content
