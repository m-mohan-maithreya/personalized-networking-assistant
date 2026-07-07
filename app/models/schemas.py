from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Primary ER Entities

class UserProfile(BaseModel):
    UserID: str = Field(..., description="Unique ID for user profile")
    BioText: str = Field(..., description="User biography details and context")
    currentEventCache: Optional[str] = Field(None, description="Cached event info for current session")

class EventContext(BaseModel):
    EventID: str = Field(..., description="Unique ID for event context")
    EventDescription: str = Field(..., description="Details and textual description of the event")
    AnalyzedThemes: List[str] = Field(default_factory=list, description="List of NLP extracted themes")

class NetworkingSession(BaseModel):
    SessionID: str = Field(..., description="Unique ID for session")
    UserID: str = Field(..., description="Foreign key to UserProfile")
    EventID: str = Field(..., description="Foreign key to EventContext")
    SessionTimestamp: str = Field(..., description="ISO 8601 Timestamp of session creation")

class GeneratedStarter(BaseModel):
    StarterID: str = Field(..., description="Unique ID for conversation starter")
    SessionID: str = Field(..., description="Foreign key to NetworkingSession")
    StarterText: str = Field(..., description="AI generated conversation starter prompt text")
    ContextPromptUsed: str = Field(..., description="Exact context prompt passed to LLM")

class WikipediaFactCheck(BaseModel):
    FactCheckID: str = Field(..., description="Unique ID for Wikipedia factcheck")
    SessionID: str = Field(..., description="Foreign key to NetworkingSession")
    VerifiedQueryText: str = Field(..., description="Query sent for verification")
    VerificationStatus: str = Field(..., description="Status, e.g., 'verified' or 'disputed'")
    WikipediaSourceURL: str = Field(..., description="Source URL of Wikipedia article")

class LogEntry(BaseModel):
    LogID: str = Field(..., description="Unique ID for log entry")
    SessionID: Optional[str] = Field(None, description="Optional Foreign key to NetworkingSession")
    ActionType: str = Field(..., description="Type of action, e.g., 'generate_starter', 'fact_check'")
    PayloadJSON: Dict[str, Any] = Field(default_factory=dict, description="Detailed JSON audit payload")
    Timestamp: str = Field(..., description="Log timestamp")

# API Request and Response Models

class GenerateRequest(BaseModel):
    BioText: str = Field(..., description="User background/biography text")
    EventDescription: str = Field(..., description="Description of the networking event")
    Interests: List[str] = Field(..., description="List of user topics of interest")

class GenerateResponse(BaseModel):
    SessionID: str
    UserID: str
    EventID: str
    Themes: List[str]
    Starters: List[GeneratedStarter]

class VerifyRequest(BaseModel):
    SessionID: str
    Query: str

class VerifyResponse(BaseModel):
    FactCheckID: str
    SessionID: str
    VerifiedQueryText: str
    VerificationStatus: str
    WikipediaSourceURL: str
    Extract: str
