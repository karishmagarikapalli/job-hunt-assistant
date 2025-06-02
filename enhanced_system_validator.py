import os
import sqlite3
import json
from datetime import datetime
import sys

class SystemValidator:
    """
    A class to validate the enhanced job hunt ecosystem workflow.
    """
    
    def __init__(self, base_dir='/home/ubuntu/job_hunt_ecosystem'):
        """
        Initialize the system validator.
        
        Args:
            base_dir: Base directory of the job hunt ecosystem
        """
        self.base_dir = base_dir
        self.db_path = os.path.join(base_dir, 'job_hunt.db')
        self.config_dir = os.path.join(base_dir, 'config')
        self.validation_results = {
            "status": "pass",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "components": {},
            "issues": []
        }
    
    def connect_db(self):
        """Connect to the SQLite database and return connection and cursor."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        return conn, cursor
    
    def validate_system(self):
        """
        Validate the entire job hunt ecosystem.
        
        Returns:
            Dictionary containing validation results
        """
        # Validate database
        self.validate_database()
        
        # Validate file structure
        self.validate_file_structure()
        
        # Validate configuration
        self.validate_configuration()
        
        # Validate modules
        self.validate_modules()
        
        # Validate enhancements
        self.validate_enhancements()
        
        # Determine overall status
        if self.validation_results["issues"]:
            self.validation_results["status"] = "fail"
        
        # Save validation results
        results_path = os.path.join(self.base_dir, 'validation_results.json')
        with open(results_path, 'w') as f:
            json.dump(self.validation_results, f, indent=4)
        
        return self.validation_results
    
    def validate_database(self):
        """Validate the database structure and sample data."""
        print("Validating database...")
        
        component_results = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        try:
            # Connect to database
            conn, cursor = self.connect_db()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'personal_info', 'job_preferences', 'target_roles', 'target_industries',
                'preferred_locations', 'work_experience', 'work_technologies', 
                'work_achievements', 'education', 'skills', 'certifications', 'projects',
                'project_technologies', 'project_highlights', 'professional_anecdotes',
                'anecdote_skills', 'reference_contacts', 'job_postings', 'job_applications',
                'application_tracking'
            ]
            
            component_results["details"]["tables"] = {
                "found": len(tables),
                "expected": len(expected_tables),
                "missing": [table for table in expected_tables if table not in tables]
            }
            
            if component_results["details"]["tables"]["missing"]:
                component_results["status"] = "fail"
                component_results["issues"].append(f"Missing tables: {', '.join(component_results['details']['tables']['missing'])}")
            
            # Check sample data
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                if table not in component_results["details"]:
                    component_results["details"][table] = {}
                component_results["details"][table]["record_count"] = count
                
                if count == 0 and table in ['personal_info', 'job_postings']:
                    component_results["status"] = "fail"
                    component_results["issues"].append(f"No records found in essential table: {table}")
            
            conn.close()
            
        except Exception as e:
            component_results["status"] = "fail"
            component_results["issues"].append(f"Database validation error: {str(e)}")
        
        self.validation_results["components"]["database"] = component_results
        
        if component_results["status"] == "fail":
            self.validation_results["issues"].extend(component_results["issues"])
        
        print(f"Database validation: {component_results['status']}")
    
    def validate_file_structure(self):
        """Validate the file structure and required directories."""
        print("Validating file structure...")
        
        component_results = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        # Check required directories
        required_dirs = [
            os.path.join(self.base_dir, 'resumes'),
            os.path.join(self.base_dir, 'cover_letters'),
            os.path.join(self.base_dir, 'templates'),
            os.path.join(self.base_dir, 'job_descriptions'),
            os.path.join(self.base_dir, 'config'),
            os.path.join(self.base_dir, 'logs')
        ]
        
        missing_dirs = []
        for directory in required_dirs:
            if not os.path.exists(directory):
                missing_dirs.append(directory)
        
        component_results["details"]["directories"] = {
            "required": len(required_dirs),
            "missing": missing_dirs
        }
        
        if missing_dirs:
            component_results["status"] = "fail"
            component_results["issues"].append(f"Missing directories: {', '.join(missing_dirs)}")
        
        # Check required files
        required_files = [
            os.path.join(self.base_dir, 'job_hunt.db'),
            os.path.join(self.base_dir, 'todo.md'),
            os.path.join(self.base_dir, 'job_scraper.py'),
            os.path.join(self.base_dir, 'document_generator.py'),
            os.path.join(self.base_dir, 'application_automation.py'),
            os.path.join(self.base_dir, 'company_website_scraper.py'),
            os.path.join(self.base_dir, 'linkedin_data_enhancer.py'),
            os.path.join(self.base_dir, 'template_selector.py')
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        component_results["details"]["files"] = {
            "required": len(required_files),
            "missing": missing_files
        }
        
        if missing_files:
            component_results["status"] = "fail"
            component_results["issues"].append(f"Missing files: {', '.join(missing_files)}")
        
        # Check configuration files
        config_files = [
            os.path.join(self.config_dir, 'job_boards.json'),
            os.path.join(self.config_dir, 'resume_config.json'),
            os.path.join(self.config_dir, 'cover_letter_config.json')
        ]
        
        missing_configs = []
        for config in config_files:
            if not os.path.exists(config):
                missing_configs.append(config)
        
        component_results["details"]["config_files"] = {
            "required": len(config_files),
            "missing": missing_configs
        }
        
        if missing_configs:
            component_results["status"] = "fail"
            component_results["issues"].append(f"Missing configuration files: {', '.join(missing_configs)}")
        
        self.validation_results["components"]["file_structure"] = component_results
        
        if component_results["status"] == "fail":
            self.validation_results["issues"].extend(component_results["issues"])
        
        print(f"File structure validation: {component_results['status']}")
    
    def validate_configuration(self):
        """Validate configuration files."""
        print("Validating configuration...")
        
        component_results = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        config_files = {
            "job_boards": os.path.join(self.config_dir, 'job_boards.json'),
            "resume": os.path.join(self.config_dir, 'resume_config.json'),
            "cover_letter": os.path.join(self.config_dir, 'cover_letter_config.json')
        }
        
        for config_name, config_path in config_files.items():
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                    
                    component_results["details"][config_name] = {
                        "valid_json": True,
                        "keys": list(config_data.keys())
                    }
                    
                    # Validate job_boards.json specifically
                    if config_name == "job_boards":
                        # Check for target_companies
                        if "target_companies" in config_data:
                            component_results["details"]["job_boards"]["has_target_companies"] = True
                            component_results["details"]["job_boards"]["target_companies_count"] = len(config_data["target_companies"])
                        else:
                            component_results["details"]["job_boards"]["has_target_companies"] = False
                            component_results["status"] = "fail"
                            component_results["issues"].append("job_boards.json is missing target_companies configuration")
                        
                        # Check for expanded roles
                        if "search_terms" in config_data:
                            has_solution_engineer = any("solution" in term.lower() for term in config_data["search_terms"])
                            component_results["details"]["job_boards"]["has_expanded_roles"] = has_solution_engineer
                            
                            if not has_solution_engineer:
                                component_results["status"] = "fail"
                                component_results["issues"].append("job_boards.json is missing expanded roles like Solution Engineer")
                        
                        # Check for full-time job focus
                        if "job_types" in config_data:
                            has_full_time = "Full-time" in config_data["job_types"]
                            component_results["details"]["job_boards"]["has_full_time_focus"] = has_full_time
                            
                            if not has_full_time:
                                component_results["status"] = "fail"
                                component_results["issues"].append("job_boards.json is missing Full-time job type focus")
                    
                except json.JSONDecodeError:
                    component_results["status"] = "fail"
                    component_results["issues"].append(f"Invalid JSON in {config_name} configuration")
                    component_results["details"][config_name] = {
                        "valid_json": False
                    }
            else:
                component_results["details"][config_name] = {
                    "exists": False
                }
                component_results["status"] = "fail"
                component_results["issues"].append(f"Missing configuration file: {config_path}")
        
        self.validation_results["components"]["configuration"] = component_results
        
        if component_results["status"] == "fail":
            self.validation_results["issues"].extend(component_results["issues"])
        
        print(f"Configuration validation: {component_results['status']}")
    
    def validate_modules(self):
        """Validate core modules."""
        print("Validating modules...")
        
        component_results = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        # Check if modules exist and have required functions
        modules = {
            "job_scraper": {
                "path": os.path.join(self.base_dir, 'job_scraper.py'),
                "required_functions": ["scrape_company_website"]
            },
            "document_generator": {
                "path": os.path.join(self.base_dir, 'document_generator.py'),
                "required_functions": []
            },
            "application_automation": {
                "path": os.path.join(self.base_dir, 'application_automation.py'),
                "required_functions": []
            },
            "company_website_scraper": {
                "path": os.path.join(self.base_dir, 'company_website_scraper.py'),
                "required_functions": ["scrape_company"]
            },
            "linkedin_data_enhancer": {
                "path": os.path.join(self.base_dir, 'linkedin_data_enhancer.py'),
                "required_functions": ["enhance_user_profile"]
            },
            "template_selector": {
                "path": os.path.join(self.base_dir, 'template_selector.py'),
                "required_functions": ["select_best_template", "analyze_job_posting"]
            }
        }
        
        for module_name, module_info in modules.items():
            module_path = module_info["path"]
            
            if os.path.exists(module_path):
                component_results["details"][module_name] = {
                    "exists": True,
                    "size": os.path.getsize(module_path)
                }
                
                # Check for required functions
                with open(module_path, 'r') as f:
                    content = f.read()
                
                missing_functions = []
                for function in module_info["required_functions"]:
                    if f"def {function}" not in content:
                        missing_functions.append(function)
                
                if missing_functions:
                    component_results["status"] = "fail"
                    component_results["issues"].append(f"Module {module_name} is missing required functions: {', '.join(missing_functions)}")
                    component_results["details"][module_name]["missing_functions"] = missing_functions
            else:
                component_results["status"] = "fail"
                component_results["issues"].append(f"Missing module: {module_path}")
                component_results["details"][module_name] = {
                    "exists": False
                }
        
        self.validation_results["components"]["modules"] = component_results
        
        if component_results["status"] == "fail":
            self.validation_results["issues"].extend(component_results["issues"])
        
        print(f"Modules validation: {component_results['status']}")
    
    def validate_enhancements(self):
        """Validate the new enhancements."""
        print("Validating enhancements...")
        
        component_results = {
            "status": "pass",
            "details": {},
            "issues": []
        }
        
        # Validate company website scraping
        company_scraper_path = os.path.join(self.base_dir, 'company_website_scraper.py')
        job_scraper_path = os.path.join(self.base_dir, 'job_scraper.py')
        
        if os.path.exists(company_scraper_path) and os.path.exists(job_scraper_path):
            # Check if company_website_scraper is imported in job_scraper
            with open(job_scraper_path, 'r') as f:
                job_scraper_content = f.read()
            
            if "from company_website_scraper import" in job_scraper_content and "def scrape_company_website" in job_scraper_content:
                component_results["details"]["company_website_scraping"] = {
                    "integrated": True
                }
            else:
                component_results["status"] = "fail"
                component_results["issues"].append("Company website scraping is not properly integrated in job_scraper.py")
                component_results["details"]["company_website_scraping"] = {
                    "integrated": False
                }
        else:
            component_results["status"] = "fail"
            component_results["issues"].append("Missing company website scraping module or job scraper")
            component_results["details"]["company_website_scraping"] = {
                "integrated": False
            }
        
        # Validate LinkedIn data enhancement
        linkedin_enhancer_path = os.path.join(self.base_dir, 'linkedin_data_enhancer.py')
        
        if os.path.exists(linkedin_enhancer_path):
            with open(linkedin_enhancer_path, 'r') as f:
                linkedin_enhancer_content = f.read()
            
            if "def enhance_user_profile" in linkedin_enhancer_content:
                component_results["details"]["linkedin_data_enhancement"] = {
                    "implemented": True
                }
            else:
                component_results["status"] = "fail"
                component_results["issues"].append("LinkedIn data enhancement is not properly implemented")
                component_results["details"]["linkedin_data_enhancement"] = {
                    "implemented": False
                }
        else:
            component_results["status"] = "fail"
            component_results["issues"].append("Missing LinkedIn data enhancer module")
            component_results["details"]["linkedin_data_enhancement"] = {
                "implemented": False
            }
        
        # Validate template selection
        template_selector_path = os.path.join(self.base_dir, 'template_selector.py')
        
        if os.path.exists(template_selector_path):
            with open(template_selector_path, 'r') as f:
                template_selector_content = f.read()
            
            if "def select_best_template" in template_selector_content and "def analyze_job_posting" in template_selector_content:
                component_results["details"]["template_selection"] = {
                    "implemented": True
                }
            else:
                component_results["status"] = "fail"
                component_results["issues"].append("Template selection is not properly implemented")
                component_results["details"]["template_selection"] = {
                    "implemented": False
                }
        else:
            component_results["status"] = "fail"
            component_results["issues"].append("Missing template selector module")
            component_results["details"]["template_selection"] = {
                "implemented": False
            }
        
        # Validate job boards configuration for full-time focus
        job_boards_path = os.path.join(self.config_dir, 'job_boards.json')
        
        if os.path.exists(job_boards_path):
            try:
                with open(job_boards_path, 'r') as f:
                    job_boards_config = json.load(f)
                
                # Check for full-time job focus
                if "job_types" in job_boards_config and "Full-time" in job_boards_config["job_types"]:
                    component_results["details"]["full_time_focus"] = {
                        "implemented": True
                    }
                else:
                    component_results["status"] = "fail"
                    component_results["issues"].append("Full-time job focus is not properly configured")
                    component_results["details"]["full_time_focus"] = {
                        "implemented": False
                    }
                
                # Check for expanded roles
                if "search_terms" in job_boards_config:
                    has_solution_engineer = any("solution" in term.lower() for term in job_boards_config["search_terms"])
                    
                    if has_solution_engineer:
                        component_results["details"]["expanded_roles"] = {
                            "implemented": True
                        }
                    else:
                        component_results["status"] = "fail"
                        component_results["issues"].append("Expanded roles like Solution Engineer are not properly configured")
                        component_results["details"]["expanded_roles"] = {
                            "implemented": False
                        }
                else:
                    component_results["status"] = "fail"
                    component_results["issues"].append("Search terms are not configured in job_boards.json")
                    component_results["details"]["expanded_roles"] = {
                        "implemented": False
                    }
            except Exception as e:
                component_results["status"] = "fail"
                component_results["issues"].append(f"Error validating job boards configuration: {str(e)}")
        else:
            component_results["status"] = "fail"
            component_results["issues"].append("Missing job boards configuration")
            component_results["details"]["full_time_focus"] = {
                "implemented": False
            }
            component_results["details"]["expanded_roles"] = {
                "implemented": False
            }
        
        self.validation_results["components"]["enhancements"] = component_results
        
        if component_results["status"] == "fail":
            self.validation_results["issues"].extend(component_results["issues"])
        
        print(f"Enhancements validation: {component_results['status']}")
    
    def generate_report(self):
        """
        Generate a comprehensive validation report.
        
        Returns:
            String containing the report
        """
        report = f"""
