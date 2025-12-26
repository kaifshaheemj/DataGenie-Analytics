from langgraph.graph import StateGraph
from typing import TypedDict, Dict, Any
from agents.story_agent import run_story_agent
from agents.sql_agent import run_sql_agent

class StoryState(TypedDict):
    question: str
    story_plan: Dict[str, Any]
    sql_query: str

def story_agent_node(state: StoryState):
    plan = run_story_agent(state["question"])
    print("From Story Agent Node:")
    print("Generated Story Plan:", plan)
    return {"story_plan": plan}

def sql_agent_node(state):
    sql = run_sql_agent(state["story_plan"])
    print("From SQL Agent Node:")
    print("Generated SQL Query:", sql)

    return {"sql_query": sql}

graph = StateGraph(StoryState)

graph.add_node("story_agent", story_agent_node)
graph.add_node("sql_agent", sql_agent_node)

graph.set_entry_point("story_agent")
graph.add_edge("story_agent", "sql_agent")

story_graph = graph.compile()
