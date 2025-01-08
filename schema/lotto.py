from pydantic import BaseModel
from datetime import date

class WinningNumberBase(BaseModel):
    numbers: str

class WinningNumberCreate(WinningNumberBase):
    date: date

class WinningNumberResponse(WinningNumberBase):
    id: int
    date: date

    class Config:
        from_attributes = True
