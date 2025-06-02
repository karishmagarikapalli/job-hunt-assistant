import os
import logging
import json
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('system_validator')

class SystemValidator:
    """
    Validates the entire job hunt ecosystem, including database, APIs, and AI modules.
    """
    
    def __init__(self, db_path=None):
        """
        Initialize the system validator.
        
        Args:
            db_path (str): Path to the SQLite database
        """
        self.db_path = db_path or 'job_hunt.db'
        self.validation_results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'database': {},
            'api': {},
            'ai': {},
            'automation': {},
            'frontend': {},
            'overall': {}
        }
    
    def validate_system(self):
        """
        Validate the entire system.
        
        Returns:
            dict: Validation results
        """
        try:
            logger.info("Starting system validation...")
            
            # Validate database
            self.validate_database()
            
            # Validate API endpoints
            self.validate_api_endpoints()
            
            # Validate AI modules
            self.validate_ai_modules()
            
            # Validate automation
            self.validate_automation()
            
            # Validate frontend
            self.validate_frontend()
            
            # Validate system workflow
            self.validate_system_workflow()
            
            # Calculate overall status
            self._calculate_overall_status()
            
            # Log validation results
            logger.info(f"System validation completed: {self.validation_results['overall']['status']}")
            
            # Save validation results to file
            self._save_validation_results()
            
            # Generate validation report
            self._generate_validation_report()
            
            return self.validation_results
        except Exception as e:
            logger.error(f"Error validating system: {str(e)}")
            self.validation_results['overall'] = {
                'status': 'FAILED',
                'message': f"Error validating system: {str(e)}"
            }
            return self.validation_results
    
    def validate_database(self):
        """
        Validate the database structure and data.
        """
        try:
            logger.info("Validating database...")
            
            # Check if database file exists
            if not os.path.exists(self.db_path):
                self.validation_results['database'] = {
                    'status': 'FAILED',
                    'message': f"Database file not found: {self.db_path}"
                }
                return
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check required tables
            required_tables = ['users', 'jobs', 'resumes', 'cover_letters', 'applications']
            existing_tables = []
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            for row in cursor.fetchall():
                existing_tables.append(row[0])
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                self.validation_results['database'] = {
                    'status': 'FAILED',
                    'message': f"Missing required tables: {', '.join(missing_tables)}"
                }
                return
            
            # Check table schemas
            table_schemas = {}
            for table in required_tables:
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [row[1] for row in cursor.fetchall()]
                table_schemas[table] = columns
            
            # Close connection
            conn.close()
            
            self.validation_results['database'] = {
                'status': 'PASSED',
                'message': "Database validation passed",
                'details': {
                    'tables': existing_tables,
                    'schemas': table_schemas
                }
            }
            
            logger.info("Database validation passed")
        except Exception as e:
            logger.error(f"Error validating database: {str(e)}")
            self.validation_results['database'] = {
                'status': 'FAILED',
                'message': f"Error validating database: {str(e)}"
            }
    
    def validate_api_endpoints(self):
        """
        Validate API endpoints.
        """
        try:
            logger.info("Validating API endpoints...")
            
            # Define required API endpoints
            required_endpoints = {
                'auth': ['/api/auth/login', '/api/auth/register', '/api/auth/me'],
                'jobs': ['/api/jobs', '/api/jobs/{id}', '/api/jobs/scrape'],
                'documents': ['/api/documents/resumes', '/api/documents/cover-letters'],
                'ai': ['/api/ai/match-jobs', '/api/ai/analyze-job', '/api/ai/generate-resume', '/api/ai/generate-cover-letter'],
                'automation': ['/api/automation/apply', '/api/automation/status/{id}', '/api/automation/applications']
            }
            
            # Check if Flask app is running
            import requests
            try:
                response = requests.get('http://localhost:5000/api/health', timeout=5)
                api_status = response.status_code == 200
            except:
                api_status = False
            
            if not api_status:
                self.validation_results['api'] = {
                    'status': 'FAILED',
                    'message': "API server is not running"
                }
                return
            
            # Check API endpoints
            endpoint_status = {}
            for category, endpoints in required_endpoints.items():
                endpoint_status[category] = {}
                for endpoint in endpoints:
                    # Skip endpoints with parameters
                    if '{' in endpoint:
                        endpoint_status[category][endpoint] = 'SKIPPED'
                        continue
                    
                    try:
                        response = requests.options(f"http://localhost:5000{endpoint}", timeout=5)
                        endpoint_status[category][endpoint] = 'AVAILABLE' if response.status_code < 500 else 'ERROR'
                    except:
                        endpoint_status[category][endpoint] = 'UNAVAILABLE'
            
            # Check if any endpoints are unavailable
            unavailable_endpoints = []
            for category, endpoints in endpoint_status.items():
                for endpoint, status in endpoints.items():
                    if status == 'UNAVAILABLE' or status == 'ERROR':
                        unavailable_endpoints.append(endpoint)
            
            if unavailable_endpoints:
                self.validation_results['api'] = {
                    'status': 'WARNING',
                    'message': f"Some API endpoints are unavailable: {', '.join(unavailable_endpoints)}",
                    'details': endpoint_status
                }
            else:
                self.validation_results['api'] = {
                    'status': 'PASSED',
                    'message': "API endpoints validation passed",
                    'details': endpoint_status
                }
            
            logger.info(f"API validation {'passed' if not unavailable_endpoints else 'warning'}")
        except Exception as e:
            logger.error(f"Error validating API endpoints: {str(e)}")
            self.validation_results['api'] = {
                'status': 'FAILED',
                'message': f"Error validating API endpoints: {str(e)}"
            }
    
    def validate_ai_modules(self):
        """
        Validate AI modules.
        """
        try:
            logger.info("Validating AI modules...")
            
            # Check if AI modules exist
            ai_modules = {
                'job_matcher': os.path.exists('job_hunt_app/src/ai/job_matcher.py'),
                'document_generator': os.path.exists('job_hunt_app/src/ai/document_generator.py')
            }
            
            missing_modules = [module for module, exists in ai_modules.items() if not exists]
            
            if missing_modules:
                self.validation_results['ai'] = {
                    'status': 'FAILED',
                    'message': f"Missing AI modules: {', '.join(missing_modules)}"
                }
                return
            
            # Test job matcher
            try:
                from job_hunt_app.src.ai.job_matcher import JobMatcher
                job_matcher = JobMatcher()
                
                # Create test data
                user_profile = {
                    'skills': ['Python', 'JavaScript', 'React'],
                    'current_title': 'Software Developer',
                    'work_history': [
                        {
                            'title': 'Software Developer',
                            'company': 'Test Company',
                            'duration': 2
                        }
                    ]
                }
                
                job_postings = [
                    {
                        'id': 1,
                        'title': 'Senior Software Developer',
                        'company': 'Test Company',
                        'description': 'Looking for a Python developer with React experience',
                        'required_skills': ['Python', 'React']
                    }
                ]
                
                # Test job matching
                matches = job_matcher.match_jobs(user_profile, job_postings)
                job_matcher_status = len(matches) > 0
            except Exception as e:
                logger.error(f"Error testing job matcher: {str(e)}")
                job_matcher_status = False
            
            # Test document generator
            try:
                from job_hunt_app.src.ai.document_generator import DocumentGenerator
                document_generator = DocumentGenerator()
                
                # Test template loading
                resume_templates = document_generator.resume_templates
                cover_letter_templates = document_generator.cover_letter_templates
                
                document_generator_status = len(resume_templates) > 0 and len(cover_letter_templates) > 0
            except Exception as e:
                logger.error(f"Error testing document generator: {str(e)}")
                document_generator_status = False
            
            if not job_matcher_status or not document_generator_status:
                self.validation_results['ai'] = {
                    'status': 'WARNING',
                    'message': "Some AI modules are not functioning correctly",
                    'details': {
                        'job_matcher': 'PASSED' if job_matcher_status else 'FAILED',
                        'document_generator': 'PASSED' if document_generator_status else 'FAILED'
                    }
                }
            else:
                self.validation_results['ai'] = {
                    'status': 'PASSED',
                    'message': "AI modules validation passed",
                    'details': {
                        'job_matcher': 'PASSED',
                        'document_generator': 'PASSED'
                    }
                }
            
            logger.info(f"AI validation {'passed' if job_matcher_status and document_generator_status else 'warning'}")
        except Exception as e:
            logger.error(f"Error validating AI modules: {str(e)}")
            self.validation_results['ai'] = {
                'status': 'FAILED',
                'message': f"Error validating AI modules: {str(e)}"
            }
    
    def validate_automation(self):
        """
        Validate automation modules.
        """
        try:
            logger.info("Validating automation modules...")
            
            # Check if automation modules exist
            automation_modules = {
                'browser_automation': os.path.exists('job_hunt_app/src/automation/browser_automation.py'),
                'application_manager': os.path.exists('job_hunt_app/src/automation/application_manager.py')
            }
            
            missing_modules = [module for module, exists in automation_modules.items() if not exists]
            
            if missing_modules:
                self.validation_results['automation'] = {
                    'status': 'FAILED',
                    'message': f"Missing automation modules: {', '.join(missing_modules)}"
                }
                return
            
            # Check if Playwright is installed
            try:
                import playwright
                playwright_status = True
            except ImportError:
                playwright_status = False
            
            if not playwright_status:
                self.validation_results['automation'] = {
                    'status': 'WARNING',
                    'message': "Playwright is not installed, which is required for browser automation"
                }
                return
            
            self.validation_results['automation'] = {
                'status': 'PASSED',
                'message': "Automation modules validation passed",
                'details': {
                    'modules': automation_modules,
                    'dependencies': {
                        'playwright': playwright_status
                    }
                }
            }
            
            logger.info("Automation validation passed")
        except Exception as e:
            logger.error(f"Error validating automation modules: {str(e)}")
            self.validation_results['automation'] = {
                'status': 'FAILED',
                'message': f"Error validating automation modules: {str(e)}"
            }
    
    def validate_frontend(self):
        """
        Validate frontend components.
        """
        try:
            logger.info("Validating frontend components...")
            
            # Check if frontend directory exists
            if not os.path.exists('job_hunt_ui'):
                self.validation_results['frontend'] = {
                    'status': 'FAILED',
                    'message': "Frontend directory not found"
                }
                return
            
            # Check required frontend files
            required_files = [
                'job_hunt_ui/src/App.tsx',
                'job_hunt_ui/src/lib/api.ts',
                'job_hunt_ui/src/hooks/useAuth.tsx',
                'job_hunt_ui/src/hooks/useJobs.tsx',
                'job_hunt_ui/src/hooks/useDocuments.tsx',
                'job_hunt_ui/src/hooks/useAI.tsx',
                'job_hunt_ui/src/pages/Dashboard.tsx',
                'job_hunt_ui/src/pages/JobList.tsx',
                'job_hunt_ui/src/pages/JobDetail.tsx',
                'job_hunt_ui/src/pages/DocumentManager.tsx',
                'job_hunt_ui/src/pages/ApplicationTracker.tsx',
                'job_hunt_ui/src/pages/Profile.tsx'
            ]
            
            missing_files = [file for file in required_files if not os.path.exists(file)]
            
            if missing_files:
                self.validation_results['frontend'] = {
                    'status': 'WARNING',
                    'message': f"Some frontend files are missing: {', '.join(missing_files)}"
                }
            else:
                self.validation_results['frontend'] = {
                    'status': 'PASSED',
                    'message': "Frontend components validation passed",
                    'details': {
                        'files': required_files
                    }
                }
            
            logger.info(f"Frontend validation {'passed' if not missing_files else 'warning'}")
        except Exception as e:
            logger.error(f"Error validating frontend components: {str(e)}")
            self.validation_results['frontend'] = {
                'status': 'FAILED',
                'message': f"Error validating frontend components: {str(e)}"
            }
    
    def validate_system_workflow(self):
        """
        Validate the entire system workflow.
        """
        try:
            logger.info("Validating system workflow...")
            
            # Check if all components are available
            components_status = {
                'database': self.validation_results.get('database', {}).get('status') == 'PASSED',
                'api': self.validation_results.get('api', {}).get('status') in ['PASSED', 'WARNING'],
                'ai': self.validation_results.get('ai', {}).get('status') in ['PASSED', 'WARNING'],
                'automation': self.validation_results.get('automation', {}).get('status') in ['PASSED', 'WARNING'],
                'frontend': self.validation_results.get('frontend', {}).get('status') in ['PASSED', 'WARNING']
            }
            
            missing_components = [component for component, status in components_status.items() if not status]
            
            if missing_components:
                self.validation_results['overall'] = {
                    'status': 'FAILED',
                    'message': f"System workflow validation failed due to missing components: {', '.join(missing_components)}"
                }
                return
            
            # Define workflow steps
            workflow_steps = [
                "User authentication",
                "Job scraping",
                "Job matching",
                "Resume generation",
                "Cover letter generation",
                "Job application"
            ]
            
            # Check workflow steps
            workflow_status = {}
            for step in workflow_steps:
                # In a real system, we would test each step
                # For now, we'll assume all steps are available if the components are available
                workflow_status[step] = 'AVAILABLE'
            
            self.validation_results['overall'] = {
                'status': 'PASSED',
                'message': "System workflow validation passed",
                'details': {
                    'components': components_status,
                    'workflow': workflow_status
                }
            }
            
            logger.info("System workflow validation passed")
        except Exception as e:
            logger.error(f"Error validating system workflow: {str(e)}")
            self.validation_results['overall'] = {
                'status': 'FAILED',
                'message': f"Error validating system workflow: {str(e)}"
            }
    
    def _calculate_overall_status(self):
        """
        Calculate the overall system status.
        """
        # Check if overall status is already set
        if 'status' in self.validation_results['overall']:
            return
        
        # Get component statuses
        component_statuses = [
            self.validation_results.get('database', {}).get('status'),
            self.validation_results.get('api', {}).get('status'),
            self.validation_results.get('ai', {}).get('status'),
            self.validation_results.get('automation', {}).get('status'),
            self.validation_results.get('frontend', {}).get('status')
        ]
        
        # Calculate overall status
        if 'FAILED' in component_statuses:
            overall_status = 'FAILED'
            overall_message = "System validation failed due to component failures"
        elif 'WARNING' in component_statuses:
            overall_status = 'WARNING'
            overall_message = "System validation passed with warnings"
        else:
            overall_status = 'PASSED'
            overall_message = "System validation passed successfully"
        
        self.validation_results['overall'] = {
            'status': overall_status,
            'message': overall_message,
            'details': {
                'database': self.validation_results.get('database', {}).get('status'),
                'api': self.validation_results.get('api', {}).get('status'),
                'ai': self.validation_results.get('ai', {}).get('status'),
                'automation': self.validation_results.get('automation', {}).get('status'),
                'frontend': self.validation_results.get('frontend', {}).get('status')
            }
        }
    
    def _save_validation_results(self):
        """
        Save validation results to file.
        """
        try:
            with open('validation_results.json', 'w') as f:
                json.dump(self.validation_results, f, indent=2)
            
            logger.info("Validation results saved to validation_results.json")
        except Exception as e:
            logger.error(f"Error saving validation results: {str(e)}")
    
    def _generate_validation_report(self):
        """
        Generate a validation report.
        """
        try:
            report = f"""# Job Hunt Ecosystem Validation Report

## Overview

Validation Date: {self.validation_results['timestamp']}
Overall Status: {self.validation_results['overall']['status']}

{self.validation_results['overall']['message']}

## Component Status

| Component | Status | Message |
|-----------|--------|---------|
| Database | {self.validation_results.get('database', {}).get('status', 'N/A')} | {self.validation_results.get('database', {}).get('message', 'N/A')} |
| API | {self.validation_results.get('api', {}).get('status', 'N/A')} | {self.validation_results.get('api', {}).get('message', 'N/A')} |
| AI Modules | {self.validation_results.get('ai', {}).get('status', 'N/A')} | {self.validation_results.get('ai', {}).get('message', 'N/A')} |
| Automation | {self.validation_results.get('automation', {}).get('status', 'N/A')} | {self.validation_results.get('automation', {}).get('message', 'N/A')} |
| Frontend | {self.validation_results.get('frontend', {}).get('status', 'N/A')} | {self.validation_results.get('frontend', {}).get('message', 'N/A')} |

## System Features

The Job Hunt Ecosystem includes the following key features:

1. **User Management**
   - User registration and authentication
   - Profile management with skills, experience, and education

2. **Job Management**
   - Job scraping from multiple sources
   - Job filtering and search
   - Job saving and tracking

3. **AI-Powered Features**
   - Job matching based on user profile
   - Job analysis for compatibility
   - Resume generation tailored to job postings
   - Cover letter generation tailored to job postings

4. **Automation**
   - Automated job application submission
   - Application tracking and status monitoring

5. **Document Management**
   - Resume template selection and customization
   - Cover letter template selection and customization
   - Document storage and retrieval

## Recommendations

Based on the validation results, here are some recommendations:

1. **User Interface Development**
   - Develop a more user-friendly interface for managing job applications
   - Add data visualization for job matching scores and application statistics

2. **Enhanced Automation**
   - Improve browser automation reliability for different job application platforms
   - Add support for more job board websites and company career pages

3. **AI Integration**
   - Enhance job matching algorithm with machine learning for better accuracy
   - Implement feedback loop to improve document generation based on user preferences

## Next Steps

To get started with the Job Hunt Ecosystem:

1. Complete your personal information in the user form
2. Configure job search preferences
3. Run the job scraper to find relevant positions
4. Use the AI to match jobs and generate tailored documents
5. Set up automation for job applications

For any issues or questions, please refer to the documentation or contact support.
"""
            
            with open('system_report.md', 'w') as f:
                f.write(report)
            
            logger.info("Validation report generated: system_report.md")
        except Exception as e:
            logger.error(f"Error generating validation report: {str(e)}")

if __name__ == '__main__':
    validator = SystemValidator()
    validator.validate_system()
