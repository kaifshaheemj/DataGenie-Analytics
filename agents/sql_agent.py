from config.settings import llm
from schema.schema_loader import load_schema_text

SYSTEM_PROMPT = """
You are the SQL Agent for an AI analytics system.

Your job is to convert an analytics plan into SAFE PostgreSQL SQL.

RULES:
- Output ONLY SQL (no text around it).
- SELECT-only (no UPDATE, DELETE, INSERT, DROP).
- Use ONLY tables and columns from the provided schema.
- Prefer explicit JOINs.
- Use GROUP BY when aggregation is needed.
- If mapping is unclear, return: /* unable to generate SQL */
"""

def run_sql_agent(story_plan: dict):
    print("Running SQL Agent with story plan:", story_plan)
    schema_text = load_schema_text()

    user_prompt = f"""
        DATABASE SCHEMA (source of truth):
        {schema_text}

        TASK:
        Generate PostgreSQL SQL that answers this analytics plan:

        {story_plan}

        IMPORTANT:
        - Map logical terms (like "revenue", "customer", "category", "date")
        to the correct columns based on schema.
        - Revenue = order_quantity * dim_products.product_price
        - Profit = revenue - (order_quantity * dim_products.product_cost)

        Return ONLY SQL.
        """
    print("SQL Agent user content prepared.")
    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])
    print("SQL Agent response:", response.content)
    return response.content
