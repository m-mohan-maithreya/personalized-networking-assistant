# Running instructions: Personalized Networking Assistant

Follow the instructions below to run the app local servers and tests.

## Setup Requirements

1. **Python**: Python 3.9+ (Python 3.13 is fully tested and verified).
2. **Environment**: Recommended to set active workspace to the project folder:
   `C:\Users\srini\.gemini\antigravity\scratch\personalized_networking_assistant`

## Run instructions

### 1. Activate Virtual Environment
Open PowerShell inside the project directory and run:
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Launch FastAPI Backend
From the virtual environment shell:
```powershell
python -m uvicorn app.main:app --port 8000
```
- API will be listening on `http://127.0.0.1:8000`
- Interactive API Docs: `http://127.0.0.1:8000/docs`

### 3. Launch Streamlit UI Frontend
In a **new terminal tab** with the virtual environment activated:
```powershell
python -m streamlit run frontend/app.py --server.port 8501
```
- Streamlit will open automatically at: `http://localhost:8501`

---

## Testing & Validation

### Run Pytest Suite
To run all unit tests, integration paths, and check coverage:
```powershell
python -m pytest --cov=app tests/
```

### Programmatic E2E Verification
To test connections, AI pipeline predictions, and DB persistence transactions, run the testing script:
```powershell
python tests/run_e2e_verification.py
```
