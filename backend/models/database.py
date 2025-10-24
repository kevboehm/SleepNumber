from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import JSON
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sleepers = db.relationship('Sleeper', backref='user', lazy=True, cascade='all, delete-orphan')
    schedules = db.relationship('Schedule', backref='user', lazy=True, cascade='all, delete-orphan')
    adjustment_logs = db.relationship('AdjustmentLog', backref='user', lazy=True, cascade='all, delete-orphan')
    mattress_credentials = db.relationship('MattressCredentials', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MattressCredentials(db.Model):
    __tablename__ = 'mattress_credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    encrypted_email = db.Column(db.Text, nullable=False)
    encrypted_password = db.Column(db.Text, nullable=False)
    bed_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bed_id': self.bed_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Sleeper(db.Model):
    __tablename__ = 'sleepers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    side = db.Column(db.String(10), nullable=False)  # 'left' or 'right'
    preferred_firmness = db.Column(db.Integer, nullable=True)  # 0-100
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    adjustment_logs = db.relationship('AdjustmentLog', backref='sleeper', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'side': self.side,
            'preferred_firmness': self.preferred_firmness,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    time = db.Column(db.String(5), nullable=False)  # Format: "HH:MM"
    left_firmness = db.Column(db.Integer, nullable=True)  # 0-100
    right_firmness = db.Column(db.Integer, nullable=True)  # 0-100
    apply_to_sides = db.Column(db.String(10), nullable=False, default='both')  # 'left', 'right', 'both'
    enabled = db.Column(db.Boolean, default=True)
    days_of_week = db.Column(JSON, nullable=True)  # List of days: [0,1,2,3,4,5,6] (0=Monday)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    adjustment_logs = db.relationship('AdjustmentLog', backref='schedule', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'time': self.time,
            'left_firmness': self.left_firmness,
            'right_firmness': self.right_firmness,
            'apply_to_sides': self.apply_to_sides,
            'enabled': self.enabled,
            'days_of_week': self.days_of_week,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def should_run_today(self):
        """Check if this schedule should run today"""
        if not self.enabled:
            return False
        
        if not self.days_of_week:
            return True  # Run every day if no days specified
        
        today = datetime.now().weekday()  # 0=Monday, 6=Sunday
        return today in self.days_of_week

class AdjustmentLog(db.Model):
    __tablename__ = 'adjustment_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=True)
    sleeper_id = db.Column(db.Integer, db.ForeignKey('sleepers.id'), nullable=True)
    side = db.Column(db.String(10), nullable=False)  # 'left' or 'right'
    firmness = db.Column(db.Integer, nullable=False)  # 0-100
    status = db.Column(db.String(20), nullable=False)  # 'success', 'failed', 'pending'
    error_message = db.Column(db.Text, nullable=True)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'schedule_id': self.schedule_id,
            'sleeper_id': self.sleeper_id,
            'side': self.side,
            'firmness': self.firmness,
            'status': self.status,
            'error_message': self.error_message,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }
