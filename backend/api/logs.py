from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import db, AdjustmentLog
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/', methods=['GET'])
@jwt_required()
def get_logs():
    """Get adjustment logs for the current user"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        side = request.args.get('side')  # 'left' or 'right'
        status = request.args.get('status')  # 'success', 'failed', 'pending'
        days = request.args.get('days', 30, type=int)  # Number of days to look back
        
        # Build query
        query = AdjustmentLog.query.filter_by(user_id=user_id)
        
        # Filter by side
        if side and side in ['left', 'right']:
            query = query.filter_by(side=side)
        
        # Filter by status
        if status and status in ['success', 'failed', 'pending']:
            query = query.filter_by(status=status)
        
        # Filter by date range
        if days > 0:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(AdjustmentLog.executed_at >= start_date)
        
        # Order by most recent first
        query = query.order_by(AdjustmentLog.executed_at.desc())
        
        # Pagination
        logs = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'pagination': {
                'page': logs.page,
                'pages': logs.pages,
                'per_page': logs.per_page,
                'total': logs.total,
                'has_next': logs.has_next,
                'has_prev': logs.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Get logs error: {str(e)}")
        return jsonify({'error': 'Failed to get logs'}), 500

@logs_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_log_stats():
    """Get statistics about adjustment logs"""
    try:
        user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all logs in date range
        logs = AdjustmentLog.query.filter(
            AdjustmentLog.user_id == user_id,
            AdjustmentLog.executed_at >= start_date
        ).all()
        
        # Calculate statistics
        total_adjustments = len(logs)
        successful_adjustments = len([log for log in logs if log.status == 'success'])
        failed_adjustments = len([log for log in logs if log.status == 'failed'])
        
        # Success rate
        success_rate = (successful_adjustments / total_adjustments * 100) if total_adjustments > 0 else 0
        
        # Adjustments by side
        left_adjustments = len([log for log in logs if log.side == 'left'])
        right_adjustments = len([log for log in logs if log.side == 'right'])
        
        # Recent activity (last 7 days)
        recent_start = datetime.utcnow() - timedelta(days=7)
        recent_logs = [log for log in logs if log.executed_at >= recent_start]
        
        return jsonify({
            'period_days': days,
            'total_adjustments': total_adjustments,
            'successful_adjustments': successful_adjustments,
            'failed_adjustments': failed_adjustments,
            'success_rate': round(success_rate, 2),
            'adjustments_by_side': {
                'left': left_adjustments,
                'right': right_adjustments
            },
            'recent_activity': {
                'last_7_days': len(recent_logs),
                'last_adjustment': recent_logs[0].executed_at.isoformat() if recent_logs else None
            }
        })
        
    except Exception as e:
        logger.error(f"Get log stats error: {str(e)}")
        return jsonify({'error': 'Failed to get log statistics'}), 500

@logs_bp.route('/<int:log_id>', methods=['GET'])
@jwt_required()
def get_log(log_id):
    """Get a specific log entry"""
    try:
        user_id = get_jwt_identity()
        log = AdjustmentLog.query.filter_by(id=log_id, user_id=user_id).first()
        
        if not log:
            return jsonify({'error': 'Log not found'}), 404
        
        return jsonify({'log': log.to_dict()})
        
    except Exception as e:
        logger.error(f"Get log error: {str(e)}")
        return jsonify({'error': 'Failed to get log'}), 500

@logs_bp.route('/clear', methods=['POST'])
@jwt_required()
def clear_logs():
    """Clear old logs (optional cleanup endpoint)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Get days parameter (default to 90 days)
        days = data.get('days', 90)
        
        if days < 7:  # Safety check - don't allow clearing recent logs
            return jsonify({'error': 'Cannot clear logs newer than 7 days'}), 400
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Count logs to be deleted
        logs_to_delete = AdjustmentLog.query.filter(
            AdjustmentLog.user_id == user_id,
            AdjustmentLog.executed_at < cutoff_date
        ).count()
        
        # Delete old logs
        deleted_count = AdjustmentLog.query.filter(
            AdjustmentLog.user_id == user_id,
            AdjustmentLog.executed_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        logger.info(f"Cleared {deleted_count} old logs for user {user_id}")
        
        return jsonify({
            'message': f'Cleared {deleted_count} logs older than {days} days',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Clear logs error: {str(e)}")
        return jsonify({'error': 'Failed to clear logs'}), 500
