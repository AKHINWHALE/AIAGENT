import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv

# 1. Load environment variables FIRST
load_dotenv()

# 2. Initialize Flask app
app = Flask(__name__)

# 3. Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'super-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ai_assistant.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
app.config['APP_URL'] = os.getenv('APP_URL', 'http://localhost:5000')

# 4. Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login' # Adjust if your login route is different
mail = Mail(app)

# 5. Import models and blueprints AFTER app is created (prevents circular imports)
from models import User
from auth import auth
from user import user
from admin import admin
from webhooks import webhooks

# 6. Register blueprints
app.register_blueprint(auth)
app.register_blueprint(user)
app.register_blueprint(admin)
app.register_blueprint(webhooks)

# 7. Create database tables
with app.app_context():
    db.create_all()

# 8. Start the background scheduler (MUST be at the very end, after 'app' is defined)
from scheduler import start_scheduler
start_scheduler(app)

@app.route('/')
def home():
    """Redirect visitors from the homepage to the login page"""
    return redirect('/login')

# 9. Run the app (This runs when you type 'python app.py' locally)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
