# Technical Architecture - Personalized Networking Assistant

```mermaid
flowchart TD
    User[User] --> UI[Streamlit Web Application]
    UI --> Inputs[Profile, Event Description, Interests]
    UI --> Display[Generated Starters, Fact Results, History]
    Inputs --> API[FastAPI Backend Service]
    Display --> API

    API --> Router[Conversation Router]
    Router --> Analyzer[Event Analyzer Service]
    Router --> Generator[Topic Generator Service]
    Router --> FactChecker[Fact Checker Service]
    Router --> History[History Logger]
    Router --> Feedback[Feedback Logger]
    Router --> Logs[System Log Entry]

    Analyzer --> DistilBERT[DistilBERT or fallback theme extraction]
    Generator --> GPT2[GPT-2 or fallback starter generation]
    FactChecker --> Wikipedia[Wikipedia REST API]

    History --> Store[(Local JSON Data Store)]
    Feedback --> Store
    Logs --> Store
```

## Layers

- User interface: Streamlit app for inputs, generated suggestions, fact checks, history, and feedback.
- API layer: FastAPI routes with Pydantic validation and Swagger documentation.
- Service layer: Theme extraction, starter generation, fact verification, history logging, feedback logging, and audit logging.
- Storage layer: Local JSON files in `data/`.

