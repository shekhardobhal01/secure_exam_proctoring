
import os
from PIL import Image

def load_icon():
    try:
        path = os.path.abspath("image.png")  
        print("Image absolute path:", path)
        img = Image.open(path)
        print("✅ Image loaded successfully!")
        return img
    except Exception as e:
        print("❌ Image failed to load:", e)
        return None
