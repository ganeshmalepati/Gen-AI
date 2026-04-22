from typing import TypedDict, List
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    name: str
    values: List[int]
    result: str

def ask_name(state: AgentState) -> AgentState:
    """
    Prompts the user for their name and updates the shared state.
    """
    print("Welcome to Budget Analyzer!")
    print("What's your name?")
    state["name"] = input(">> ")
    return state

def ask_values(state: AgentState) -> AgentState:
    """
    Prompts the user to enter a list of recent purchase amounts and updates the state.
    """
    print(f"Hi {state['name']}! Enter last 5 financial transactions (separated by commas):")
    raw = input(">> ")
    try:
        values = [int(v.strip()) for v in raw.split(",") if v.strip()]
        if len(values) < 1: ### values = [10, 20, 30, -15, -5]
            raise ValueError()
    except ValueError:
        print("⚠️ Please enter only valid numbers separated by commas.")
        return ask_values(state)
    state["values"] = values
    return state

def analyze_and_report(state: AgentState) -> AgentState:
    """
    Calculates total spending, classifies the user as a Saver or Spender,
    stores the result, and prints a summary message.
    """
    total = sum(state["values"])
    result = "Saver" if total > 0 else "Spender"
    state["result"] = result

    print("\n📊 Budget Summary")
    print(f"Name: {state['name']}")
    print(f"Total Spent: ${total}")
    print(f"Result: You are a {result}!")

    return state

graph = StateGraph(AgentState)

graph.add_node("ask_name", ask_name)
graph.add_node("ask_values", ask_values)
graph.add_node("analyze_and_report", analyze_and_report)

graph.set_entry_point("ask_name")
graph.add_edge("ask_name", "ask_values")
graph.add_edge("ask_values", "analyze_and_report")
graph.add_edge("analyze_and_report", END)

compiled_graph = graph.compile()

# Optional: Visualize the graph structure
print(compiled_graph.get_graph().draw_ascii())

# Run the graph
compiled_graph.invoke({})




