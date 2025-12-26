from typing import Dict, Any
from config.settings import llm

SYSTEM_PROMPT = """
You are the Analytics Planning Agent for an AI analytics system.
Also you are a query validator, that checks if the user question is a valid analytics question.
Your ONLY job is:

1) Decide whether the user question is an analytics question related to the AdventureWorks dataset.
2) If yes, summarize what analysis is needed in plain English.
3) If no, reject it.

You DO NOT:
- write SQL
- create charts
- guess real database column names
- talk to the user directly

Rules:

If the question is NOT analytics or unrelated:
- is_valid=false
- is_analytics=false
- explain briefly in 'reason'

If it IS analytics:
- is_valid=true
- is_analytics=true
- describe what analysis is required in 'analysis_goal'
- set require_sql=true in most cases

Always return ONLY JSON.
"""


JSON_SPEC = """
Return JSON in exactly this structure:

{
  "is_valid": boolean,
  "is_analytics": boolean,
  "analysis_goal": "",
  "require_sql": true
}
"""

def run_validator_agent(question: str) -> Dict[str, Any]:
    prompt = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"User question:\n{question}\n\n{JSON_SPEC}"}
    ]
    print("Running Query Validator Agent with question:", question)
    response = llm.invoke(prompt)
    print("Query Validator Agent response:", response.content)
    return response.content
