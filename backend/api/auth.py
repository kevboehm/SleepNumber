from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db, User, MattressCredentials
from services.sleepiq_service import sleepiq_service
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        logger.info(f"New user registered: {user.username}")
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == data['username']) | (User.email == data['username'])
        ).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        logger.info(f"User logged in: {user.username}")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()})
        
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return jsonify({'error': 'Failed to get profile'}), 500

@auth_bp.route('/setup-credentials', methods=['POST'])
@jwt_required()
def setup_credentials():
    """Store encrypted SleepNumber credentials"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'SleepNumber email and password are required'}), 400
        
        # Store credentials using the service
        result = sleepiq_service.store_credentials(user_id, data['email'], data['password'])
        
        if result['success']:
            return jsonify({'message': 'SleepNumber credentials stored successfully'})
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"Setup credentials error: {str(e)}")
        return jsonify({'error': 'Failed to store credentials'}), 500

@auth_bp.route('/credentials', methods=['GET'])
@jwt_required()
def get_credentials():
    """Check if user has stored credentials"""
    try:
        user_id = get_jwt_identity()
        credentials = MattressCredentials.query.filter_by(user_id=user_id).first()
        
        if credentials:
            return jsonify({
                'has_credentials': True,
                'bed_id': credentials.bed_id,
                'created_at': credentials.created_at.isoformat() if credentials.created_at else None
            })
        else:
            return jsonify({'has_credentials': False})
            
    except Exception as e:
        logger.error(f"Get credentials error: {str(e)}")
        return jsonify({'error': 'Failed to check credentials'}), 500

@auth_bp.route('/test-connection', methods=['POST'])
@jwt_required()
def test_connection():
    """Test SleepNumber connection"""
    try:
        user_id = get_jwt_identity()
        
        # Try to get bed status to test connection
        bed_status = sleepiq_service.get_bed_status(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Connection successful',
            'bed_info': bed_status
        })
        
    except Exception as e:
        logger.error(f"Test connection error: {str(e)}")
        return jsonify({'error': f'Connection failed: {str(e)}'}), 400
