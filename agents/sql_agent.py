from config.settings import llm
from schema.schema_prompt import SQL_SCHEMA_PROMPT
import json

MAX_RETRIES = 3

def run_sql_agent(validator: dict):
    print("Running SQL Agent with story plan:")

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n--- SQL Agent Attempt {attempt} ---")

        user_prompt = f"""
            DATABASE SCHEMA:
            {SQL_SCHEMA_PROMPT}

            TASK:
            Generate PostgreSQL SQL for this analytics plan:

            {validator}

            Return ONLY valid JSON:
            {{
            "sql": "<query>"
            }}
            """
        response = llm.invoke([
            {"role": "system", "content": "You generate SQL only following instructions strictly."},
            {"role": "user", "content": user_prompt}
        ])

        text = response.content.strip()
        print("Raw model output:\n", text)

        # Remove fences if present
        if text.startswith("```"):
            text = (
                text.replace("```json", "")
                    .replace("```sql", "")
                    .replace("```", "")
                    .strip()
            )

        # Try parse JSON safely
        try:
            data = json.loads(text)
        except Exception as e:
            print("JSON parse failed:", e)
            continue   # retry

        sql = (data.get("sql") or "").strip()

        # if model returned empty / null sql → retry
        if not sql or sql.lower() == "null" or "unable" in sql.lower():
            print("Model returned null/invalid SQL — retrying...")
            continue

        print("SQL Agent produced valid SQL.")
        return sql

    # After retries failed
    print("SQL Agent failed after retries.")
    return "/* unable to generate SQL */"
