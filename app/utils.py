import os
import qrcode
import socket
from PIL import Image, ImageDraw, ImageFont
from flask import current_app, session, redirect, url_for, flash, request
from functools import wraps

def login_required(role=None):
    """
    Decorator to restrict access to specific roles (admin/staff).
    Includes 'next' parameter handling to fix redirect loops.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session:
                # Redirect to login, remembering the 'next' URL
                return redirect(url_for('auth.login', next=request.url))
            
            if role and session['user_role'] != role:
                flash("Unauthorized access.", "error")
                return redirect(url_for('auth.login'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_local_ip():
    """
    Gets the local IP address of the machine for local testing.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except: 
        return "127.0.0.1"

def generate_card(member):
    """
    Generates a premium membership card image.
    - Embeds the Logo
    - Generates QR pointing to the Customer Portal
    - Adapts URL for Production (Railway) vs Local
    - Saves to app/static/cards/
    """
    
    # 1. Define Paths safely using Flask's root_path
    base_path = current_app.root_path
    static_path = os.path.join(base_path, 'static')
    cards_path = os.path.join(static_path, 'cards')
    logo_path = os.path.join(static_path, 'logo.png')
    
    # Ensure cards folder exists
    os.makedirs(cards_path, exist_ok=True)

    # 2. Design Setup (Emerald & Gold Theme)
    width, height = 1000, 600
    bg_color = "#064E3B" # Emerald 900
    gold_color = "#C9A14A"
    
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Gold Header Strip
    draw.rectangle([0, 0, width, 120], fill=gold_color)
    
    # 3. Paste Logo
    if os.path.exists(logo_path):
        try:
            # Open logo, convert to RGBA to handle transparency
            logo = Image.open(logo_path).convert("RGBA")
            logo = logo.resize((100, 100))
            
            # Create a mask for transparency
            mask = logo.split()[3]
            
            # Paste onto card at coordinates (50, 10)
            img.paste(logo, (50, 10), mask)
        except Exception as e:
            print(f"Warning: Could not load logo for card: {e}")
    else:
        print(f"Warning: Logo file not found at {logo_path}. Run setup_assets.py or force_logo_fix.py.")

    # 4. Font Loading
    try:
        # Try to load standard fonts, fallback to default if missing
        title_font = ImageFont.truetype("arialbd.ttf", 60)
        text_font = ImageFont.truetype("arial.ttf", 40)
        id_font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        id_font = ImageFont.load_default()

    # 5. Draw Text Details
    draw.text((180, 30), "LIME SPA PRIVILEGE", fill="#000000", font=title_font)
    draw.text((50, 200), f"Name: {member['name']}", fill="white", font=text_font)
    draw.text((50, 280), f"Valid Thru: {member['expiry']}", fill="white", font=text_font)
    draw.text((50, 530), f"ID: {member['id']}", fill=gold_color, font=id_font)

    # 6. Generate QR Code
    # SMART URL LOGIC:
    # If on Railway/Production (PUBLIC_DOMAIN exists), use HTTPS and that domain.
    # If Local, use HTTP and local IP with port 5000.
    
    public_domain = os.getenv('PUBLIC_DOMAIN')
    
    if public_domain:
        # Production Mode (Railway)
        # Strip protocol if user added it, ensuring clean domain
        clean_domain = public_domain.replace("https://", "").replace("http://", "").strip("/")
        base_url = f"https://{clean_domain}"
    else:
        # Local Mode
        base_url = f"http://{get_local_ip()}:5000"

    # Point to the CUSTOMER PORTAL
    qr_data = f"{base_url}/portal/{member['id']}"
    
    qr = qrcode.make(qr_data)
    qr = qr.resize((250, 250))
    
    # Paste QR Code on the right side
    img.paste(qr, (700, 200))

    # 7. Save Final Card
    save_path = os.path.join(cards_path, f"{member['id']}.png")
    img.save(save_path)
    return save_path