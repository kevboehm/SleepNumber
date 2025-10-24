import os
import logging
from cryptography.fernet import Fernet
from sleepyq import Sleepyq
from models.database import db, MattressCredentials, AdjustmentLog
from datetime import datetime

logger = logging.getLogger(__name__)

class SleepIQService:
    def __init__(self):
        self.clients = {}  # Cache clients per user
        self.encryption_key = os.environ.get('ENCRYPTION_KEY')
        if not self.encryption_key:
            # Generate a new key if none exists (for development)
            self.encryption_key = Fernet.generate_key()
            logger.warning("No ENCRYPTION_KEY found in environment. Generated new key for development.")
        
        self.cipher_suite = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
    
    def _get_client(self, user_id):
        """Get or create a SleepIQ client for the user"""
        if user_id in self.clients:
            return self.clients[user_id]
        
        # Get encrypted credentials
        credentials = MattressCredentials.query.filter_by(user_id=user_id).first()
        if not credentials:
            raise ValueError("No SleepNumber credentials found for user")
        
        # Decrypt credentials
        email = self.cipher_suite.decrypt(credentials.encrypted_email.encode()).decode()
        password = self.cipher_suite.decrypt(credentials.encrypted_password.encode()).decode()
        
        # Create client
        client = Sleepyq(email, password)
        
        # Login and cache client
        try:
            client.login()
            self.clients[user_id] = client
            logger.info(f"Successfully logged in SleepIQ client for user {user_id}")
            return client
        except Exception as e:
            logger.error(f"Failed to login SleepIQ client for user {user_id}: {str(e)}")
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
            client = self._get_client(user_id)
            
            # Get bed information
            beds = client.beds()
            bed_family_status = client.bed_family_status()
            
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
            client = self._get_client(user_id)
            
            # Validate inputs
            if side not in ['left', 'right']:
                raise ValueError("Side must be 'left' or 'right'")
            
            if not (0 <= firmness <= 100):
                raise ValueError("Firmness must be between 0 and 100")
            
            # Set the firmness
            bed_id = ''  # Use default bed
            client.set_sleepnumber(side, firmness, bedId=bed_id)
            
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
            
            # Test the credentials by creating a client
            test_client = Sleepyq(email, password)
            test_client.login()
            
            logger.info(f"Successfully stored and verified SleepNumber credentials for user {user_id}")
            return {'success': True, 'message': 'Credentials stored and verified successfully'}
            
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            logger.error(f"Failed to store credentials for user {user_id}: {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def clear_client_cache(self, user_id):
        """Clear cached client for a user (useful when credentials change)"""
        if user_id in self.clients:
            del self.clients[user_id]
            logger.info(f"Cleared SleepIQ client cache for user {user_id}")

# Global service instance
sleepiq_service = SleepIQService()
