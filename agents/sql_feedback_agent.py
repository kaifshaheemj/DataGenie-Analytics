from config.settings import llm
from schema.schema_prompt import SQL_SCHEMA_PROMPT


SQL_FEEDBACK_SYSTEM = """
You are an expert SQL correction assistant.

You receive:
- the user's question
- the SQL query that failed
- the database schema
- the error message OR empty result signal

Your job: produce a BETTER SQL query.

Rules:
- Return ONLY JSON: { "sql": "..." }
- Never reuse invalid columns.
- Use only schema fields.
- Explain nothing.
"""

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
        {"role": "system", "content": SQL_FEEDBACK_SYSTEM},
        {"role": "user", "content": prompt}
    ])

    return resp.content
