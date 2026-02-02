from flask import Flask
from .db import init_db, close_db
import os

def create_app():
    # 1. Create the Flask app instance (This was likely missing or out of scope)
    app = Flask(__name__)
    
    # 2. Configuration
    app.secret_key = os.getenv('SECRET_KEY', 'dev')
    
    # 3. Initialize Database
    init_db(app)
    app.teardown_appcontext(close_db)
    
    # 4. Register Blueprints (Now including 'public')
    from .routes import auth, admin, staff, public
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(staff.bp)
    app.register_blueprint(public.bp)
    
    return app