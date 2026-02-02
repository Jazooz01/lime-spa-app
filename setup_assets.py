import os
from PIL import Image, ImageDraw, ImageFont
from werkzeug.security import generate_password_hash

def create_logo():
    """Generates a placeholder professional logo."""
    os.makedirs("app/static", exist_ok=True)
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw Emerald Circle
    draw.ellipse([10, 10, 190, 190], fill="#064E3B", outline="#ECFDF5", width=5)
    # Draw Text
    try: font = ImageFont.truetype("arial.ttf", 100)
    except: font = ImageFont.load_default()
    draw.text((65, 45), "L", fill="white", font=font)
    img.save("app/static/logo.png")
    print("✅ Logo generated at app/static/logo.png")

def generate_hashes():
    """Prints hashes for .env"""
    print("\n--- COPY THESE TO .ENV ---")
    print(f"ADMIN_HASH={generate_password_hash('0000')}")
    print(f"STAFF_HASH={generate_password_hash('1234')}")
    print("--------------------------\n")

if __name__ == "__main__":
    create_logo()
    generate_hashes()