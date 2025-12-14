from fastapi import FastAPI
from .core.db import Base,engine
from .models import Base
from datetime import datetime
from .routers import user,whatsapp

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Basic Auth API",
    description="A simple authentication system",
    version="1.0.0"
)


app.include_router([user,whatsapp])

@app.get("/")
def root():
    return {"message": "Welcome to Basic Auth API"}

# Debug endpoint (optional)
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}




