from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    variety = Column(String, nullable=True)
    season = Column(String, nullable=True)

    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    farmer = relationship("User", back_populates="crops")