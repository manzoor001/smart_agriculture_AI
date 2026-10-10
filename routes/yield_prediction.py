from fastapi import APIRouter, HTTPException

from app.schemas.yield_prediction import (
    YieldPredictionRequest,
    YieldPredictionResponse
)

from app.services.yield_prediction import predict_yield


router = APIRouter(
    prefix="/yield",
    tags=["Yield Prediction"]
)


@router.post(
    "/predict",
    response_model=YieldPredictionResponse
)
def predict_crop_yield(request: YieldPredictionRequest):

    try:
        predicted_yield = predict_yield(request)

        return {
            "success": True,
            "predicted_yield": predicted_yield
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Yield prediction failed: {str(e)}"
        )