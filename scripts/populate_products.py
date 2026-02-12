from sqlalchemy.orm import Session
from backend.database import database, models, crud

def populate_products():
    db = database.SessionLocal()
    
    # User's list with names and barcodes. All prices are 1.0.
    products_data = [
        ("Leche (en brick)", "0539099943917"),
        ("Pan de molde (paquete)", "1084724715128"),
        ("Huevos (cartón)", "1219842322051"),
        ("Arroz (en bolsa)", "1335045520640"),
        ("Pasta seca (espaguetis)", "1396156870581"),
        ("Queso en lonchas/rallado (en paquete)", "4241103635966"), # Assuming this is the one with barcode
        ("Azúcar (en bolsa)", "4395890092065"), # Assuming this is the one with barcode
        ("Aceite de oliva/girasol (en botella)", "4875392321240"), # Assuming this is the one with barcode
        ("Conservas de pescado (atún)", "6005937036812"), # Assuming this is the one with barcode
        ("Detergente para la ropa (en botella)", "6760811754144"), # Assuming this is the one with barcode
        ("Yogures (en packs)", "9441995496545"), # Assuming this is the one with barcode
        ("Tomate triturado/frito (en lata o brick)", "1429431122034"),
        ("Galletas (en paquete o caja)", "1918413472378"),
        ("Cereales de desayuno (en caja)", "2681348886181"),
        ("Embutidos (jamón cocido)", "3079378130395"),
        ("Café molido/soluble (bote)", "4328438249867"),
        ("Sal (en paquete o salero)", "4552596012104"),
        ("Agua embotellada (en botella)", "5724601862212"),
        ("Legumbres cocidas (garbanzos)", "6190164536089"),
        ("Gel de ducha/Champú (en botella)", "7181030293655"),
    ]

    # Note: Some items in the user request didn't have barcodes explicitly next to them in the first list, 
    # but were repeated with barcodes later or seemed to be part of a numbered list without barcodes.
    # The second part of the user request had a more clean list with barcodes.
    # I used the barcodes provided in the text.
    
    print("Populating products...")
    for name, barcode in products_data:
        # Check if exists
        existing = crud.get_product_by_barcode(db, barcode)
        if not existing:
            print(f"Adding {name} ({barcode})")
            crud.create_product(db, models.Product(name=name, barcode=barcode, price=1.0))
        else:
            print(f"Skipping {name} ({barcode}) - Already exists")
            
    db.close()
    print("Done.")

if __name__ == "__main__":
    # Ensure tables exist
    models.Base.metadata.create_all(bind=database.engine)
    populate_products()
