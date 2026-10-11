from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.soil_data import SoilData
from app.models.user import User
from app.schemas.soil_data import SoilDataCreate, SoilDataResponse
from app.auth.security import get_current_user


router = APIRouter(
    prefix="/soil",
    tags=["Soil Data"]
)


@router.post("/", response_model=SoilDataResponse)
def create_soil_data(
    soil_data: SoilDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_soil_data = SoilData(
        crop_name=soil_data.crop_name,
        nitrogen=soil_data.nitrogen,
        phosphorus=soil_data.phosphorus,
        potassium=soil_data.potassium,
        ph=soil_data.ph,
        farmer_id=current_user.id
    )

    db.add(new_soil_data)
    db.commit()
    db.refresh(new_soil_data)

    return new_soil_data


@router.get("/", response_model=list[SoilDataResponse])
def get_soil_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    soil_data = (
        db.query(SoilData)
        .filter(SoilData.farmer_id == current_user.id)
        .all()
    )

    return soil_data


@router.get("/{soil_id}", response_model=SoilDataResponse)
def get_single_soil_data(
    soil_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    soil_data = (
        db.query(SoilData)
        .filter(
            SoilData.id == soil_id,
            SoilData.farmer_id == current_user.id
        )
        .first()
    )

    if not soil_data:
        raise HTTPException(
            status_code=404,
            detail="Soil data not found"
        )

    return soil_data


@router.put("/{soil_id}", response_model=SoilDataResponse)
def update_soil_data(
    soil_id: int,
    soil_data: SoilDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_soil = (
        db.query(SoilData)
        .filter(
            SoilData.id == soil_id,
            SoilData.farmer_id == current_user.id
        )
        .first()
    )

    if not existing_soil:
        raise HTTPException(
            status_code=404,
            detail="Soil data not found"
        )

    existing_soil.crop_name = soil_data.crop_name
    existing_soil.nitrogen = soil_data.nitrogen
    existing_soil.phosphorus = soil_data.phosphorus
    existing_soil.potassium = soil_data.potassium
    existing_soil.ph = soil_data.ph

    db.commit()
    db.refresh(existing_soil)

    return existing_soil


@router.delete("/{soil_id}")
def delete_soil_data(
    soil_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    soil_data = (
        db.query(SoilData)
        .filter(
            SoilData.id == soil_id,
            SoilData.farmer_id == current_user.id
        )
        .first()
    )

    if not soil_data:
        raise HTTPException(
            status_code=404,
            detail="Soil data not found"
        )

    db.delete(soil_data)
    db.commit()

    return {
        "message": "Soil data deleted successfully"
    }