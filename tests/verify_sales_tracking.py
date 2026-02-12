import os
from sqlalchemy.orm import Session
from backend.database import database, models, crud
from backend.sales_tracker import SalesTracker

def verify_sales_logging():
    db = database.SessionLocal()
    
    # 1. Clear existing codes for clean test
    crud.delete_all_codes(db)
    
    # 2. Add some test codes
    test_codes = [
        {"data": "0539099943917", "type": "EAN13", "product_name": "Leche (en brick)", "price": 1.0},
        {"data": "0539099943917", "type": "EAN13", "product_name": "Leche (en brick)", "price": 1.0},
        {"data": "1084724715128", "type": "EAN13", "product_name": "Pan de molde (paquete)", "price": 1.0}
    ]
    
    print("Adding test codes to database...")
    for c in test_codes:
        db_code = models.ScannedCode(
            data=c["data"], 
            type=c["type"], 
            product_name=c["product_name"],
            price=c["price"]
        )
        db.add(db_code)
    db.commit()

    # 3. Simulate "New Client" logic manually
    print("Simulating 'New Client' logic (Fetching and Logging)...")
    # We need to manually match the logic in main.py but here we can just use the objects
    # Note: crud.get_codes returns ORM objects. We need to ensure they have the 'price' attribute.
    # Actually, the ORM ScannedCode doesn't have 'price' column in DB (it wasn't in the original schema and I didn't add it to ScannedCode model, only Product).
    # Wait, I should check models.py again.
    
    codes_to_log = crud.get_codes(db, limit=100)
    
    # In main.py, I used: SalesTracker().log_sale(codes)
    # But wait, ScannedCode model DOES NOT HAVE price column.
    # Where does price come from?
    # In get_barcode_metadata, I return (name, price, count).
    # In service.py, I add 'price' to the 'code' dict.
    # BUT ScannedCode instances in DB don't store price.
    
    # Re-reading models.py:
    # class ScannedCode(Base):
    #     ...
    #     product_name = Column(String, nullable=True)
    #     timestamp = Column(DateTime, default=datetime.now)
    
    # Re-reading service.py aggregation:
    # code['price'] = price
    
    # Re-reading sales_tracker.py log_sale:
    # price = code.price if code.price is not None else 0.0
    
    # If ScannedCode objects from DB don't have .price, this will fail.
    # I should have added 'price' to ScannedCode model OR I need to look it up during logging.
    
    print("Checking if ScannedCode objects have price...")
    if codes_to_log and not hasattr(codes_to_log[0], 'price'):
        print("ERROR: ScannedCode objects from DB do not have 'price'. Need to fix models or logging logic.")
        # I'll modify the tracker to lookup price if missing
    else:
        SalesTracker().log_sale(codes_to_log)
        if os.path.exists("sales.xlsx"):
            print("SUCCESS: sales.xlsx created.")
        else:
            print("FAILURE: sales.xlsx not found.")

    db.close()

if __name__ == "__main__":
    verify_sales_logging()
