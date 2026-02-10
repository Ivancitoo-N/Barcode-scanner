from sqlalchemy.orm import Session
from . import models
from ..schemas import ScannedCodeCreate

def get_codes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ScannedCode).order_by(models.ScannedCode.timestamp.desc()).offset(skip).limit(limit).all()

def create_code(db: Session, code: ScannedCodeCreate):
    db_code = models.ScannedCode(data=code.data, type=code.type, product_name=code.product_name)
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    return db_code

def delete_code(db: Session, code_id: int):
    code = db.query(models.ScannedCode).filter(models.ScannedCode.id == code_id).first()
    if code:
        db.delete(code)
        db.commit()
        return True
    return False

def delete_all_codes(db: Session):
    db.query(models.ScannedCode).delete()
    db.commit()

def get_barcode_metadata(db: Session, barcode: str):
    """Returns (last_name, total_count) for a given barcode."""
    last_entry = db.query(models.ScannedCode)\
                   .filter(models.ScannedCode.data == barcode)\
                   .order_by(models.ScannedCode.timestamp.desc())\
                   .first()
    
    count = db.query(models.ScannedCode)\
              .filter(models.ScannedCode.data == barcode)\
              .count()
    
    last_name = last_entry.product_name if last_entry else None
    return last_name, count
