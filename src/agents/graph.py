from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.agents import planner_node, coder_node, critic_node, should_continue

def build_graph():
    """Builds the LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    workflow.add_node("planner", planner_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("critic", critic_node)
    
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "coder")
    workflow.add_edge("coder", "critic")
    
    workflow.add_conditional_edges(
        "critic",
        should_continue,
        {
            "end": END,
            "coder": "coder"
        }
    )
    
    return workflow.compile()