from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ml.fertilizer_predictor import predict_fertilizer


router = APIRouter(
    prefix="/fertilizer",
    tags=["Fertilizer Recommendation"]
)


class FertilizerRequest(BaseModel):
    temperature: float
    humidity: float
    moisture: float
    soil_type: str
    crop_type: str
    nitrogen: float
    potassium: float
    phosphorus: float


@router.post("/recommend")
def recommend_fertilizer(
    request: FertilizerRequest
):
    try:

        result = predict_fertilizer(
            temperature=request.temperature,
            humidity=request.humidity,
            moisture=request.moisture,
            soil_type=request.soil_type,
            crop_type=request.crop_type,
            nitrogen=request.nitrogen,
            potassium=request.potassium,
            phosphorus=request.phosphorus
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Fertilizer prediction failed: {str(e)}"
        )