"""Small advisory API for the saved course model."""
from pathlib import Path
import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field

MODEL_PATH = Path(__file__).parent / "model_artifacts" / "delivery_risk_model.joblib"
app = FastAPI(title="Olist Delivery Risk Advisory API", version="1.0.0")
model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None


class OrderFeatures(BaseModel):
    estimated_lead_days: float = Field(ge=0, le=365)
    item_count: int = Field(ge=1, le=100)
    basket_value: float = Field(ge=0, le=100000)
    freight_value: float = Field(ge=0, le=100000)
    category: str = "Unknown"
    customer_region: str = "Unknown"
    seller_region: str = "Unknown"
    purchase_month: str = "1"
    purchase_weekday: str = "0"
    purchase_hour: str = "12"


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None, "mode": "advisory"}


@app.post("/predict")
def predict(order: OrderFeatures):
    if model is None:
        return {"error": "Model artifact not found. Run train.py first."}
    row = order.model_dump()
    import pandas as pd
    probability = float(model.predict_proba(pd.DataFrame([row]))[0, 1])
    return {
        "late_delivery_probability": round(probability, 4),
        "risk_flag_at_0_50": bool(probability >= 0.5),
        "threshold": 0.5,
        "use_limit": "Human review only; not a customer or seller decision.",
    }
