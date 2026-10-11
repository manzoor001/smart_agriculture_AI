from sqlalchemy import Column, Integer, String, Float
from app.database.database import Base


class DiseaseRecord(Base):
    __tablename__ = "disease_records"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String, nullable=False)
    disease_name = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)