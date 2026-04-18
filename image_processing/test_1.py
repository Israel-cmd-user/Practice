import easyocr
import os
import shutil
import cv2

source_folder = r'C:\Users\is2648257\Documents\Ond-assets\2025-10V4\GX010593'
target_folder = './line_marking_blur'
search_phrase = "line marking blur"

if not os.path.exists(target_folder):
    os.makedirs(target_folder)

reader = easyocr.Reader(['en'])

for filename in os.listdir(source_folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        file_path = os.path.join(source_folder, filename)
        
        # Load the image with OpenCV to crop it
        img = cv2.imread(file_path)
        h, w, _ = img.shape
        
        # Define the Left Corner (Top 25% height, Left 35% width)
        roi = img[0:int(h*0.25), 0:int(w*0.35)]
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Read text ONLY from the cropped corner
        results = reader.readtext(roi, detail=0)
        full_text = " ".join(results).lower()
        
        if search_phrase in full_text:
            print(f"Match found in metadata: {filename}")
            shutil.move(file_path, os.path.join(target_folder, filename))
        else:
            print(f"Skipping {filename} (phrase not in corner).")