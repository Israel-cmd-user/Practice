import easyocr
import cv2
import os

# 1. Setup
image_path = 'id-2.jpg'  
search_phrase = "line marking blur"

# 2. Initialize Reader (CPU Mode for testing)
reader = easyocr.Reader(['en'], gpu=False)

if os.path.exists(image_path):
    # Load and get dimensions
    img = cv2.imread(image_path)
    h, w, _ = img.shape

    # 3. Create the Crop (Top 25%, Left 35%)
    roi = img[0:int(h*0.25), 0:int(w*0.25)]
    
    # Pre-process: Convert to grayscale for better reading
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # 4. Run OCR
    print("Reading text... please wait...")
    results = reader.readtext(roi_gray, detail=0)
    full_text = " ".join(results).lower()

    # 5. Output Results
    print("-" * 30)
    print(f"Text Found: {full_text}")
    if search_phrase in full_text:
        print(f"SUCCESS: Found '{search_phrase}'!")
    else:
        print(f"FAILED: Could not find '{search_phrase}'.")
    print("-" * 30)

    # 6. Show the Crop
    # This lets you see if the text is being cut off
    cv2.imshow("What the AI Sees (Press any key to close)", roi_gray)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

else:
    print(f"Error: Could not find {image_path}")