# Job Hunt Ecosystem - Enhanced System Validation Report

## System Overview

The Job Hunt Ecosystem has been enhanced with the following features:

1. **Direct Company Website Targeting**: The system now directly targets company career pages for job applications
2. **Full-Time Job Focus**: The system now focuses exclusively on full-time job opportunities
3. **Expanded Role Targeting**: The system now includes additional roles like Solution Engineering
4. **Enhanced LinkedIn Data Utilization**: The system now makes better use of LinkedIn profile data
5. **Intelligent Template Selection**: The system now intelligently selects the best resume and cover letter templates for each job

## Validation Results

Overall Status: **{self.validation_results["status"]}**

### Database Validation
Status: **{self.validation_results["components"]["database"]["status"]}**
{f"Issues: {', '.join(self.validation_results['components']['database']['issues'])}" if self.validation_results["components"]["database"]["issues"] else "No issues found."}

### File Structure Validation
Status: **{self.validation_results["components"]["file_structure"]["status"]}**
{f"Issues: {', '.join(self.validation_results['components']['file_structure']['issues'])}" if self.validation_results["components"]["file_structure"]["issues"] else "No issues found."}

### Configuration Validation
Status: **{self.validation_results["components"]["configuration"]["status"]}**
{f"Issues: {', '.join(self.validation_results['components']['configuration']['issues'])}" if self.validation_results["components"]["configuration"]["issues"] else "No issues found."}

