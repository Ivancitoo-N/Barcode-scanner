from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re

class ScannedCodeBase(BaseModel):
    data: str = Field(..., min_length=1, description="The content of the barcode")
    type: str = Field(..., description="The type of the barcode (e.g., EAN13)")

    @validator('data')
    def validate_data(cls, v):
        if not v.strip():
            raise ValueError('Barcode data cannot be empty')
        # Basic regex to avoid obviously bad chars (SQL injection prevention start)
        if not re.match(r'^[a-zA-Z0-9\-\.\ \/\+\%\$]+$', v):
             raise ValueError('Barcode data contains invalid characters')
        return v

class ScannedCodeCreate(ScannedCodeBase):
    product_name: Optional[str] = None

class ScannedCodeResponse(ScannedCodeBase):
    id: Optional[int] = None
    product_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        orm_mode = True

class ErrorResponse(BaseModel):
    detail: str
