from sqlalchemy.orm import Session
from backend.database import database, models, crud

def verify_product():
    db = database.SessionLocal()
    
    # Test with "Leche (en brick)" - 0539099943917
    barcode = "0539099943917"
    expected_name = "Leche (en brick)"
    expected_price = 1.0
    
    print(f"Verifying barcode: {barcode}")
    name, price, count = crud.get_barcode_metadata(db, barcode)
    
    print(f"Result: Name='{name}', Price={price}, Count={count}")
    
    if name == expected_name and price == expected_price:
        print("SUCCESS: Product lookup verified.")
    else:
        print(f"FAILURE: Expected Name='{expected_name}', Price={expected_price}")

    db.close()

if __name__ == "__main__":
    verify_product()
