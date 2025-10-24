from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import db, AdjustmentLog
from services.sleepiq_service import sleepiq_service
import logging

logger = logging.getLogger(__name__)

mattress_bp = Blueprint('mattress', __name__)

@mattress_bp.route('/status', methods=['GET'])
@jwt_required()
def get_status():
    """Get current mattress status"""
    try:
        user_id = get_jwt_identity()
        bed_status = sleepiq_service.get_bed_status(user_id)
        
        return jsonify(bed_status)
        
    except Exception as e:
        logger.error(f"Get mattress status error: {str(e)}")
        return jsonify({'error': f'Failed to get mattress status: {str(e)}'}), 500

@mattress_bp.route('/adjust', methods=['POST'])
@jwt_required()
def adjust_firmness():
    """Manually adjust mattress firmness"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Check if adjusting both sides or individual sides
        if 'left_firmness' in data and 'right_firmness' in data:
            # Adjust both sides
            left_firmness = data.get('left_firmness')
            right_firmness = data.get('right_firmness')
            
            results = sleepiq_service.set_both_sides(
                user_id=user_id,
                left_firmness=left_firmness,
                right_firmness=right_firmness
            )
            
            return jsonify({
                'message': 'Firmness adjustment completed',
                'results': results
            })
        
        elif 'side' in data and 'firmness' in data:
            # Adjust single side
            side = data['side']
            firmness = data['firmness']
            
            if side not in ['left', 'right']:
                return jsonify({'error': 'Side must be left or right'}), 400
            
            if not (0 <= firmness <= 100):
                return jsonify({'error': 'Firmness must be between 0 and 100'}), 400
            
            result = sleepiq_service.set_firmness(
                user_id=user_id,
                side=side,
                firmness=firmness
            )
            
            return jsonify({
                'message': f'{side.capitalize()} side adjusted successfully',
                'result': result
            })
        
        else:
            return jsonify({'error': 'Either specify side and firmness, or left_firmness and right_firmness'}), 400
        
    except Exception as e:
        logger.error(f"Adjust firmness error: {str(e)}")
        return jsonify({'error': f'Failed to adjust firmness: {str(e)}'}), 500

@mattress_bp.route('/test', methods=['POST'])
@jwt_required()
def test_connection():
    """Test SleepNumber connection"""
    try:
        user_id = get_jwt_identity()
        
        # Try to get bed status to test connection
        bed_status = sleepiq_service.get_bed_status(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Connection test successful',
            'bed_info': bed_status
        })
        
    except Exception as e:
        logger.error(f"Test connection error: {str(e)}")
        return jsonify({'error': f'Connection test failed: {str(e)}'}), 400
