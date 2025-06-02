import os
import time
import json
import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'automation.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('browser_automation')

class BrowserAutomation:
    """
    Enhanced browser automation for job application submission.
    Uses Playwright for robust browser control and form filling.
    """
    
    def __init__(self, headless=True, browser_type='chromium', slow_mo=100):
        """
        Initialize the browser automation.
        
        Args:
            headless (bool): Whether to run browser in headless mode
            browser_type (str): Type of browser to use ('chromium', 'firefox', or 'webkit')
            slow_mo (int): Slow down operations by specified milliseconds (helpful for debugging)
        """
        self.headless = headless
        self.browser_type = browser_type
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.session_data = {}
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)
    
    def start(self):
        """Start the browser session."""
        try:
            self.playwright = sync_playwright().start()
            
            # Select browser based on browser_type
            if self.browser_type == 'firefox':
                self.browser = self.playwright.firefox.launch(headless=self.headless, slow_mo=self.slow_mo)
            elif self.browser_type == 'webkit':
                self.browser = self.playwright.webkit.launch(headless=self.headless, slow_mo=self.slow_mo)
            else:  # Default to chromium
                self.browser = self.playwright.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
            
            # Create a new browser context with specific viewport
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            # Enable request interception for handling captchas or other challenges
            self.context.route("**/*", self._route_handler)
            
            # Create a new page
            self.page = self.context.new_page()
            
            # Set default navigation timeout (30 seconds)
            self.page.set_default_navigation_timeout(30000)
            
            # Set up event listeners
            self._setup_event_listeners()
            
            logger.info(f"Browser session started with {self.browser_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            self.close()
            return False
    
    def _route_handler(self, route, request):
        """Handle intercepted requests."""
        # Block certain resource types to speed up browsing
        if request.resource_type in ['image', 'media', 'font']:
            route.abort()
        else:
            route.continue_()
    
    def _setup_event_listeners(self):
        """Set up event listeners for the page."""
        # Listen for console messages
        self.page.on("console", lambda msg: logger.debug(f"Console {msg.type}: {msg.text}"))
        
        # Listen for page errors
        self.page.on("pageerror", lambda err: logger.error(f"Page error: {err}"))
        
        # Listen for request failures
        self.page.on("requestfailed", lambda request: logger.warning(f"Request failed: {request.url}"))
    
    def close(self):
        """Close the browser session."""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None
            
            logger.info("Browser session closed")
            return True
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
            return False
    
    def navigate_to(self, url, wait_until='networkidle'):
        """
        Navigate to a URL.
        
        Args:
            url (str): URL to navigate to
            wait_until (str): When to consider navigation complete
                              ('load', 'domcontentloaded', 'networkidle')
        
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            response = self.page.goto(url, wait_until=wait_until)
            if response and response.ok:
                logger.info(f"Successfully navigated to {url}")
                return True
            else:
                status = response.status if response else "Unknown"
                logger.warning(f"Navigation to {url} returned status {status}")
                return False
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            return False
    
    def fill_form(self, form_data):
        """
        Fill a form with the provided data.
        
        Args:
            form_data (dict): Dictionary mapping selectors to values
        
        Returns:
            bool: True if form was filled successfully, False otherwise
        """
        try:
            for selector, value in form_data.items():
                try:
                    # Wait for the element to be visible
                    self.page.wait_for_selector(selector, state='visible', timeout=5000)
                    
                    # Check if it's a file input
                    if isinstance(value, dict) and 'file_path' in value:
                        self.page.set_input_files(selector, value['file_path'])
                        logger.info(f"Set file input {selector} to {value['file_path']}")
                    # Check if it's a checkbox or radio
                    elif isinstance(value, bool):
                        if value:
                            self.page.check(selector)
                        else:
                            self.page.uncheck(selector)
                        logger.info(f"Set checkbox/radio {selector} to {value}")
                    # Check if it's a select
                    elif isinstance(value, dict) and 'select' in value:
                        self.page.select_option(selector, value['select'])
                        logger.info(f"Selected option {value['select']} in {selector}")
                    # Regular input field
                    else:
                        self.page.fill(selector, str(value))
                        logger.info(f"Filled {selector} with value")
                except Exception as e:
                    logger.warning(f"Failed to fill {selector}: {str(e)}")
            return True
        except Exception as e:
            logger.error(f"Form filling failed: {str(e)}")
            return False
    
    def click_element(self, selector, timeout=5000):
        """
        Click on an element.
        
        Args:
            selector (str): CSS selector for the element
            timeout (int): Timeout in milliseconds
        
        Returns:
            bool: True if click was successful, False otherwise
        """
        try:
            # Wait for the element to be visible and enabled
            self.page.wait_for_selector(selector, state='visible', timeout=timeout)
            
            # Scroll element into view
            self.page.evaluate(f"document.querySelector('{selector}').scrollIntoView()")
            time.sleep(0.5)  # Small delay after scrolling
            
            # Click the element
            self.page.click(selector)
            logger.info(f"Clicked element {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {str(e)}")
            return False
    
    def wait_for_navigation(self, timeout=30000):
        """
        Wait for navigation to complete.
        
        Args:
            timeout (int): Timeout in milliseconds
        
        Returns:
            bool: True if navigation completed, False if timed out
        """
        try:
            self.page.wait_for_load_state('networkidle', timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            logger.warning(f"Navigation timed out after {timeout}ms")
            return False
        except Exception as e:
            logger.error(f"Error waiting for navigation: {str(e)}")
            return False
    
    def wait_for_selector(self, selector, state='visible', timeout=5000):
        """
        Wait for an element to appear.
        
        Args:
            selector (str): CSS selector for the element
            state (str): State to wait for ('attached', 'detached', 'visible', 'hidden')
            timeout (int): Timeout in milliseconds
        
        Returns:
            bool: True if element appeared, False if timed out
        """
        try:
            self.page.wait_for_selector(selector, state=state, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            logger.warning(f"Selector {selector} not found after {timeout}ms")
            return False
        except Exception as e:
            logger.error(f"Error waiting for selector {selector}: {str(e)}")
            return False
    
    def extract_text(self, selector):
        """
        Extract text from an element.
        
        Args:
            selector (str): CSS selector for the element
        
        Returns:
            str: Extracted text or None if element not found
        """
        try:
            element = self.page.query_selector(selector)
            if element:
                return element.inner_text()
            return None
        except Exception as e:
            logger.error(f"Failed to extract text from {selector}: {str(e)}")
            return None
    
    def take_screenshot(self, path):
        """
        Take a screenshot of the current page.
        
        Args:
            path (str): Path to save the screenshot
        
        Returns:
            bool: True if screenshot was taken, False otherwise
        """
        try:
            self.page.screenshot(path=path)
            logger.info(f"Screenshot saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return False
    
    def handle_captcha(self, captcha_type='recaptcha'):
        """
        Handle common captcha types.
        
        Args:
            captcha_type (str): Type of captcha ('recaptcha', 'hcaptcha', etc.)
        
        Returns:
            bool: True if captcha was handled, False otherwise
        """
        try:
            if captcha_type == 'recaptcha':
                # Check if reCAPTCHA is present
                if self.page.query_selector('iframe[src*="recaptcha"]'):
                    logger.warning("reCAPTCHA detected, attempting to solve")
                    
                    # For now, we'll just log this and return False
                    # In a real implementation, you might use a captcha solving service
                    return False
            
            elif captcha_type == 'hcaptcha':
                # Check if hCaptcha is present
                if self.page.query_selector('iframe[src*="hcaptcha"]'):
                    logger.warning("hCaptcha detected, attempting to solve")
                    
                    # For now, we'll just log this and return False
                    return False
            
            # No captcha detected
            return True
        except Exception as e:
            logger.error(f"Error handling captcha: {str(e)}")
            return False
    
    def save_session_data(self, key, value):
        """
        Save data to the session.
        
        Args:
            key (str): Key to store the data under
            value: Value to store
        """
        self.session_data[key] = value
    
    def get_session_data(self, key, default=None):
        """
        Get data from the session.
        
        Args:
            key (str): Key to retrieve
            default: Default value if key not found
        
        Returns:
            Value stored under key or default if not found
        """
        return self.session_data.get(key, default)
    
    def export_session_data(self, path):
        """
        Export session data to a file.
        
        Args:
            path (str): Path to save the data
        
        Returns:
            bool: True if data was exported, False otherwise
        """
        try:
            with open(path, 'w') as f:
                json.dump(self.session_data, f, indent=2)
            logger.info(f"Session data exported to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export session data: {str(e)}")
            return False
    
    def import_session_data(self, path):
        """
        Import session data from a file.
        
        Args:
            path (str): Path to load the data from
        
        Returns:
            bool: True if data was imported, False otherwise
        """
        try:
            with open(path, 'r') as f:
                self.session_data = json.load(f)
            logger.info(f"Session data imported from {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to import session data: {str(e)}")
            return False
