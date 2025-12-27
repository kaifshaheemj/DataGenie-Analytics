from config.settings import llm
from prompts.narrative_promt import NARRATIVE_SYSTEM_PROMPT as SYSTEM_PROMPT

def run_narrative_agent(question, df):
    user_prompt = f"""
    USER QUESTION:
    {question}

    DATA (first 10 rows):
    {df.head(10).to_markdown()}
    
    Write a business-friendly summary.
    """

    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])

    return response.content.strip()
