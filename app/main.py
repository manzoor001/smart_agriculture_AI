from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import Base, engine, get_db

# Import ALL models first
from app.models.user import User
from app.models.crop import Crop
from app.models.soil_data import SoilData
from app.models.disease import DiseaseRecord

# Import authentication after models
from app.auth.router import router as auth_router
from app.auth.security import get_current_user

from app.schemas.crop import CropCreate
from routes.soil import router as soil_router

# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="Smart Agriculture AI",
    version="1.0.0"
)


# Authentication routes
app.include_router(auth_router)
app.include_router(soil_router)


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Smart Agriculture AI Backend is running!"
    }


# Test PostgreSQL connection
@app.get("/test-db")
def test_database():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "success",
            "message": "Successfully connected to PostgreSQL!"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# Test database session
@app.get("/db-test")
def database_test(db: Session = Depends(get_db)):
    return {
        "status": "success",
        "message": "Database session is working!"
    }


# Create Crop - Protected
@app.post("/crops")
def create_crop(
    crop: CropCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_crop = Crop(
        name=crop.name,
        variety=crop.variety,
        season=crop.season,
        farmer_id=current_user.id
    )

    db.add(new_crop)
    db.commit()
    db.refresh(new_crop)

    return new_crop


# Get All Crops - Protected
@app.get("/crops")
def get_crops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    crops = db.query(Crop).filter(Crop.farmer_id == current_user.id).all()

    return crops


# Get Single Crop - Protected
@app.get("/crops/{crop_id}")
def get_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    crop = db.query(Crop).filter(
    Crop.id == crop_id,
    Crop.farmer_id == current_user.id
    ).first()

    if crop is None:
        return {
            "status": "error",
            "message": "Crop not found"
        }

    return crop


# Update Crop - Protected
@app.put("/crops/{crop_id}")
def update_crop(
    crop_id: int,
    crop_data: CropCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    crop = db.query(Crop).filter(
    Crop.id == crop_id,
    Crop.farmer_id == current_user.id
    ).first()

    if crop is None:
        return {
            "status": "error",
            "message": "Crop not found"
        }

    crop.name = crop_data.name
    crop.variety = crop_data.variety
    crop.season = crop_data.season

    db.commit()
    db.refresh(crop)

    return crop


# Delete Crop - Protected
@app.delete("/crops/{crop_id}")
def delete_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    crop = db.query(Crop).filter(
    Crop.id == crop_id,
    Crop.farmer_id == current_user.id
    ).first()

    if crop is None:
        return {
            "status": "error",
            "message": "Crop not found"
        }

    db.delete(crop)
    db.commit()

    return {
        "status": "success",
        "message": "Crop deleted successfully"
    }