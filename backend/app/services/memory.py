from langchain_core.messages import HumanMessage, AIMessage
from app.models.chat import ChatMemory

def load_memory(db, chat_id):
    records = db.query(ChatMemory).filter_by(chat_id=chat_id).order_by(ChatMemory.created_at).all()
    messages = []

    for r in records:
        if r.role == "human":
            messages.append(HumanMessage(content=r.content))
        else:
            messages.append(AIMessage(content=r.content))

    return messages

def save_message(db, chat_id, role, content):
    db.add(ChatMemory(chat_id=chat_id, role=role, content=content))
    db.commit()
