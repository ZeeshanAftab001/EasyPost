from langgraph.graph import StateGraph,START,END
from typing import TypedDict,List
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv

load_dotenv()
# -----------------------------
class ChatState(TypedDict):
    tenant_id: int
    user_id: int
    chat_id: str
    messages: List[BaseMessage]

# -----------------------------
# LLM NODE
# -----------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.4
)

def chat_node(state: ChatState):
    response = llm.invoke(state["messages"])
    return {
        "messages": state["messages"] + [response]
    }

# -----------------------------
# GRAPH
# -----------------------------
graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.set_entry_point("chat")
graph.add_edge("chat", END)

# -----------------------------
# CHECKPOINTER
# -----------------------------
checkpointer = SqliteSaver("checkpoints.sqlite")
agent = graph.compile(checkpointer=checkpointer)


