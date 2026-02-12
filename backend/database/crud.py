from sqlalchemy.orm import Session
from . import models
from ..schemas import ScannedCodeCreate

def get_codes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ScannedCode).order_by(models.ScannedCode.timestamp.desc()).offset(skip).limit(limit).all()

def create_code(db: Session, code: ScannedCodeCreate):
    db_code = models.ScannedCode(
        data=code.data, 
        type=code.type, 
        product_name=code.product_name,
        price=code.price
    )
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
    """Returns (name, price, total_count) for a given barcode."""
    
    # 1. Check Product Catalog first
    product = get_product_by_barcode(db, barcode)
    catalog_name = product.name if product else None
    catalog_price = product.price if product else None

    # 2. Check Scan History
    last_entry = db.query(models.ScannedCode)\
                   .filter(models.ScannedCode.data == barcode)\
                   .order_by(models.ScannedCode.timestamp.desc())\
                   .first()
    
    count = db.query(models.ScannedCode)\
              .filter(models.ScannedCode.data == barcode)\
              .count()
    
    # Prioritize catalog name, fallback to history
    final_name = catalog_name if catalog_name else (last_entry.product_name if last_entry else None)
    
    return final_name, catalog_price, count

def get_product_by_barcode(db: Session, barcode: str):
    return db.query(models.Product).filter(models.Product.barcode == barcode).first()

def create_product(db: Session, product: models.Product):
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
