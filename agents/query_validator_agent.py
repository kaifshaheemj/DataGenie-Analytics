from typing import Dict, Any
from config.settings import llm
from prompts.validator_prompt import VALIDATOR_SYSTEM_PROMPT as SYSTEM_PROMPT

JSON_SPEC = """
Return ONLY JSON in this format:

{
  "is_valid": boolean,
  "is_analytics": boolean,
  "analysis_goal": "",
  "require_sql": true,
  "visualization": true,
  "dashboard": false
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