### Modules Validation
Status: **{self.validation_results["components"]["modules"]["status"]}**
{f"Issues: {', '.join(self.validation_results['components']['modules']['issues'])}" if self.validation_results["components"]["modules"]["issues"] else "No issues found."}

### Enhancements Validation
Status: **{self.validation_results["components"]["enhancements"]["status"]}**
{f"Issues: {', '.join(self.validation_results['components']['enhancements']['issues'])}" if self.validation_results["components"]["enhancements"]["issues"] else "No issues found."}

## Enhanced Features

### 1. Direct Company Website Targeting

The system now directly targets company career pages for job applications, providing several benefits:

- **More Comprehensive Job Search**: By directly scraping company career pages, the system can find jobs that may not be listed on job boards
- **Better Application Success Rate**: Applying directly through company websites often has a higher success rate than through job boards
- **Customized Scraping Logic**: The system uses specialized scrapers for different career page platforms (Workday, Greenhouse, Lever, etc.)
- **Configurable Target Companies**: Users can specify which companies to target in the configuration

### 2. Full-Time Job Focus

The system now focuses exclusively on full-time job opportunities:

- **Filtering Logic**: Jobs are filtered based on job type, with a focus on full-time positions
- **Configuration Options**: The job_boards.json configuration specifies "Full-time" as the target job type
- **Scraping Optimization**: The scraping logic prioritizes and identifies full-time positions

