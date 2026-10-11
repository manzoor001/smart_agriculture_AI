from fastapi import APIRouter, File, UploadFile, HTTPException
from PIL import Image
import io

from app.services.disease_prediction import predict_disease


router = APIRouter(
    prefix="/disease",
    tags=["Disease Prediction"]
)


@router.post("/predict")
async def predict_plant_disease(
    file: UploadFile = File(...)
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid image file."
        )

    try:
        contents = await file.read()

        image = Image.open(io.BytesIO(contents))

        result = predict_disease(image)

        return {
            "filename": file.filename,
            "predicted_disease": result["predicted_disease"],
            "confidence": round(result["confidence"], 4)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image prediction failed: {str(e)}"
        )
