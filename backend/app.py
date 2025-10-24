from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire for convenience

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Production (PostgreSQL)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Development (SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sleepnumber.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
CORS(app, origins=['*'])

# Import models to ensure they're registered with SQLAlchemy
from models.database import User, MattressCredentials, Sleeper, Schedule, AdjustmentLog

# Import API routes
from api.auth import auth_bp
from api.schedules import schedules_bp
from api.mattress import mattress_bp
from api.logs import logs_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(schedules_bp, url_prefix='/api/schedules')
app.register_blueprint(mattress_bp, url_prefix='/api/mattress')
app.register_blueprint(logs_bp, url_prefix='/api/logs')

# Health check endpoint
@app.route('/api/health')
def health_check():
    from datetime import datetime
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# Initialize scheduler service
from services.scheduler_service import start_scheduler

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        start_scheduler()
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