### 3. Expanded Role Targeting

The system now includes additional roles like Solution Engineering:

- **Expanded Search Terms**: The job_boards.json configuration includes roles like "Solution Engineer", "Solutions Engineer", "Technical Solutions Engineer", etc.
- **Broader Opportunity Scope**: This expansion allows the system to find more relevant opportunities that match the user's skills and experience

### 4. Enhanced LinkedIn Data Utilization

The system now makes better use of LinkedIn profile data:

- **Comprehensive Data Extraction**: The LinkedIn data enhancer extracts detailed information from the user's LinkedIn profile
- **Intelligent Data Mapping**: The system maps LinkedIn data to the appropriate database fields
- **Skills Extraction**: The system extracts skills from LinkedIn work experience and summary
- **Achievement Identification**: The system identifies achievements from LinkedIn work descriptions

### 5. Intelligent Template Selection

The system now intelligently selects the best resume and cover letter templates for each job:

- **Job Analysis**: The template selector analyzes job postings to extract key information
- **Template Matching**: Templates are matched based on industry, role, and job description
- **Customization Factors**: The system considers formality level, company type, and required skills
- **Optimization for Success**: The selected templates are optimized for the specific job application

## Next Steps

1. **User Interface Development**: Create a web-based interface for easier management
2. **Enhanced Automation**: Implement more sophisticated browser automation for application submission
3. **AI Integration**: Add machine learning for better job matching and document optimization
4. **Notification System**: Implement email or mobile notifications for application updates
5. **Interview Preparation**: Add features for interview scheduling and preparation

## Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Save report to file
        report_path = os.path.join(self.base_dir, 'enhanced_system_report.md')
        with open(report_path, 'w') as f:
            f.write(report)
        
        return report

# Run validation if executed directly
if __name__ == "__main__":
    validator = SystemValidator()
    results = validator.validate_system()
    
    print(f"\nValidation status: {results['status']}")
    
    if results["issues"]:
        print("\nIssues found:")
        for issue in results["issues"]:
            print(f"- {issue}")
    else:
        print("\nNo issues found.")
    
    report = validator.generate_report()
    print(f"\nReport generated: {os.path.join(validator.base_dir, 'enhanced_system_report.md')}")
