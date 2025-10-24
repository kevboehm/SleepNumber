from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from models.database import db, Schedule
from services.sleepiq_service import sleepiq_service
from datetime import datetime
import logging
import atexit

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = None
        self.is_running = False
    
    def start(self):
        """Start the scheduler service"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Configure scheduler
        executors = {
            'default': ThreadPoolExecutor(max_workers=5)
        }
        
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 60  # 1 minute grace period
        }
        
        self.scheduler = BackgroundScheduler(
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        # Add the main job that checks schedules every minute
        self.scheduler.add_job(
            func=self.check_and_execute_schedules,
            trigger=CronTrigger(second=0),  # Run at the start of every minute
            id='schedule_checker',
            name='Check and execute schedules',
            replace_existing=True
        )
        
        # Start the scheduler
        self.scheduler.start()
        self.is_running = True
        
        logger.info("Scheduler service started")
        
        # Register shutdown handler
        atexit.register(self.shutdown)
    
    def shutdown(self):
        """Shutdown the scheduler service"""
        if self.scheduler and self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler service stopped")
    
    def check_and_execute_schedules(self):
        """Check all schedules and execute those that should run now"""
        try:
            current_time = datetime.now()
            current_minute = current_time.strftime('%H:%M')
            current_weekday = current_time.weekday()  # 0=Monday, 6=Sunday
            
            logger.debug(f"Checking schedules at {current_minute} (weekday: {current_weekday})")
            
            # Get all enabled schedules
            schedules = Schedule.query.filter_by(enabled=True).all()
            
            executed_count = 0
            
            for schedule in schedules:
                try:
                    # Check if schedule should run now
                    if self.should_execute_schedule(schedule, current_minute, current_weekday):
                        logger.info(f"Executing schedule '{schedule.name}' for user {schedule.user_id}")
                        
                        # Execute the schedule
                        self.execute_schedule(schedule)
                        executed_count += 1
                        
                except Exception as e:
                    logger.error(f"Error executing schedule '{schedule.name}': {str(e)}")
                    continue
            
            if executed_count > 0:
                logger.info(f"Executed {executed_count} schedules")
            
        except Exception as e:
            logger.error(f"Error in schedule checker: {str(e)}")
    
    def should_execute_schedule(self, schedule, current_minute, current_weekday):
        """Check if a schedule should execute now"""
        # Check time match
        if schedule.time != current_minute:
            return False
        
        # Check if schedule should run today
        return schedule.should_run_today()
    
    def execute_schedule(self, schedule):
        """Execute a specific schedule"""
        try:
            user_id = schedule.user_id
            
            # Determine which sides to adjust
            sides_to_adjust = []
            if schedule.apply_to_sides in ['left', 'both'] and schedule.left_firmness is not None:
                sides_to_adjust.append(('left', schedule.left_firmness))
            
            if schedule.apply_to_sides in ['right', 'both'] and schedule.right_firmness is not None:
                sides_to_adjust.append(('right', schedule.right_firmness))
            
            # Execute adjustments
            results = {}
            for side, firmness in sides_to_adjust:
                try:
                    result = sleepiq_service.set_firmness(
                        user_id=user_id,
                        side=side,
                        firmness=firmness,
                        schedule_id=schedule.id
                    )
                    results[side] = result
                    
                    if result['success']:
                        logger.info(f"Successfully set {side} side to {firmness} for schedule '{schedule.name}'")
                    else:
                        logger.error(f"Failed to set {side} side to {firmness} for schedule '{schedule.name}': {result.get('error')}")
                        
                except Exception as e:
                    logger.error(f"Exception setting {side} side for schedule '{schedule.name}': {str(e)}")
                    results[side] = {
                        'success': False,
                        'error': str(e),
                        'side': side,
                        'firmness': firmness
                    }
            
            return results
            
        except Exception as e:
            logger.error(f"Exception executing schedule '{schedule.name}': {str(e)}")
            raise
    
    def get_scheduler_status(self):
        """Get current scheduler status"""
        if not self.scheduler:
            return {'running': False, 'jobs': []}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return {
            'running': self.is_running,
            'jobs': jobs
        }
    
    def add_test_job(self, func, trigger_time):
        """Add a test job (for testing purposes)"""
        if not self.scheduler:
            raise RuntimeError("Scheduler not started")
        
        job = self.scheduler.add_job(
            func=func,
            trigger='date',
            run_date=trigger_time,
            id=f'test_job_{datetime.now().timestamp()}',
            name='Test Job'
        )
        
        return job.id

# Global scheduler instance
scheduler_service = SchedulerService()

def start_scheduler():
    """Start the scheduler service"""
    scheduler_service.start()

def get_scheduler_status():
    """Get scheduler status"""
    return scheduler_service.get_scheduler_status()
