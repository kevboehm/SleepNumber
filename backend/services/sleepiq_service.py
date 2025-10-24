import os
import logging
import requests
from cryptography.fernet import Fernet
from models.database import db, MattressCredentials, AdjustmentLog
from datetime import datetime

logger = logging.getLogger(__name__)

class SleepIQService:
    def __init__(self):
        self.sessions = {}  # Cache sessions per user
        self.encryption_key = os.environ.get('ENCRYPTION_KEY')
        if not self.encryption_key:
            # Generate a new key if none exists (for development)
            self.encryption_key = Fernet.generate_key()
            logger.warning("No ENCRYPTION_KEY found in environment. Generated new key for development.")
        
        self.cipher_suite = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
        self.base_url = "https://prod-api.sleepiq.sleepnumber.com"
    
    def _get_session(self, user_id):
        """Get or create a SleepIQ session for the user"""
        if user_id in self.sessions:
            return self.sessions[user_id]
        
        # Get encrypted credentials
        credentials = MattressCredentials.query.filter_by(user_id=user_id).first()
        if not credentials:
            raise ValueError("No SleepNumber credentials found for user")
        
        # Decrypt credentials
        email = self.cipher_suite.decrypt(credentials.encrypted_email.encode()).decode()
        password = self.cipher_suite.decrypt(credentials.encrypted_password.encode()).decode()
        
        # Create session
        session = requests.Session()
        
        # Login and cache session
        try:
            login_data = {
                "login": email,
                "password": password
            }
            
            response = session.post(f"{self.base_url}/rest/login", json=login_data)
            response.raise_for_status()
            
            login_result = response.json()
            if not login_result.get('success'):
                raise ValueError("Login failed")
            
            # Store session key
            session.headers.update({
                'Authorization': f"Bearer {login_result.get('key', '')}"
            })
            
            self.sessions[user_id] = session
            logger.info(f"Successfully logged in SleepIQ session for user {user_id}")
            return session
        except Exception as e:
            logger.error(f"Failed to login SleepIQ session for user {user_id}: {str(e)}")
            raise ValueError(f"Failed to authenticate with SleepNumber: {str(e)}")
    
    def _log_adjustment(self, user_id, schedule_id, side, firmness, status, error_message=None, sleeper_id=None):
        """Log an adjustment attempt"""
        log = AdjustmentLog(
            user_id=user_id,
            schedule_id=schedule_id,
            sleeper_id=sleeper_id,
            side=side,
            firmness=firmness,
            status=status,
            error_message=error_message,
            executed_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return log
    
    def get_bed_status(self, user_id):
        """Get current bed status and information"""
        try:
            session = self._get_session(user_id)
            
            # Get bed information
            beds_response = session.get(f"{self.base_url}/rest/beds")
            beds_response.raise_for_status()
            beds = beds_response.json()
            
            family_status_response = session.get(f"{self.base_url}/rest/bedFamilyStatus")
            family_status_response.raise_for_status()
            bed_family_status = family_status_response.json()
            
            return {
                'beds': beds,
                'bed_family_status': bed_family_status,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get bed status for user {user_id}: {str(e)}")
            raise ValueError(f"Failed to get bed status: {str(e)}")
    
    def set_firmness(self, user_id, side, firmness, schedule_id=None, sleeper_id=None):
        """Set mattress firmness for a specific side"""
        try:
            session = self._get_session(user_id)
            
            # Validate inputs
            if side not in ['left', 'right']:
                raise ValueError("Side must be 'left' or 'right'")
            
            if not (0 <= firmness <= 100):
                raise ValueError("Firmness must be between 0 and 100")
            
            # Set the firmness using SleepIQ API
            sleepnumber_data = {
                "side": side,
                "sleepNumber": firmness
            }
            
            response = session.post(f"{self.base_url}/rest/sleepNumber", json=sleepnumber_data)
            response.raise_for_status()
            
            # Log successful adjustment
            log = self._log_adjustment(
                user_id=user_id,
                schedule_id=schedule_id,
                side=side,
                firmness=firmness,
                status='success',
                sleeper_id=sleeper_id
            )
            
            logger.info(f"Successfully set {side} side to {firmness} for user {user_id}")
            return {
                'success': True,
                'side': side,
                'firmness': firmness,
                'log_id': log.id,
                'timestamp': log.executed_at.isoformat()
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to set firmness for user {user_id}: {error_msg}")
            
            # Log failed adjustment
            log = self._log_adjustment(
                user_id=user_id,
                schedule_id=schedule_id,
                side=side,
                firmness=firmness,
                status='failed',
                error_message=error_msg,
                sleeper_id=sleeper_id
            )
            
            return {
                'success': False,
                'side': side,
                'firmness': firmness,
                'error': error_msg,
                'log_id': log.id,
                'timestamp': log.executed_at.isoformat()
            }
    
    def set_both_sides(self, user_id, left_firmness, right_firmness, schedule_id=None):
        """Set firmness for both sides"""
        results = {}
        
        if left_firmness is not None:
            results['left'] = self.set_firmness(user_id, 'left', left_firmness, schedule_id)
        
        if right_firmness is not None:
            results['right'] = self.set_firmness(user_id, 'right', right_firmness, schedule_id)
        
        return results
    
    def store_credentials(self, user_id, email, password):
        """Store encrypted SleepNumber credentials"""
        try:
            # Encrypt credentials
            encrypted_email = self.cipher_suite.encrypt(email.encode()).decode()
            encrypted_password = self.cipher_suite.encrypt(password.encode()).decode()
            
            # Check if credentials already exist
            existing = MattressCredentials.query.filter_by(user_id=user_id).first()
            
            if existing:
                # Update existing credentials
                existing.encrypted_email = encrypted_email
                existing.encrypted_password = encrypted_password
                existing.updated_at = datetime.utcnow()
            else:
                # Create new credentials
                credentials = MattressCredentials(
                    user_id=user_id,
                    encrypted_email=encrypted_email,
                    encrypted_password=encrypted_password
                )
                db.session.add(credentials)
            
            db.session.commit()
            
            # Test the credentials by creating a session
            test_session = requests.Session()
            login_data = {
                "login": email,
                "password": password
            }
            
            response = test_session.post(f"{self.base_url}/rest/login", json=login_data)
            response.raise_for_status()
            
            login_result = response.json()
            if not login_result.get('success'):
                raise ValueError("Login test failed")
            
            logger.info(f"Successfully stored and verified SleepNumber credentials for user {user_id}")
            return {'success': True, 'message': 'Credentials stored and verified successfully'}
            
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            logger.error(f"Failed to store credentials for user {user_id}: {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def clear_session_cache(self, user_id):
        """Clear cached session for a user (useful when credentials change)"""
        if user_id in self.sessions:
            del self.sessions[user_id]
            logger.info(f"Cleared SleepIQ session cache for user {user_id}")

# Global service instance
sleepiq_service = SleepIQService()
