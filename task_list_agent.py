from typing import Annotated, Sequence, TypedDict, List, Dict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()

# { description: str, done: bool }
tasks: List[Dict[str, bool]] = []

###{"description": "Buy groceries", "done": False}

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def add_task(description: str) -> str:
    """Add a new task to the to-do list."""
    tasks.append({"description": description, "done": False})
    return show_task_list()

@tool
def mark_done(index: int) -> str:
    """Mark a task as done by its number (starting from 1)."""
    if 1 <= index <= len(tasks):
        tasks[index - 1]["done"] = True
        return show_task_list()
    return "❌ Invalid task number."

@tool
def save_tasks(filename: str) -> str:
    """Save all tasks to a text file and end the session."""
    if not filename.endswith(".txt"):
        filename += ".txt"
    try:
        with open(filename, "w") as f:
            f.write(show_task_list())
        return f"✅ Tasks saved to '{filename}'."
    except Exception as e:
        return f"❌ Failed to save tasks: {str(e)}"
    
def show_task_list() -> str:
    if not tasks:
        return "📋 No tasks yet."
    return "\n".join(
        [f"{i+1}. [{'✔' if t['done'] else ' '}] {t['description']}" for i, t in enumerate(tasks)]
    )

tools = [add_task, mark_done, save_tasks]

model = ChatOpenAI(model="gpt-5").bind_tools(tools)

def task_agent(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
    You are a helpful personal task manager assistant.
    
    - Use 'add_task' to add tasks.
    - Use 'mark_done' to check off completed ones.
    - Use 'save_tasks' when the user is finished.

    Here’s the current to-do list:\n\n{show_task_list()}
    """)

    if not state["messages"]:
        user_input = "Welcome! What task would you like to add first?"
        user_message = HumanMessage(content=user_input)
    else:
        user_input = input("\n📝 Your input: ")
        print(f"\n👤 USER: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]
    response = model.invoke(all_messages)

    print(f"\n🤖 AI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"🔧 TOOLS USED: {[tc['name'] for tc in response.tool_calls]}")

    return {"messages": list(state["messages"]) + [user_message, response]}

def should_continue(state: AgentState) -> str:
    for message in reversed(state["messages"]):
        if isinstance(message, ToolMessage) and "saved" in message.content.lower():
            return "end"
    return "continue"

def print_messages(messages):
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\n🛠️ TOOL RESULT: {message.content}")
            break

graph = StateGraph(AgentState)

graph.add_node("agent", task_agent)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("agent")

graph.add_edge("agent", "tools")

graph.add_conditional_edges("tools", should_continue, {
    "continue": "agent",
    "end": END
})

app = graph.compile()

def run_task_manager():
    print("\n===== ✅ PERSONAL TASK MANAGER =====")
    state = {"messages": []}
    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
print("\n===== 🎉 DONE MANAGING TASKS =====")

if __name__ == "__main__":
    run_task_manager()














