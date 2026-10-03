from pydantic import BaseModel
from typing import Optional


class SoilDataCreate(BaseModel):
    crop_name: str
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None


class SoilDataResponse(BaseModel):
    id: int
    crop_name: str
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None
    farmer_id: int

    class Config:
        from_attributes = True