from langgraph.graph import StateGraph
from typing import TypedDict, Dict, Any
from agents.query_validator_agent import run_validator_agent
from agents.sql_agent import run_sql_agent

class StoryState(TypedDict):
    question: str
    validator: Dict[str, Any]
    sql_query: str

def query_validator_node(state: StoryState):
    plan = run_validator_agent(state["question"])
    # print("From Query Validator Node:")
    # print("Generated Query Validation Plan:", plan)
    return {"validator": plan}

def sql_agent_node(state):
    sql = run_sql_agent(state["validator"])
    print("From SQL Agent Node:")
    return {"sql_query": sql}

graph = StateGraph(StoryState)

graph.add_node("query_validator", query_validator_node)
graph.add_node("sql_agent", sql_agent_node)

graph.set_entry_point("query_validator")
graph.add_edge("query_validator", "sql_agent")
agents_graph = graph.compile()
