from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.conversation import router as conversation_router

app = FastAPI(
    title="Personalized Networking Assistant API",
    description="Backend services for extracting event themes, generating conversation starters, and performing factchecks.",
    version="1.0.0"
)

# Enable CORS for frontend UI interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register our primary REST router
app.include_router(conversation_router)

@app.get("/")
def read_root():
    """
    Health check route to verify the FastAPI backend is running.
    """
    return {
        "status": "healthy",
        "service": "Personalized Networking Assistant API",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
