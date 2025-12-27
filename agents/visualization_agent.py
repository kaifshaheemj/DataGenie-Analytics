from config.settings import llm
from agents.query_validator_agent import SYSTEM_PROMPT
from typing import Dict, Any
from prompts.visualization_prompt import VISUALIZATION_SYSTEM_PROMPT

def run_visualization_agent(analysis_goal: str, sample_data: str, columns: str) -> str:
    print("Running Visualization Agent with analysis goal:")

    prompt = f"""
        ANALYSIS GOAL:
        {analysis_goal}

        SAMPLE DATA (head):
        {sample_data}

        COLUMNS:
        {columns}

        Generate Python Plotly code to create the best visualization.
        """

    response = llm.invoke([
        {"role": "system", "content": VISUALIZATION_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ])

    visual_json = response.content
    print("Raw model output:\n", visual_json)
    print("Visualization Agent produced code.")
    return visual_json