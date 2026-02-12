from fpdf import FPDF
from datetime import datetime
from collections import defaultdict

class InvoicePDF(FPDF):
    def header(self):
        # Logo could go here
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'Lista de Escaneo / Factura', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', align='C')

class PDFGenerator:
    def generate(self, codes):
        pdf = InvoicePDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Date and Time
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 10, f'Fecha de generación: {now}', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        
        # Aggregation Logic
        # Group by data (barcode) or product_name if barcode is missing (fallback)
        grouped_items = defaultdict(lambda: {'count': 0, 'price': 0, 'name': 'Unknown', 'type': ''})
        
        for code in codes:
            key = code.data
            name = code.product_name if code.product_name else code.data
            price = code.price if code.price is not None else 0.0
            
            grouped_items[key]['count'] += 1
            grouped_items[key]['price'] = price # Assuming price is constant per item type
            grouped_items[key]['name'] = name
            grouped_items[key]['type'] = code.type

        # Table Header
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        
        # Columns: Product | Qty | Unit Price | Total
        col_widths = [90, 25, 35, 35] # Total 185 (A4 width approx 210 - margins)
        headers = ['Producto / Código', 'Cant.', 'Precio Unit.', 'Total']
        
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, border=1, fill=True, align='C')
        pdf.ln()
        
        # Table Content
        pdf.set_font('Helvetica', '', 10)
        grand_total = 0.0
        
        for key, item in grouped_items.items():
            count = item['count']
            unit_price = item['price']
            total_price = count * unit_price
            grand_total += total_price
            
            # Truncate name if too long
            name = item['name']
            if len(name) > 40:
                name = name[:37] + "..."
                
            pdf.cell(col_widths[0], 8, name, border=1)
            pdf.cell(col_widths[1], 8, str(count), border=1, align='C')
            pdf.cell(col_widths[2], 8, f"{unit_price:.2f}", border=1, align='R')
            pdf.cell(col_widths[3], 8, f"{total_price:.2f}", border=1, align='R')
            pdf.ln()

        # Grand Total
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(sum(col_widths[:3]), 10, 'TOTAL GENERAL:', border=1, align='R')
        pdf.cell(col_widths[3], 10, f"{grand_total:.2f}", border=1, align='R', fill=True)
        
        return pdf.output()
