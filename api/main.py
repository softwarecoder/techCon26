from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import json

# Import your existing logic
from engine.scoring import ScoringEngine
from engine.predictor import PredictorEngine
from engine.optimizer import OptimizerEngine
from ai_agent.rag_pipeline import AIAgent

app = FastAPI(title="Smart Banker AI API", version="1.0.0")

# --- DATA MODELS (Pydantic) ---
# These define exactly what the API expects to receive

class Transaction(BaseModel):
    date: str
    amount: float
    category: str
    merchant: str
    type: str  # 'Income' or 'Expense'

class UserData(BaseModel):
    profile: dict
    debt: dict
    transactions: List[Transaction]

class ChatRequest(BaseModel):
    query: str
    openai_api_key: Optional[str] = None
    # The API needs the summary to ground the RAG
    fhs_score: float
    current_balance: float
    predicted_balance: float
    debt_status: str
    top_category: str

# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Banker AI API. Go to /docs for Swagger UI."}

@app.post("/analyze")
async def analyze_finances(data: UserData):
    """
    Takes raw user data and returns the calculated 
    Health Score, Predictions, and Debt Optimization.
    """
    try:
        # 1. Convert Pydantic models to Pandas DataFrame
        df = pd.DataFrame([t.dict() for t in data.transactions])
        df['date'] = pd.to_datetime(df['date'])
        
        # 2. Initialize Engines
        scoring = ScoringEngine(df, data.debt, data.profile)
        predictor = PredictorEngine(df)
        optimizer = OptimizerEngine(data.debt)

        # 3. Run Calculations
        fhs = scoring.calculate_fhs()
        prediction = predictor.predict_cash_flow()
        debt_plan = optimizer.get_debt_recommendations()

        return {
            "financial_health": fhs,
            "cash_flow_prediction": prediction,
            "debt_optimization": debt_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_coach(request: ChatRequest):
    """
    The "Voice" endpoint. Takes a user question and 
    returns an AI response grounded in RAG.
    """
    try:
        # 1. Prepare the context for the RAG
        ai_context = {
            "fhs_score": request.fhs_score,
            "current_balance": request.current_balance,
            "predicted_balance": request.predicted_balance,
            "debt_status": request.debt_status,
            "top_category": request.top_category
        }

        # 2. Initialize the AI Agent
        agent = AIAgent(openai_api_key=request.openai_api_key)
        
        # 3. Setup Knowledge Base (In production, this would be pre-loaded)
        # We assume the file exists in the root
        agent.setup_knowledge_base("financial_knowledge.txt")

        # 4. Get Response
        response = agent.chat(request.query, ai_context)

        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- TO RUN THIS: uvicorn api.main:app --reload ---
