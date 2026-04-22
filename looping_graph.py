from langgraph.graph import StateGraph, END
from typing import TypedDict

class AuthState(TypedDict):
    attempt: int
    authenticated: bool

CORRECT_PASSWORD = "secure123"

def get_password(state: AuthState) -> AuthState:
    print(f"Attempt {state['attempt'] + 1} - Enter your password:")
    pw = input(">> ")
    state["attempt"] += 1
    state["authenticated"] = pw == CORRECT_PASSWORD
    return state

def success_node(state: AuthState) -> AuthState:
    print("✅ Access granted!")
    return state

def check_auth(state: AuthState) -> str:
    return "success" if state["authenticated"] else "retry"

builder = StateGraph(AuthState)

builder.add_node("get_password", get_password)
builder.add_node("success", success_node)

builder.set_entry_point("get_password")

# Retry loop until correct password is entered
builder.add_conditional_edges(
    "get_password",
    check_auth,
    {
        "success": "success", # proceed to end the graph
        "retry": "get_password" # self-loop back to same node
    }
) 

builder.add_edge("success", END)

# Compile and run
graph = builder.compile()

graph.invoke({
    "attempt": 0,  
    "authenticated": False
})


