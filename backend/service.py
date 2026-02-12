from typing import List, Optional
from backend.schemas import ScannedCodeCreate
import time
import requests

class BarcodeService:
    def __init__(self):
        # In-memory deduplication buffer
        # Key: barcode_data, Value: timestamp of last scan
        self._last_scanned = {} 
        self._dedup_interval = 5.0 # Seconds to ignore duplicates

    def _fetch_from_off_family(self, barcode: str, api_type: str = "food") -> Optional[str]:
        """
        Helper for OFF family APIs (food, beauty, products).
        api_type can be 'food', 'beauty', or 'products'.
        """
        subdomain = {
            "food": "world",
            "beauty": "world",
            "products": "world"
        }.get(api_type, "world")
        
        # OFF URLs differ slightly by type
        base_urls = {
            "food": "https://world.openfoodfacts.org",
            "beauty": "https://world.openbeautyfacts.org",
            "products": "https://world.openproductfacts.org"
        }
        
        url = f"{base_urls.get(api_type)}/api/v0/product/{barcode}.json"
        
        try:
            response = requests.get(url, timeout=2) # Short timeout to keep fallback snappy
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 1:
                    product = data.get("product", {})
                    name = product.get("product_name") or product.get("generic_name")
                    if name: return name
            return None
        except:
            return None

    def _fetch_from_open_library(self, barcode: str) -> Optional[str]:
        """
        Fetches book title from Open Library API.
        Works best for EAN-13 starting with 978/979.
        """
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{barcode}&format=json&jscmd=data"
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                key = f"ISBN:{barcode}"
                if key in data:
                    return data[key].get("title")
            return None
        except:
            return None

    def get_product_name(self, barcode: str, db_name: Optional[str] = None) -> str:
        """
        Tries local memory first, then multiple APIs.
        """
        # 1. Local Memory (Check if we already named it)
        if db_name and db_name != "Product Unknown":
            return db_name

        # 2. Check if it's likely a book (ISBN-13 usually starts with 978 or 979)
        if barcode.startswith(("978", "979")) and len(barcode) == 13:
            book_title = self._fetch_from_open_library(barcode)
            if book_title: return f"Book: {book_title}"

        # 3. Try Open Food Facts
        name = self._fetch_from_off_family(barcode, "food")
        if name: return name

        # 4. Try Open Product Facts
        name = self._fetch_from_off_family(barcode, "products")
        if name: return name

        # 5. Try Open Beauty Facts
        name = self._fetch_from_off_family(barcode, "beauty")
        if name: return name

        return "Product Unknown"

    def validate_code(self, code_data: str) -> bool:
        # Additional business rules can go here
        if len(code_data) < 3: 
            return False
        return True

    def is_duplicate(self, code_data: str) -> bool:
        now = time.time()
        last_time = self._last_scanned.get(code_data)
        if last_time and (now - last_time < self._dedup_interval):
            return True
        self._last_scanned[code_data] = now
        return False

    def process_frame_codes(self, raw_codes: List[dict], db_metadata_func=None) -> List[dict]:
        """
        Filters raw codes and attaches product info + scan counts.
        """
        valid_codes = []
        for code in raw_codes:
            data = code['data']
            if self.validate_code(data):
                if not self.is_duplicate(data):
                    code['is_new'] = True
                    
                    last_name, price, count = (None, None, 0)
                    if db_metadata_func:
                        last_name, price, count = db_metadata_func(data)
                    
                    code['product_name'] = self.get_product_name(data, db_name=last_name)
                    code['price'] = price
                    code['scan_count'] = count + 1 # Include current scan
                else:
                    code['is_new'] = False
                    code['product_name'] = None
                    code['scan_count'] = 0
                valid_codes.append(code)
        return valid_codes
