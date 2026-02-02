import os
from PIL import Image, ImageDraw, ImageFont

# 1. Calculate the absolute path to app/static
# This ensures we don't accidentally create 'static' in the wrong folder
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, 'app', 'static')
logo_path = os.path.join(static_dir, 'logo.png')

# 2. Ensure directory exists
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    print(f"📁 Created directory: {static_dir}")

# 3. Generate the Image
print(f"🎨 Generating logo at: {logo_path}")
try:
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0)) # Transparent background
    draw = ImageDraw.Draw(img)
    
    # Draw Emerald Circle
    draw.ellipse([10, 10, 190, 190], fill="#064E3B", outline="#ECFDF5", width=5)
    
    # Draw Text
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except:
        font = ImageFont.load_default()
    
    # Center 'L' roughly
    draw.text((75, 40), "L", fill="white", font=font)
    
    img.save(logo_path)
    print("✅ SUCCESS: Logo generated successfully.")
    print("👉 Now restart your Flask server and clear your browser cache.")
except Exception as e:
    print(f"❌ ERROR: {e}")