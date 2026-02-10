from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class ScannedCode(Base):
    __tablename__ = "scanned_codes"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(String, index=True) # The barcode content
    type = Column(String)             # E.g., EAN-13
    product_name = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<ScannedCode(data={self.data}, type={self.type})>"
