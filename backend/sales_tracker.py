import os
import openpyxl
from openpyxl import Workbook
from datetime import datetime
from collections import defaultdict

class SalesTracker:
    def __init__(self, filename="sales.xlsx"):
        self.filename = filename

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            wb = Workbook()
            ws = wb.active
            ws.title = "Ventas"
            headers = ["Fecha y Hora", "Código de Barras", "Producto", "Cantidad", "Precio Unitario", "Total"]
            ws.append(headers)
            wb.save(self.filename)

    def log_sale(self, codes):
        """
        Aggregates scanned codes and appends them to the Excel file.
        """
        if not codes:
            return

        self._ensure_file_exists()
        wb = openpyxl.load_workbook(self.filename)
        ws = wb.active

        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Aggregate items
        aggregated = defaultdict(lambda: {"count": 0, "name": "Unknown", "price": 0.0})
        for code in codes:
            key = code.data
            aggregated[key]["count"] += 1
            aggregated[key]["name"] = code.product_name or code.data
            aggregated[key]["price"] = code.price if code.price is not None else 0.0

        for barcode, item in aggregated.items():
            qty = item["count"]
            unit_price = item["price"]
            total = qty * unit_price
            
            row = [now, barcode, item["name"], qty, unit_price, total]
            ws.append(row)

        wb.save(self.filename)
        print(f"[INFO] Sales recorded in {self.filename}")
