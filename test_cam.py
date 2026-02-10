import cv2
import sys

def test_camera():
    print("Initializing camera test...")
    # Try index 0 first, then 1
    for index in range(2):
        print(f"Testing camera index {index}...")
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            print(f"Failed to open camera index {index}")
            continue
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print(f"Success: Camera index {index} is working. Frame captured.")
            return True
        else:
            print(f"Warning: Camera index {index} opened but failed to return a frame.")
    
    print("Error: Could not capture frame from any camera.")
    return False

if __name__ == "__main__":
    if test_camera():
        sys.exit(0)
    else:
        sys.exit(1)
