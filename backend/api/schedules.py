from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import db, Schedule, Sleeper
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

schedules_bp = Blueprint('schedules', __name__)

@schedules_bp.route('/', methods=['GET'])
@jwt_required()
def get_schedules():
    """Get all schedules for the current user"""
    try:
        user_id = get_jwt_identity()
        schedules = Schedule.query.filter_by(user_id=user_id).order_by(Schedule.time).all()
        
        return jsonify({
            'schedules': [schedule.to_dict() for schedule in schedules]
        })
        
    except Exception as e:
        logger.error(f"Get schedules error: {str(e)}")
        return jsonify({'error': 'Failed to get schedules'}), 500

@schedules_bp.route('/', methods=['POST'])
@jwt_required()
def create_schedule():
    """Create a new schedule"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate time format (HH:MM)
        time = data['time']
        try:
            datetime.strptime(time, '%H:%M')
        except ValueError:
            return jsonify({'error': 'Time must be in HH:MM format'}), 400
        
        # Validate firmness values
        left_firmness = data.get('left_firmness')
        right_firmness = data.get('right_firmness')
        
        if left_firmness is not None and not (0 <= left_firmness <= 100):
            return jsonify({'error': 'Left firmness must be between 0 and 100'}), 400
        
        if right_firmness is not None and not (0 <= right_firmness <= 100):
            return jsonify({'error': 'Right firmness must be between 0 and 100'}), 400
        
        # Validate apply_to_sides
        apply_to_sides = data.get('apply_to_sides', 'both')
        if apply_to_sides not in ['left', 'right', 'both']:
            return jsonify({'error': 'apply_to_sides must be left, right, or both'}), 400
        
        # Validate days_of_week
        days_of_week = data.get('days_of_week')
        if days_of_week is not None:
            if not isinstance(days_of_week, list):
                return jsonify({'error': 'days_of_week must be a list'}), 400
            if not all(0 <= day <= 6 for day in days_of_week):
                return jsonify({'error': 'days_of_week must contain values between 0 and 6'}), 400
        
        # Create schedule
        schedule = Schedule(
            user_id=user_id,
            name=data['name'],
            description=data.get('description'),
            time=time,
            left_firmness=left_firmness,
            right_firmness=right_firmness,
            apply_to_sides=apply_to_sides,
            enabled=data.get('enabled', True),
            days_of_week=days_of_week
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        logger.info(f"Created schedule '{schedule.name}' for user {user_id}")
        
        return jsonify({
            'message': 'Schedule created successfully',
            'schedule': schedule.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create schedule error: {str(e)}")
        return jsonify({'error': 'Failed to create schedule'}), 500

@schedules_bp.route('/<int:schedule_id>', methods=['GET'])
@jwt_required()
def get_schedule(schedule_id):
    """Get a specific schedule"""
    try:
        user_id = get_jwt_identity()
        schedule = Schedule.query.filter_by(id=schedule_id, user_id=user_id).first()
        
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        return jsonify({'schedule': schedule.to_dict()})
        
    except Exception as e:
        logger.error(f"Get schedule error: {str(e)}")
        return jsonify({'error': 'Failed to get schedule'}), 500

@schedules_bp.route('/<int:schedule_id>', methods=['PUT'])
@jwt_required()
def update_schedule(schedule_id):
    """Update a schedule"""
    try:
        user_id = get_jwt_identity()
        schedule = Schedule.query.filter_by(id=schedule_id, user_id=user_id).first()
        
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            schedule.name = data['name']
        
        if 'description' in data:
            schedule.description = data['description']
        
        if 'time' in data:
            # Validate time format
            try:
                datetime.strptime(data['time'], '%H:%M')
                schedule.time = data['time']
            except ValueError:
                return jsonify({'error': 'Time must be in HH:MM format'}), 400
        
        if 'left_firmness' in data:
            left_firmness = data['left_firmness']
            if left_firmness is not None and not (0 <= left_firmness <= 100):
                return jsonify({'error': 'Left firmness must be between 0 and 100'}), 400
            schedule.left_firmness = left_firmness
        
        if 'right_firmness' in data:
            right_firmness = data['right_firmness']
            if right_firmness is not None and not (0 <= right_firmness <= 100):
                return jsonify({'error': 'Right firmness must be between 0 and 100'}), 400
            schedule.right_firmness = right_firmness
        
        if 'apply_to_sides' in data:
            if data['apply_to_sides'] not in ['left', 'right', 'both']:
                return jsonify({'error': 'apply_to_sides must be left, right, or both'}), 400
            schedule.apply_to_sides = data['apply_to_sides']
        
        if 'enabled' in data:
            schedule.enabled = bool(data['enabled'])
        
        if 'days_of_week' in data:
            days_of_week = data['days_of_week']
            if days_of_week is not None:
                if not isinstance(days_of_week, list):
                    return jsonify({'error': 'days_of_week must be a list'}), 400
                if not all(0 <= day <= 6 for day in days_of_week):
                    return jsonify({'error': 'days_of_week must contain values between 0 and 6'}), 400
            schedule.days_of_week = days_of_week
        
        schedule.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Updated schedule '{schedule.name}' for user {user_id}")
        
        return jsonify({
            'message': 'Schedule updated successfully',
            'schedule': schedule.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update schedule error: {str(e)}")
        return jsonify({'error': 'Failed to update schedule'}), 500

@schedules_bp.route('/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
def delete_schedule(schedule_id):
    """Delete a schedule"""
    try:
        user_id = get_jwt_identity()
        schedule = Schedule.query.filter_by(id=schedule_id, user_id=user_id).first()
        
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        schedule_name = schedule.name
        db.session.delete(schedule)
        db.session.commit()
        
        logger.info(f"Deleted schedule '{schedule_name}' for user {user_id}")
        
        return jsonify({'message': 'Schedule deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete schedule error: {str(e)}")
        return jsonify({'error': 'Failed to delete schedule'}), 500

@schedules_bp.route('/<int:schedule_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_schedule(schedule_id):
    """Enable or disable a schedule"""
    try:
        user_id = get_jwt_identity()
        schedule = Schedule.query.filter_by(id=schedule_id, user_id=user_id).first()
        
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        schedule.enabled = not schedule.enabled
        schedule.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'enabled' if schedule.enabled else 'disabled'
        logger.info(f"{status.capitalize()} schedule '{schedule.name}' for user {user_id}")
        
        return jsonify({
            'message': f'Schedule {status} successfully',
            'schedule': schedule.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Toggle schedule error: {str(e)}")
        return jsonify({'error': 'Failed to toggle schedule'}), 500
