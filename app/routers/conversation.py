import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any

from app.models.schemas import (
    GenerateRequest, GenerateResponse, VerifyResponse, 
    GeneratedStarter, WikipediaFactCheck, LogEntry
)
from app.services.event_analyzer import extract_event_themes
from app.services.topic_generator import generate_topics
from app.services.fact_checker import fact_check
from app.services.history_logger import log_conversation, load_history
from app.services.feedback_logger import log_feedback, load_feedback_history
from app.services import data_store

router = APIRouter(prefix="/api/v1")

@router.post("/generate", response_model=GenerateResponse)
def generate_conversation_starters(request: GenerateRequest):
    """
    Orchestrates the conversation starter pipeline:
    1. Extracts themes from event description
    2. Generates smart conversation starters
    3. Saves session details to the database history
    """
    try:
        # Extract themes
        themes = extract_event_themes(request.EventDescription)
        
        # Generate topics
        interests = [interest.strip() for interest in request.Interests if interest.strip()]
        starters = generate_topics(themes, interests)
        
        # Format context prompt used for logging
        prompt_used = f"Themes: {themes}, Interests: {interests}"
        
        # Log session to database
        res_data = log_conversation(
            bio_text=request.BioText,
            event_desc=request.EventDescription,
            themes=themes,
            starters=starters,
            prompt_used=prompt_used
        )
        
        return GenerateResponse(
            SessionID=res_data["SessionID"],
            UserID=res_data["UserID"],
            EventID=res_data["EventID"],
            Themes=res_data["Themes"],
            Starters=res_data["Starters"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate starters: {str(e)}")


@router.get("/verify", response_model=VerifyResponse)
def verify_fact(
    query: str = Query(..., description="Query terms to verify on Wikipedia"),
    session_id: str = Query(..., description="Networking context session ID")
):
    """
    Performs Wikipedia verification check on query details.
    Saves verification audit details linked back to the session.
    """
    try:
        # Fetch from Wikipedia API
        check_result = fact_check(query)
        
        fact_check_id = str(uuid.uuid4())
        
        # Create fact check entry
        fc_entry = WikipediaFactCheck(
            FactCheckID=fact_check_id,
            SessionID=session_id,
            VerifiedQueryText=check_result["VerifiedQueryText"],
            VerificationStatus=check_result["VerificationStatus"],
            WikipediaSourceURL=check_result["WikipediaSourceURL"]
        )
        
        # Save to database
        data_store.save_wikipedia_fact_check(fc_entry)
        
        # Save audit log entry
        log_id = str(uuid.uuid4())
        log_entry = LogEntry(
            LogID=log_id,
            SessionID=session_id,
            ActionType="fact_check",
            PayloadJSON={
                "query": query,
                "status": check_result["VerificationStatus"],
                "url": check_result["WikipediaSourceURL"]
            },
            Timestamp=datetime.utcnow().isoformat()
        )
        data_store.save_log_entry(log_entry)
        
        return VerifyResponse(
            FactCheckID=fc_entry.FactCheckID,
            SessionID=fc_entry.SessionID,
            VerifiedQueryText=fc_entry.VerifiedQueryText,
            VerificationStatus=fc_entry.VerificationStatus,
            WikipediaSourceURL=fc_entry.WikipediaSourceURL,
            Extract=check_result["Extract"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fact check service error: {str(e)}")


@router.post("/feedback")
def submit_feedback(payload: Dict[str, Any]):
    """
    Receives user ratings ('like' or 'dislike') on a suggestion lines.
    """
    suggestion_text = payload.get("suggestion_text")
    action = payload.get("action")
    session_id = payload.get("session_id", "")
    starter_id = payload.get("starter_id", "")
    
    if not suggestion_text or not action:
        raise HTTPException(status_code=400, detail="Missing required field suggestion_text or action")
        
    if action not in ["like", "dislike"]:
        raise HTTPException(status_code=400, detail="Action must be 'like' or 'dislike'")
        
    try:
        feedback = log_feedback(
            suggestion_text=suggestion_text,
            action=action,
            session_id=session_id,
            starter_id=starter_id
        )
        return {"status": "success", "data": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def get_conversation_history():
    """
    Retrieves the chronological list of user networking sessions.
    """
    try:
        history = load_history()
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/history")
def get_feedback_history():
    """
    Retrieves the chronological list of user feedback actions.
    """
    try:
        history = load_feedback_history()
        return {"feedback": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
