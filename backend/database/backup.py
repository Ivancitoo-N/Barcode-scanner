import csv
import json
import io
from datetime import datetime
from sqlalchemy.orm import Session
from . import models

def export_to_csv(db: Session):
    codes = db.query(models.ScannedCode).all()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ID', 'Data', 'Type', 'Timestamp'])
    
    for code in codes:
        writer.writerow([code.id, code.data, code.type, code.timestamp])
        
    return output.getvalue()

def export_to_json(db: Session):
    codes = db.query(models.ScannedCode).all()
    data = []
    for code in codes:
        data.append({
            'id': code.id,
            'data': code.data,
            'type': code.type,
            'timestamp': code.timestamp.isoformat() if code.timestamp else None
        })
    return data
