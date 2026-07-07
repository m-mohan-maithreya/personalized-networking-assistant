# Personalized Networking Assistant

An AI-powered web application that helps users generate smart, tailored conversation starters for professional or social networking events. 

The application uses **DistilBERT** for zero-shot theme extraction from event descriptions and **GPT-2** for generating context-aware conversation prompts. It coordinates with **Wikipedia Search & REST APIs** to check and verify topics of interest.

## Features
- **Smart Starter Generator**: Extracts event themes and combines them with user interests to generate 3 tailored icebreakers.
- **Wikipedia Fact Verification**: Probes Wikipedia page content extracts and sources URL in real time.
- **Interactive Feedback System**: Captures user ratings (thumbs-up/thumbs-down) on generated suggestions.
- **History & Auditing Audit**: Persistent JSON file-based database for User Profiles, Event Contexts, Sessions, Starters, Fact-Checks, and System logs.

## Project Structure
```
personalized_networking_assistant/
│
├── app/
│   ├── main.py                     # FastAPI Entrypoint
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py              # Pydantic schemas (ER entities)
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── conversation.py         # API REST Endpoints
│   │
│   └── services/
│       ├── __init__.py
│       ├── data_store.py           # Persistent JSON DB layer
│       ├── event_analyzer.py       # DistilBERT classifier service
│       ├── fact_checker.py         # Wikipedia factchecker service
│       ├── feedback_logger.py      # Likes/dislikes logger service
│       ├── history_logger.py       # Session history logger service
│       └── topic_generator.py      # GPT-2 small generative service
│
├── frontend/
│   └── app.py                      # Streamlit UI Interface
│
├── tests/                          # Pytest Unit & Integration tests
│   ├── test_analyzer.py
│   ├── test_checker.py
│   ├── test_generator.py
│   └── test_routes.py
│
├── requirements.txt                # Python package list
└── RUNNING.md                      # Details on environment & run commands
```

## Running the Application
Refer to [RUNNING.md](./RUNNING.md) for details on launching the FastAPI backend and Streamlit frontend.
