from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class TipCalcState(TypedDict):
    bill: float
    adjustAmount: float
    operation: Literal["+", "-"]
    final_total: float

def get_user_input(state: TipCalcState) -> TipCalcState:
    print("Enter your total bill amount:")
    state["bill"] = float(input(">> "))

    print("Do you want to add tip (+) or apply a discount (-)?")
    op = input(">> ").strip()
    if op not in {"+", "-"}:
        print("⚠️ Invalid operation, defaulting to '+'")
        op = "+"
    state["operation"] = op

    print("Enter the tip or discount amount:")
    state["adjustAmount"] = float(input(">> "))
    return state

def apply_tip(state: TipCalcState) -> TipCalcState:
    state["final_total"] = state["bill"] + state["adjustAmount"]
    print(f"💰 Final total after adding tip: ${state['final_total']:.2f}")
    return state

def apply_discount(state: TipCalcState) -> TipCalcState:
    state["final_total"] = state["bill"] - state["adjustAmount"]
    print(f"💸 Final total after discount: ${state['final_total']:.2f}")
    return state

builder = StateGraph(TipCalcState)

builder.add_node("input", get_user_input)
builder.add_node("tip", apply_tip)
builder.add_node("discount", apply_discount)

builder.set_entry_point("input")

def get_operation(state):
    return state["operation"]

builder.add_conditional_edges(
    "input",
    get_operation,  # using the named function
    {
        "+": "tip",
        "-": "discount"
    }
)

builder.add_edge("tip", END)
builder.add_edge("discount", END)

graph = builder.compile()

# invoke with default values
graph.invoke({"bill": 0, "modifier": 0, "operation": "+", "final_total": 0})









