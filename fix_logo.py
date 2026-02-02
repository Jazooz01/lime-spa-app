import os
from PIL import Image, ImageDraw, ImageFont

# Define the exact path Flask expects
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, 'app', 'static')
logo_path = os.path.join(static_dir, 'logo.png')

# Ensure folder exists
os.makedirs(static_dir, exist_ok=True)

print(f" Attempting to create logo at: {logo_path}")

# Create Image
try:
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw Emerald Circle
    draw.ellipse([10, 10, 190, 190], fill="#064E3B", outline="#ECFDF5", width=5)
    
    # Draw 'L' Text
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except:
        font = ImageFont.load_default()
        
    # Center the text roughly
    draw.text((75, 40), "L", fill="white", font=font)
    
    img.save(logo_path)
    print("✅ SUCCESS: Logo created.")
except Exception as e:
    print(f"❌ ERROR: {e}")