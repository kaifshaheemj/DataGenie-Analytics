from config.settings import llm
from agents.query_validator_agent import SYSTEM_PROMPT
from typing import Dict, Any

VISUALIZATION_SYSTEM_PROMPT = """
    You are the Visualization Agent.

    Your task:
    Given a dataset sample and analysis goal,
    decide the best visualization and mapping.

    You DO NOT:
    - write SQL
    - execute code
    - return Python code
    - hallucinate columns that don't exist

    Return ONLY JSON in this format:

    {
    "chart_type": "bar | line | pie | area",
    "x": "<column_name>",
    "y": "<column_name>",
    "title": "<chart title>"
    }
    """

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