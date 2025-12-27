from langgraph.graph import StateGraph
from typing import TypedDict, Dict, Any
from agents.query_validator_agent import run_validator_agent
from agents.sql_agent import run_sql_agent
import json
import re


class StoryState(TypedDict, total=False):
    question: str
    validator: Dict[str, Any]
    sql_query: str | None
    response: str | None


def clean_json(text: str) -> str:
    if not text:
        return "{}"

    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"```[a-zA-Z]*", "", text)
        text = text.replace("```", "").strip()

    return text


def query_validator_node(state: StoryState):
    raw = run_validator_agent(state["question"])
    print("\nRAW VALIDATOR OUTPUT:", repr(raw))

    cleaned = clean_json(raw)
    plan = json.loads(cleaned)

    return {**state, "validator": plan}


def sql_agent_node(state: StoryState):
    sql = run_sql_agent(state["validator"])
    print("From SQL Agent Node:")

    return {**state, "sql_query": sql}


def non_analytics_node(state: StoryState):
    validator = state["validator"]

    msg = (
        "This question is not related to analytics.\n"
        f"Reason: {validator.get('analysis_goal') or validator.get('reason','')}"
    )

    print(msg)

    # 🔥 keep state + store final response
    return {**state, "response": msg}


def route_after_validation(state: StoryState):
    validator = state["validator"]

    if not validator.get("is_valid") or not validator.get("is_analytics"):
        return "non_analytics"

    return "sql_agent"


graph = StateGraph(StoryState)

graph.add_node("query_validator", query_validator_node)
graph.add_node("sql_agent", sql_agent_node)
graph.add_node("non_analytics", non_analytics_node)

graph.set_entry_point("query_validator")

graph.add_conditional_edges(
    "query_validator",
    route_after_validation,
    {
        "sql_agent": "sql_agent",
        "non_analytics": "non_analytics",
    },
)

agents_graph = graph.compile()
