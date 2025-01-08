from sqlalchemy import Column, Integer, String, Date
from datetime import date
from config.database import Base

class WinningNumber(Base):
    __tablename__ = "winning_numbers"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, default=date.today)
    numbers = Column(String)  # Store numbers as a comma-separated string