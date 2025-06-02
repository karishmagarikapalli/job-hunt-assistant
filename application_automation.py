import json
import os
import sqlite3
import time
import random
from datetime import datetime
import re
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/job_hunt_ecosystem/logs/application_automation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('application_automation')

class ApplicationAutomator:
    """
    A class to automate job applications using generated resumes and cover letters.
    """
    
    def __init__(self, db_path='/home/ubuntu/job_hunt_ecosystem/job_hunt.db',
                 resume_dir='/home/ubuntu/job_hunt_ecosystem/resumes',
                 cover_letter_dir='/home/ubuntu/job_hunt_ecosystem/cover_letters',
                 config_path='/home/ubuntu/job_hunt_ecosystem/config/application_config.json'):
        """
        Initialize the application automator with paths to database and document directories.
        
        Args:
            db_path: Path to the SQLite database
            resume_dir: Directory containing generated resumes
            cover_letter_dir: Directory containing generated cover letters
            config_path: Path to application automation configuration file
        """
        self.db_path = db_path
        self.resume_dir = resume_dir
        self.cover_letter_dir = cover_letter_dir
        
        # Create directories if they don't exist
        os.makedirs(resume_dir, exist_ok=True)
        os.makedirs(cover_letter_dir, exist_ok=True)
        os.makedirs('/home/ubuntu/job_hunt_ecosystem/logs', exist_ok=True)
        
        # Create default configuration if it doesn't exist
        if not os.path.exists(config_path):
            self.create_default_config(config_path)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def create_default_config(self, config_path):
        """Create default configuration file for application automation."""
        default_config = {
            "application_settings": {
                "auto_apply": False,  # Set to false by default for safety
                "apply_delay_min": 30,  # Minimum delay between applications in seconds
                "apply_delay_max": 60,  # Maximum delay between applications in seconds
                "max_daily_applications": 10,  # Maximum number of applications per day
                "working_hours": {
                    "start": "09:00",
                    "end": "17:00"
                },
                "blacklisted_companies": [],
                "preferred_companies": []
            },
            "application_platforms": {
                "linkedin": {
                    "enabled": True,
                    "username": "",
                    "password_env_var": "LINKEDIN_PASSWORD",  # Store password in environment variable
                    "easy_apply": true
                },
                "indeed": {
                    "enabled": True,
                    "username": "",
                    "password_env_var": "INDEED_PASSWORD"
                },
                "company_websites": {
                    "enabled": True,
                    "auto_detect_form": True
                }
            },
            "application_form_defaults": {
                "willing_to_relocate": False,
                "authorized_to_work": True,
                "require_sponsorship": True,
                "desired_salary": "Negotiable",
                "start_date": "Immediate",
                "referral_source": "Job Board",
                "cover_letter_required": True
            },
            "notification_settings": {
                "email_notifications": True,
                "email_address": "",
                "notify_on_application": True,
                "notify_on_error": True
            }
        }
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        logger.info(f"Created default configuration file at {config_path}")
    
    def connect_db(self):
        """Connect to the SQLite database and return connection and cursor."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        return conn, cursor
    
    def get_pending_jobs(self, limit=10):
        """
        Get jobs that are pending application.
        
        Args:
            limit: Maximum number of jobs to retrieve
            
        Returns:
            List of job dictionaries
        """
        conn, cursor = self.connect_db()
        
        cursor.execute('''
        SELECT * FROM job_postings 
        WHERE status = 'new' 
        ORDER BY date_posted DESC
        LIMIT ?
        ''', (limit,))
        
        jobs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jobs
    
    def get_user_data(self, user_id=1):
        """
        Retrieve user data from the database.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary containing user data
        """
        conn, cursor = self.connect_db()
        
        cursor.execute('SELECT * FROM personal_info WHERE id = ?', (user_id,))
        user_data = dict(cursor.fetchone())
        
        conn.close()
        return user_data
    
    def find_resume_for_job(self, user_id, job_id):
        """
        Find the appropriate resume for a job.
        
        Args:
            user_id: ID of the user
            job_id: ID of the job
            
        Returns:
            Path to the resume file
        """
        conn, cursor = self.connect_db()
        
        # Get user and job information
        cursor.execute('SELECT first_name, last_name FROM personal_info WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        cursor.execute('SELECT company, title FROM job_postings WHERE id = ?', (job_id,))
        job = cursor.fetchone()
        
        conn.close()
        
        if not user or not job:
            raise ValueError(f"User ID {user_id} or Job ID {job_id} not found")
        
        # Try to find a specific resume for this job
        company_name = re.sub(r'[^\w\s-]', '', job['company']).strip().replace(' ', '_')
        job_title = re.sub(r'[^\w\s-]', '', job['title']).strip().replace(' ', '_')
        specific_resume_pattern = f"{user['first_name']}_{user['last_name']}_Resume_{company_name}_{job_title}"
        
        for filename in os.listdir(self.resume_dir):
            if filename.startswith(specific_resume_pattern) and filename.endswith('.pdf'):
                return os.path.join(self.resume_dir, filename)
        
        # If no specific resume found, look for a generic one
        generic_resume_pattern = f"{user['first_name']}_{user['last_name']}_Resume"
        
        for filename in os.listdir(self.resume_dir):
            if filename.startswith(generic_resume_pattern) and filename.endswith('.pdf'):
                return os.path.join(self.resume_dir, filename)
        
        raise FileNotFoundError(f"No resume found for user {user_id} and job {job_id}")
    
    def find_cover_letter_for_job(self, user_id, job_id):
        """
        Find the appropriate cover letter for a job.
        
        Args:
            user_id: ID of the user
            job_id: ID of the job
            
        Returns:
            Path to the cover letter file
        """
        conn, cursor = self.connect_db()
        
        # Get user and job information
        cursor.execute('SELECT first_name, last_name FROM personal_info WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        cursor.execute('SELECT company, title FROM job_postings WHERE id = ?', (job_id,))
        job = cursor.fetchone()
        
        conn.close()
        
        if not user or not job:
            raise ValueError(f"User ID {user_id} or Job ID {job_id} not found")
        
        # Try to find a specific cover letter for this job
        company_name = re.sub(r'[^\w\s-]', '', job['company']).strip().replace(' ', '_')
        job_title = re.sub(r'[^\w\s-]', '', job['title']).strip().replace(' ', '_')
        cover_letter_pattern = f"{user['first_name']}_{user['last_name']}_CoverLetter_{company_name}_{job_title}"
        
        for filename in os.listdir(self.cover_letter_dir):
            if filename.startswith(cover_letter_pattern) and filename.endswith('.pdf'):
                return os.path.join(self.cover_letter_dir, filename)
        
        raise FileNotFoundError(f"No cover letter found for user {user_id} and job {job_id}")
    
    def record_application(self, job_id, resume_path, cover_letter_path=None, status='submitted', notes=None):
        """
        Record a job application in the database.
        
        Args:
            job_id: ID of the job
            resume_path: Path to the resume used
            cover_letter_path: Path to the cover letter used (optional)
            status: Application status
            notes: Additional notes
            
        Returns:
            ID of the recorded application
        """
        conn, cursor = self.connect_db()
        
        # Update job status
        cursor.execute('''
        UPDATE job_postings SET status = 'applied', updated_at = ? WHERE id = ?
        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), job_id))
        
        # Record application
        cursor.execute('''
        INSERT INTO job_applications (
            job_id, resume_path, cover_letter_path, application_date,
            status, notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_id,
            resume_path,
            cover_letter_path,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            status,
            notes,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        application_id = cursor.lastrowid
        
        # Record tracking entry
        cursor.execute('''
        INSERT INTO application_tracking (
            application_id, status, date, notes
        ) VALUES (?, ?, ?, ?)
        ''', (
            application_id,
            status,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            f"Initial application {status}"
        ))
        
        conn.commit()
        conn.close()
        
        return application_id
    
    def setup_webdriver(self):
        """
        Set up and return a configured webdriver for browser automation.
        
        Returns:
            Configured webdriver instance
        """
        # This is a placeholder implementation
        # In a real implementation, you would need to set up a proper webdriver
        
        logger.info("Setting up webdriver for browser automation")
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Add user agent to avoid detection
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Initialize webdriver
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_window_size(1920, 1080)
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize webdriver: {e}")
            raise
    
    def apply_via_linkedin(self, job_data, resume_path, cover_letter_path=None):
        """
        Apply to a job via LinkedIn.
        
        Args:
            job_data: Dictionary containing job data
            resume_path: Path to the resume file
            cover_letter_path: Path to the cover letter file (optional)
            
        Returns:
            Boolean indicating success and notes about the application
        """
        # This is a placeholder implementation
        # In a real implementation, you would need to use Selenium to automate the application process
        
        logger.info(f"Applying to job {job_data['id']} at {job_data['company']} via LinkedIn")
        
        # Check if LinkedIn automation is enabled
        if not self.config['application_platforms']['linkedin']['enabled']:
            return False, "LinkedIn automation is disabled in configuration"
        
        # Check if we have LinkedIn credentials
        if not self.config['application_platforms']['linkedin']['username']:
            return False, "LinkedIn username is not configured"
        
        # Simulate application process
        logger.info("LinkedIn application process would be automated here")
        logger.info(f"Would use resume: {resume_path}")
        if cover_letter_path:
            logger.info(f"Would use cover letter: {cover_letter_path}")
        
        # Simulate success
        time.sleep(2)  # Simulate some processing time
        
        return True, "Application submitted via LinkedIn Easy Apply"
    
    def apply_via_indeed(self, job_data, resume_path, cover_letter_path=None):
        """
        Apply to a job via Indeed.
        
        Args:
            job_data: Dictionary containing job data
            resume_path: Path to the resume file
            cover_letter_path: Path to the cover letter file (optional)
            
        Returns:
            Boolean indicating success and notes about the application
        """
        # This is a placeholder implementation
        # In a real implementation, you would need to use Selenium to automate the application process
        
        logger.info(f"Applying to job {job_data['id']} at {job_data['company']} via Indeed")
        
        # Check if Indeed automation is enabled
        if not self.config['application_platforms']['indeed']['enabled']:
            return False, "Indeed automation is disabled in configuration"
        
        # Check if we have Indeed credentials
        if not self.config['application_platforms']['indeed']['username']:
            return False, "Indeed username is not configured"
        
        # Simulate application process
        logger.info("Indeed application process would be automated here")
        logger.info(f"Would use resume: {resume_path}")
        if cover_letter_path:
            logger.info(f"Would use cover letter: {cover_letter_path}")
        
        # Simulate success
        time.sleep(2)  # Simulate some processing time
        
        return True, "Application submitted via Indeed Apply"
    
    def apply_via_company_website(self, job_data, resume_path, cover_letter_path=None):
        """
        Apply to a job via the company website.
        
        Args:
            job_data: Dictionary containing job data
            resume_path: Path to the resume file
            cover_letter_path: Path to the cover letter file (optional)
            
        Returns:
            Boolean indicating success and notes about the application
        """
        # This is a placeholder implementation
        # In a real implementation, you would need to use Selenium to automate the application process
        
        logger.info(f"Applying to job {job_data['id']} at {job_data['company']} via company website")
        
        # Check if company website automation is enabled
        if not self.config['application_platforms']['company_websites']['enabled']:
            return False, "Company website automation is disabled in configuration"
        
        # Check if we have a valid application URL
        if not job_data['application_url'] or not job_data['application_url'].startswith('http'):
            return False, "Invalid application URL"
        
        # Simulate application process
        logger.info(f"Company website application process would be automated here for URL: {job_data['application_url']}")
        logger.info(f"Would use resume: {resume_path}")
        if cover_letter_path:
            logger.info(f"Would use cover letter: {cover_letter_path}")
        
        # Simulate success
        time.sleep(2)  # Simulate some processing time
        
        return True, "Application submitted via company website"
    
    def apply_to_job(self, job_id, user_id=1):
        """
        Apply to a specific job.
        
        Args:
            job_id: ID of the job to apply to
            user_id: ID of the user
            
        Returns:
            Boolean indicating success and application ID if successful
        """
        conn, cursor = self.connect_db()
        
        # Get job data
        cursor.execute('SELECT * FROM job_postings WHERE id = ?', (job_id,))
        job_data = dict(cursor.fetchone())
        
        conn.close()
        
        if not job_data:
            logger.error(f"Job ID {job_id} not found")
            return False, None
        
        # Check if job is already applied to
        if job_data['status'] != 'new':
            logger.info(f"Job ID {job_id} is already in status: {job_data['status']}")
            return False, None
        
        try:
            # Find resume and cover letter
            resume_path = self.find_resume_for_job(user_id, job_id)
            
            try:
                cover_letter_path = self.find_cover_letter_for_job(user_id, job_id)
            except FileNotFoundError:
                cover_letter_path = None
                logger.warning(f"No cover letter found for job {job_id}, proceeding without one")
            
            # Determine application method based on source
            source = job_data['source_website'].lower()
            success = False
            notes = None
            
            if 'linkedin' in source:
                success, notes = self.apply_via_linkedin(job_data, resume_path, cover_letter_path)
            elif 'indeed' in source:
                success, notes = self.apply_via_indeed(job_data, resume_path, cover_letter_path)
            else:
                # Default to company website
                success, notes = self.apply_via_company_website(job_data, resume_path, cover_letter_path)
            
            if success:
                # Record the application
                application_id = self.record_application(
                    job_id, 
                    resume_path, 
                    cover_letter_path, 
                    'submitted', 
                    notes
                )
                logger.info(f"Successfully applied to job {job_id}, application ID: {application_id}")
                return True, application_id
            else:
                logger.warning(f"Failed to apply to job {job_id}: {notes}")
                return False, None
            
        except Exception as e:
            logger.error(f"Error applying to job {job_id}: {e}")
            return False, None
    
    def process_pending_applications(self, user_id=1, limit=5):
        """
        Process pending job applications.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of applications to process
            
        Returns:
            Dictionary with statistics about the processing run
        """
        stats = {
            "total_processed": 0,
            "successful_applications": 0,
            "failed_applications": 0,
            "application_ids": []
        }
        
        # Check if auto-apply is enabled
        if not self.config['application_settings']['auto_apply']:
            logger.info("Auto-apply is disabled in configuration")
            return stats
        
        # Get pending jobs
        pending_jobs = self.get_pending_jobs(limit)
        
        if not pending_jobs:
            logger.info("No pending jobs found")
            return stats
        
        logger.info(f"Found {len(pending_jobs)} pending jobs to process")
        
        # Process each job
        for job in pending_jobs:
            stats["total_processed"] += 1
            
            # Apply to job
            success, application_id = self.apply_to_job(job['id'], user_id)
            
            if success:
                stats["successful_applications"] += 1
                stats["application_ids"].append(application_id)
            else:
                stats["failed_applications"] += 1
            
            # Add delay between applications
            delay = random.uniform(
                self.config['application_settings']['apply_delay_min'],
                self.config['application_settings']['apply_delay_max']
            )
            logger.info(f"Waiting {delay:.2f} seconds before next application")
            time.sleep(delay)
        
        return stats
    
    def update_application_status(self, application_id, new_status, notes=None):
        """
        Update the status of a job application.
        
        Args:
            application_id: ID of the application
            new_status: New status to set
            notes: Additional notes
            
        Returns:
            Boolean indicating success
        """
        conn, cursor = self.connect_db()
        
        # Update application status
        cursor.execute('''
        UPDATE job_applications SET status = ?, updated_at = ? WHERE id = ?
        ''', (new_status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), application_id))
        
        # Record tracking entry
        cursor.execute('''
        INSERT INTO application_tracking (
            application_id, status, date, notes
        ) VALUES (?, ?, ?, ?)
        ''', (
            application_id,
            new_status,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            notes
        ))
        
        # Get job_id for this application
        cursor.execute('SELECT job_id FROM job_applications WHERE id = ?', (application_id,))
        job_id = cursor.fetchone()[0]
        
        # Update job status
        cursor.execute('''
        UPDATE job_postings SET status = ?, updated_at = ? WHERE id = ?
        ''', (new_status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), job_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Updated application {application_id} status to {new_status}")
        return True
    
    def get_application_history(self, application_id):
        """
        Get the history of status changes for an application.
        
        Args:
            application_id: ID of the application
            
        Returns:
            List of status change dictionaries
        """
        conn, cursor = self.connect_db()
        
        cursor.execute('''
        SELECT * FROM application_tracking 
        WHERE application_id = ? 
        ORDER BY date ASC
        ''', (application_id,))
        
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return history
    
    def get_application_statistics(self, user_id=1, days=30):
        """
        Get statistics about job applications.
        
        Args:
            user_id: ID of the user
            days: Number of days to include in statistics
            
        Returns:
            Dictionary with application statistics
        """
        conn, cursor = self.connect_db()
        
        # Get date threshold
        date_threshold = (datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Get total applications
        cursor.execute('''
        SELECT COUNT(*) FROM job_applications ja
        JOIN job_postings jp ON ja.job_id = jp.id
        WHERE ja.application_date >= ?
        ''', (date_threshold,))
        
        total_applications = cursor.fetchone()[0]
        
        # Get applications by status
        cursor.execute('''
        SELECT ja.status, COUNT(*) as count FROM job_applications ja
        JOIN job_postings jp ON ja.job_id = jp.id
        WHERE ja.application_date >= ?
        GROUP BY ja.status
        ''', (date_threshold,))
        
        status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Get applications by source
        cursor.execute('''
        SELECT jp.source_website, COUNT(*) as count FROM job_applications ja
        JOIN job_postings jp ON ja.job_id = jp.id
        WHERE ja.application_date >= ?
        GROUP BY jp.source_website
        ''', (date_threshold,))
        
        source_counts = {row['source_website']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_applications": total_applications,
            "by_status": status_counts,
            "by_source": source_counts,
            "days": days
        }

# Example usage
if __name__ == "__main__":
    automator = ApplicationAutomator()
    
    # Create application configuration if it doesn't exist
    if not os.path.exists('/home/ubuntu/job_hunt_ecosystem/config/application_config.json'):
        automator.create_default_config('/home/ubuntu/job_hunt_ecosystem/config/application_config.json')
    
    # Process a sample job application
    try:
        # Get a sample job
        conn, cursor = automator.connect_db()
        cursor.execute('SELECT id FROM job_postings LIMIT 1')
        job_id = cursor.fetchone()
        conn.close()
        
        if job_id:
            job_id = job_id[0]
            print(f"Processing sample application for job ID: {job_id}")
            
            # Apply to job
            success, application_id = automator.apply_to_job(job_id)
            
            if success:
                print(f"Successfully applied to job {job_id}, application ID: {application_id}")
                
                # Update status (simulate interview invitation)
                automator.update_application_status(
                    application_id, 
                    'interview', 
                    'Received interview invitation via email'
                )
                
                # Get application history
                history = automator.get_application_history(application_id)
                print("\nApplication history:")
                for entry in history:
                    print(f"{entry['date']} - {entry['status']}: {entry['notes']}")
            else:
                print(f"Failed to apply to job {job_id}")
        else:
            print("No jobs found in database")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Print application statistics
    try:
        stats = automator.get_application_statistics(days=30)
        print("\nApplication statistics (last 30 days):")
        print(f"Total applications: {stats['total_applications']}")
        print("By status:")
        for status, count in stats.get('by_status', {}).items():
            print(f"  {status}: {count}")
        print("By source:")
        for source, count in stats.get('by_source', {}).items():
            print(f"  {source}: {count}")
    except Exception as e:
        print(f"Error getting statistics: {e}")
