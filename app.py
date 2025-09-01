# app.py
from pathlib import Path
from typing import Dict, Any
import numpy as np
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent
BUNDLE_PATH = ROOT / "model" / "heart-disease-v1.joblib"

# Carga del bundle (soporta modelo solo o dict {"model":..., "features":[...]})
bundle = joblib.load(BUNDLE_PATH)
if isinstance(bundle, dict) and "model" in bundle:
    model = bundle["model"]
    feature_names = bundle.get("features")
else:
    model = bundle
    feature_names = None

origins = ["*"]

app = FastAPI(title="Heart Disease Prediction")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    age: int
    sex: int
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int

class OutputData(BaseModel):
    score: float

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/score", response_model=OutputData)
def score(data: InputData):
    # Pydantic v1: .dict(); v2: .model_dump()
    payload: Dict[str, Any] = data.dict() if hasattr(data, "dict") else data.model_dump()

    # Si entrenaste guardando "features", respetamos ese orden
    if feature_names:
        missing = [f for f in feature_names if f not in payload]
        if missing:
            raise HTTPException(status_code=400, detail=f"Faltan campos: {missing}")
        x = [[payload[f] for f in feature_names]]
    else:
        # Fallback (menos recomendado porque el orden no está garantizado)
        x = [[payload[k] for k in payload.keys()]]

    proba = model.predict_proba(np.array(x))[:, -1][0]
    return {"score": float(proba)}

