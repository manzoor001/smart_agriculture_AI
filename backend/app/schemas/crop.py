from pydantic import BaseModel


class CropCreate(BaseModel):
    name: str
    variety: str | None = None
    season: str | None = None