from pydantic import BaseModel


class YieldPredictionRequest(BaseModel):
    year: int
    region: str
    crop: str
    season: str
    temperature: float
    rainfall: float
    humidity: float
    soil_type: str
    ph: float
    nitrogen: float
    phosphorus: float
    potassium: float
    fertilizer: float
    pesticide: float


class YieldPredictionResponse(BaseModel):
    success: bool
    predicted_yield: float