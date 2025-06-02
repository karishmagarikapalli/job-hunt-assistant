import os
import logging
import json
from datetime import datetime
from .browser_automation import BrowserAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'application_manager.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('application_manager')

class ApplicationManager:
    """
    Manages the job application process using browser automation.
    Handles different application platforms and form types.
    """
    
    def __init__(self, config_path=None):
        """
        Initialize the application manager.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.automation = None
        self.config = self._load_config(config_path)
        self.application_stats = {
            'total_attempts': 0,
            'successful': 0,
            'failed': 0,
            'last_application': None
        }
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)
    
    def _load_config(self, config_path):
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path (str): Path to configuration file
        
        Returns:
            dict: Configuration dictionary
        """
        default_config = {
            'browser': {
                'type': 'chromium',
                'headless': True,
                'slow_mo': 100
            },
            'application': {
                'max_retries': 3,
                'timeout': 60000,
                'screenshot_on_failure': True,
                'screenshot_dir': os.path.join(os.path.dirname(__file__), 'screenshots')
            },
            'platforms': {
                'workday': {
                    'selectors': {
                        'apply_button': 'a.css-1hfgk44',
                        'email_field': 'input[name="email"]',
                        'password_field': 'input[name="password"]',
                        'submit_button': 'button[type="submit"]'
                    }
                },
                'greenhouse': {
                    'selectors': {
                        'apply_button': 'a.job-app-btn',
                        'first_name': 'input#first_name',
                        'last_name': 'input#last_name',
                        'email': 'input#email',
                        'phone': 'input#phone',
                        'resume_upload': 'input#resume',
                        'cover_letter_upload': 'input#cover_letter',
                        'submit_button': 'input[type="submit"]'
                    }
                },
                'lever': {
                    'selectors': {
                        'apply_button': 'a[data-qa="btn-apply-bottom"]',
                        'name': 'input[name="name"]',
                        'email': 'input[name="email"]',
                        'resume_upload': 'input[name="resume"]',
                        'phone': 'input[name="phone"]',
                        'company': 'input[name="org"]',
                        'submit_button': 'button[type="submit"]'
                    }
                },
                'linkedin': {
                    'selectors': {
                        'apply_button': 'button.jobs-apply-button',
                        'easy_apply_submit': 'button[aria-label="Submit application"]',
                        'next_button': 'button[aria-label="Continue to next step"]',
                        'review_button': 'button[aria-label="Review your application"]'
                    }
                }
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                
                # Merge user config with default config
                for key, value in user_config.items():
                    if key in default_config and isinstance(value, dict):
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
                
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
        
        # Create screenshot directory if it doesn't exist
        os.makedirs(default_config['application']['screenshot_dir'], exist_ok=True)
        
        return default_config
    
    def start(self):
        """
        Start the application manager.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            browser_config = self.config['browser']
            self.automation = BrowserAutomation(
                headless=browser_config['headless'],
                browser_type=browser_config['type'],
                slow_mo=browser_config['slow_mo']
            )
            
            success = self.automation.start()
            if success:
                logger.info("Application manager started")
                return True
            else:
                logger.error("Failed to start browser automation")
                return False
        except Exception as e:
            logger.error(f"Failed to start application manager: {str(e)}")
            return False
    
    def stop(self):
        """
        Stop the application manager.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            if self.automation:
                success = self.automation.close()
                self.automation = None
                
                if success:
                    logger.info("Application manager stopped")
                    return True
                else:
                    logger.error("Failed to stop browser automation")
                    return False
            return True
        except Exception as e:
            logger.error(f"Failed to stop application manager: {str(e)}")
            return False
    
    def apply_to_job(self, job_data, user_data, resume_path, cover_letter_path=None):
        """
        Apply to a job using browser automation.
        
        Args:
            job_data (dict): Job posting data
            user_data (dict): User profile data
            resume_path (str): Path to resume file
            cover_letter_path (str): Path to cover letter file (optional)
        
        Returns:
            dict: Application result with status and details
        """
        if not self.automation:
            logger.error("Browser automation not started")
            return {'success': False, 'error': 'Browser automation not started'}
        
        # Initialize result
        result = {
            'job_id': job_data.get('id'),
            'company': job_data.get('company'),
            'position': job_data.get('title'),
            'application_url': job_data.get('application_url'),
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'platform': None,
            'steps_completed': [],
            'error': None
        }
        
        # Update application stats
        self.application_stats['total_attempts'] += 1
        self.application_stats['last_application'] = datetime.now().isoformat()
        
        try:
            # Navigate to application URL
            logger.info(f"Navigating to application URL: {job_data['application_url']}")
            if not self.automation.navigate_to(job_data['application_url']):
                result['error'] = 'Failed to navigate to application URL'
                self._handle_failure(result)
                return result
            
            result['steps_completed'].append('navigation')
            
            # Detect application platform
            platform = self._detect_platform()
            if not platform:
                result['error'] = 'Failed to detect application platform'
                self._handle_failure(result)
                return result
            
            result['platform'] = platform
            result['steps_completed'].append('platform_detection')
            
            # Apply based on platform
            if platform == 'workday':
                success = self._apply_workday(job_data, user_data, resume_path, cover_letter_path)
            elif platform == 'greenhouse':
                success = self._apply_greenhouse(job_data, user_data, resume_path, cover_letter_path)
            elif platform == 'lever':
                success = self._apply_lever(job_data, user_data, resume_path, cover_letter_path)
            elif platform == 'linkedin':
                success = self._apply_linkedin(job_data, user_data, resume_path, cover_letter_path)
            else:
                success = self._apply_generic(job_data, user_data, resume_path, cover_letter_path)
            
            if success:
                result['success'] = True
                result['steps_completed'].append('submission')
                self.application_stats['successful'] += 1
                logger.info(f"Successfully applied to {job_data['title']} at {job_data['company']}")
            else:
                result['error'] = f'Failed to complete {platform} application process'
                self._handle_failure(result)
            
            return result
        except Exception as e:
            error_msg = f"Error applying to job: {str(e)}"
            logger.error(error_msg)
            result['error'] = error_msg
            self._handle_failure(result)
            return result
    
    def _detect_platform(self):
        """
        Detect the application platform based on page content.
        
        Returns:
            str: Platform name or None if not detected
        """
        try:
            # Check URL and page content for platform indicators
            current_url = self.automation.page.url
            
            # Check for Workday
            if 'myworkdayjobs.com' in current_url or self.automation.page.query_selector('div.WGDC'):
                return 'workday'
            
            # Check for Greenhouse
            if 'boards.greenhouse.io' in current_url or self.automation.page.query_selector('div#application'):
                return 'greenhouse'
            
            # Check for Lever
            if 'jobs.lever.co' in current_url or self.automation.page.query_selector('div.application-page'):
                return 'lever'
            
            # Check for LinkedIn
            if 'linkedin.com/jobs' in current_url or self.automation.page.query_selector('div.jobs-details'):
                return 'linkedin'
            
            # If no specific platform detected, return generic
            return 'generic'
        except Exception as e:
            logger.error(f"Error detecting platform: {str(e)}")
            return None
    
    def _apply_workday(self, job_data, user_data, resume_path, cover_letter_path):
        """
        Apply to a job on Workday.
        
        Returns:
            bool: True if application was successful, False otherwise
        """
        try:
            selectors = self.config['platforms']['workday']['selectors']
            
            # Click apply button
            if not self.automation.click_element(selectors['apply_button']):
                logger.warning("Apply button not found on Workday page")
                return False
            
            # Wait for navigation
            self.automation.wait_for_navigation()
            
            # Check if login is required
            if self.automation.wait_for_selector(selectors['email_field'], timeout=5000):
                # Fill login form
                self.automation.fill_form({
                    selectors['email_field']: user_data['email'],
                    selectors['password_field']: user_data.get('workday_password', '')
                })
                
                # Click login button
                if not self.automation.click_element(selectors['submit_button']):
                    logger.warning("Login button not found on Workday page")
                    return False
                
                # Wait for navigation
                self.automation.wait_for_navigation()
            
            # TODO: Implement Workday application form filling
            # This is a placeholder for the actual implementation
            logger.info("Workday application process not fully implemented")
            return False
        except Exception as e:
            logger.error(f"Error applying on Workday: {str(e)}")
            return False
    
    def _apply_greenhouse(self, job_data, user_data, resume_path, cover_letter_path):
        """
        Apply to a job on Greenhouse.
        
        Returns:
            bool: True if application was successful, False otherwise
        """
        try:
            selectors = self.config['platforms']['greenhouse']['selectors']
            
            # Click apply button if not already on application page
            if not self.automation.page.url.endswith('/apply'):
                if not self.automation.click_element(selectors['apply_button']):
                    logger.warning("Apply button not found on Greenhouse page")
                    return False
                
                # Wait for navigation
                self.automation.wait_for_navigation()
            
            # Fill application form
            form_data = {
                selectors['first_name']: user_data['first_name'],
                selectors['last_name']: user_data['last_name'],
                selectors['email']: user_data['email'],
                selectors['phone']: user_data.get('phone', ''),
                selectors['resume_upload']: {'file_path': resume_path}
            }
            
            # Add cover letter if provided
            if cover_letter_path and selectors.get('cover_letter_upload'):
                form_data[selectors['cover_letter_upload']] = {'file_path': cover_letter_path}
            
            # Fill the form
            if not self.automation.fill_form(form_data):
                logger.warning("Failed to fill Greenhouse application form")
                return False
            
            # Submit application
            if not self.automation.click_element(selectors['submit_button']):
                logger.warning("Submit button not found on Greenhouse page")
                return False
            
            # Wait for confirmation
            self.automation.wait_for_navigation()
            
            # Check for success indicators
            if self.automation.page.query_selector('div.application-confirmation'):
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error applying on Greenhouse: {str(e)}")
            return False
    
    def _apply_lever(self, job_data, user_data, resume_path, cover_letter_path):
        """
        Apply to a job on Lever.
        
        Returns:
            bool: True if application was successful, False otherwise
        """
        try:
            selectors = self.config['platforms']['lever']['selectors']
            
            # Click apply button if not already on application page
            if not self.automation.page.url.endswith('/apply'):
                if not self.automation.click_element(selectors['apply_button']):
                    logger.warning("Apply button not found on Lever page")
                    return False
                
                # Wait for navigation
                self.automation.wait_for_navigation()
            
            # Fill application form
            form_data = {
                selectors['name']: f"{user_data['first_name']} {user_data['last_name']}",
                selectors['email']: user_data['email'],
                selectors['resume_upload']: {'file_path': resume_path}
            }
            
            # Add optional fields if available
            if selectors.get('phone') and user_data.get('phone'):
                form_data[selectors['phone']] = user_data['phone']
            
            if selectors.get('company') and user_data.get('current_company'):
                form_data[selectors['company']] = user_data['current_company']
            
            # Fill the form
            if not self.automation.fill_form(form_data):
                logger.warning("Failed to fill Lever application form")
                return False
            
            # Submit application
            if not self.automation.click_element(selectors['submit_button']):
                logger.warning("Submit button not found on Lever page")
                return False
            
            # Wait for confirmation
            self.automation.wait_for_navigation()
            
            # Check for success indicators
            if self.automation.page.query_selector('div.confirmation-content'):
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error applying on Lever: {str(e)}")
            return False
    
    def _apply_linkedin(self, job_data, user_data, resume_path, cover_letter_path):
        """
        Apply to a job on LinkedIn.
        
        Returns:
            bool: True if application was successful, False otherwise
        """
        try:
            selectors = self.config['platforms']['linkedin']['selectors']
            
            # Click apply button
            if not self.automation.click_element(selectors['apply_button']):
                logger.warning("Apply button not found on LinkedIn page")
                return False
            
            # Wait for application modal to appear
            self.automation.wait_for_selector('div.jobs-easy-apply-content')
            
            # Check if it's an Easy Apply
            if self.automation.page.query_selector(selectors['easy_apply_submit']):
                # Simple one-click application
                if not self.automation.click_element(selectors['easy_apply_submit']):
                    logger.warning("Submit button not found on LinkedIn Easy Apply")
                    return False
                
                # Wait for confirmation
                self.automation.wait_for_selector('div.artdeco-modal__content', timeout=5000)
                return True
            
            # Multi-step application
            while self.automation.page.query_selector(selectors['next_button']):
                # TODO: Fill form fields based on current step
                # This is a placeholder for the actual implementation
                
                # Click next button
                if not self.automation.click_element(selectors['next_button']):
                    logger.warning("Next button not found on LinkedIn application")
                    return False
                
                # Wait for next step to load
                self.automation.wait_for_selector('div.jobs-easy-apply-content', timeout=5000)
            
            # Check for review button
            if self.automation.page.query_selector(selectors['review_button']):
                if not self.automation.click_element(selectors['review_button']):
                    logger.warning("Review button not found on LinkedIn application")
                    return False
                
                # Wait for review page to load
                self.automation.wait_for_selector('div.jobs-easy-apply-content', timeout=5000)
            
            # Submit application
            if not self.automation.click_element(selectors['easy_apply_submit']):
                logger.warning("Submit button not found on LinkedIn application")
                return False
            
            # Wait for confirmation
            self.automation.wait_for_selector('div.artdeco-modal__content', timeout=5000)
            return True
        except Exception as e:
            logger.error(f"Error applying on LinkedIn: {str(e)}")
            return False
    
    def _apply_generic(self, job_data, user_data, resume_path, cover_letter_path):
        """
        Apply to a job on a generic platform.
        
        Returns:
            bool: True if application was successful, False otherwise
        """
        try:
            # Look for common application elements
            apply_button = self.automation.page.query_selector('a:text("Apply"), button:text("Apply")')
            if apply_button:
                apply_button.click()
                self.automation.wait_for_navigation()
            
            # Look for common form fields
            form_fields = {
                'input[name="firstName"], input[name="first_name"], input#firstName, input#first_name': user_data['first_name'],
                'input[name="lastName"], input[name="last_name"], input#lastName, input#last_name': user_data['last_name'],
                'input[type="email"], input[name="email"], input#email': user_data['email'],
                'input[name="phone"], input[type="tel"], input#phone': user_data.get('phone', '')
            }
            
            # Fill form fields if found
            for selector, value in form_fields.items():
                if self.automation.page.query_selector(selector):
                    self.automation.fill_form({selector: value})
            
            # Look for resume upload
            resume_upload = self.automation.page.query_selector('input[type="file"][accept=".pdf,.doc,.docx"], input[name="resume"], input#resume')
            if resume_upload:
                self.automation.page.set_input_files(resume_upload, resume_path)
            
            # Look for cover letter upload if provided
            if cover_letter_path:
                cover_letter_upload = self.automation.page.query_selector('input[type="file"][accept=".pdf,.doc,.docx"]:not([name="resume"]), input[name="cover_letter"], input#cover_letter')
                if cover_letter_upload:
                    self.automation.page.set_input_files(cover_letter_upload, cover_letter_path)
            
            # Look for submit button
            submit_button = self.automation.page.query_selector('button[type="submit"], input[type="submit"], button:text("Submit"), button:text("Apply")')
            if submit_button:
                submit_button.click()
                self.automation.wait_for_navigation()
                return True
            
            logger.warning("Could not complete generic application process")
            return False
        except Exception as e:
            logger.error(f"Error applying on generic platform: {str(e)}")
            return False
    
    def _handle_failure(self, result):
        """
        Handle application failure.
        
        Args:
            result (dict): Application result
        """
        self.application_stats['failed'] += 1
        
        # Take screenshot if configured
        if self.config['application']['screenshot_on_failure'] and self.automation:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = os.path.join(
                self.config['application']['screenshot_dir'],
                f"failure_{result['job_id']}_{timestamp}.png"
            )
            self.automation.take_screenshot(screenshot_path)
            result['screenshot'] = screenshot_path
        
        logger.error(f"Application failed: {result['error']}")
    
    def get_stats(self):
        """
        Get application statistics.
        
        Returns:
            dict: Application statistics
        """
        return self.application_stats
