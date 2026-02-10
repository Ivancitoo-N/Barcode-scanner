from pyzbar.pyzbar import decode, ZBarSymbol
import cv2
import numpy

class BarcodeDetector:
    def __init__(self):
        # We restrict to common 1D codes to avoid PDF417 assertion failures on noise
        self.allowed_symbols = [
            ZBarSymbol.EAN13,
            ZBarSymbol.EAN8,
            ZBarSymbol.CODE128,
            ZBarSymbol.CODE39,
            ZBarSymbol.UPCA,
            ZBarSymbol.UPCE
        ]

    def detect(self, frame):
        """
        Detects barcodes in a frame.
        Returns the frame with drawn rectangles and a list of detected codes.
        """
        # Optimization: Resolution Handling
        height, width = frame.shape[:2]
        scale = 1.0
        
        # If too big, downscale (speed). If too small, upscale (readability).
        if width > 1280:
            scale = 1280 / float(width)
        elif width < 800:
            scale = 2.0  # Upscale for small webcams to help pyzbar see gaps
            
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if scale != 1.0:
            detect_img = cv2.resize(gray, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_LINEAR)
        else:
            detect_img = gray

        # 1. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        detect_img = clahe.apply(detect_img)

        # 2. Sharpening kernel (Mild)
        kernel = numpy.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) 
        detect_img_sharp = cv2.filter2D(detect_img, -1, kernel)
        
        # Pass 1: Sharpened Grayscale
        barcodes = decode(detect_img_sharp, symbols=self.allowed_symbols)
        
        # Pass 2: Otsu's Thresholding (High Contrast Black/White)
        if not barcodes:
            # Blur slightly before thresholding to remove noise
            blur = cv2.GaussianBlur(detect_img, (5, 5), 0)
            _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            barcodes = decode(binary, symbols=self.allowed_symbols)
            
            # Debug: Show binary image logic (cannot show in web stream easily without changing return)
            # if barcodes: print("[DEBUG] Detected via Otsu")

        # Pass 3: Zoomed/Cropped Center (simulate "focusing" on center)
        if not barcodes:
             h, w = detect_img.shape
             cx, cy = w // 2, h // 2
             half_w, half_h = w // 4, h // 4 # Grab center 50%
             cropped = detect_img[cy-half_h:cy+half_h, cx-half_w:cx+half_w]
             # Resize crop back to full size
             zoomed = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
             # Threshold the zoom
             _, binary_zoom = cv2.threshold(zoomed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
             barcodes_zoom = decode(binary_zoom, symbols=self.allowed_symbols)
             
             for b in barcodes_zoom:
                 # Need to adjust bbox coordinates back to full frame? 
                 # This is complex for visualization. For now, let's just see if we can READ it.
                 # If we read it, we accept it. The bounding box might look wrong but the DATA is good.
                 # Let's map coordinates roughly or just accept the data.
                 barcodes.append(b) 

        detected_codes = []

        for barcode in barcodes:
            # Extract bounding box location
            (x, y, w, h) = barcode.rect
            
            # Map coordinates back to original size
            if scale != 1.0:
                x = int(x / scale)
                y = int(y / scale)
                w = int(w / scale)
                h = int(h / scale)
            
            # Decode the barcode data
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            # Draw the bounding box on the ORIGINAL frame
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Draw label
            text = f"{barcode_data} ({barcode_type})"
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)

            detected_codes.append({
                "data": barcode_data,
                "type": barcode_type,
                "bbox": [x, y, w, h]
            })

        return frame, detected_codes
