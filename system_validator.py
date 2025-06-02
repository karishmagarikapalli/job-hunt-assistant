import os
import sqlite3
import json
from datetime import datetime

def validate_system_workflow():
    """
    Validate the entire job hunt ecosystem workflow by checking all components
    and their integration.
    """
    validation_results = {
        "database": validate_database(),
        "file_structure": validate_file_structure(),
        "configuration": validate_configuration(),
        "modules": {
            "job_scraper": validate_job_scraper(),
            "document_generator": validate_document_generator(),
            "application_automation": validate_application_automation()
        },
        "integration": validate_integration(),
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Aggregate status and issues
    all_statuses = [
        validation_results["database"]["status"],
        validation_results["file_structure"]["status"],
        validation_results["configuration"]["status"],
        validation_results["modules"]["job_scraper"]["status"],
        validation_results["modules"]["document_generator"]["status"],
        validation_results["modules"]["application_automation"]["status"],
        validation_results["integration"]["status"]
    ]
    
    # Overall status is "pass" only if all components pass
    validation_results["status"] = "pass" if all(status == "pass" for status in all_statuses) else "fail"
    
    # Collect all issues
    validation_results["issues"] = []
    validation_results["issues"].extend(validation_results["database"]["issues"])
    validation_results["issues"].extend(validation_results["file_structure"]["issues"])
    validation_results["issues"].extend(validation_results["configuration"]["issues"])
    validation_results["issues"].extend(validation_results["modules"]["job_scraper"]["issues"])
    validation_results["issues"].extend(validation_results["modules"]["document_generator"]["issues"])
    validation_results["issues"].extend(validation_results["modules"]["application_automation"]["issues"])
    validation_results["issues"].extend(validation_results["integration"]["issues"])
    
    # Save validation results
    with open('/home/ubuntu/job_hunt_ecosystem/validation_results.json', 'w') as f:
        json.dump(validation_results, f, indent=4)
    
    return validation_results

def validate_database():
    """Validate the database structure and sample data."""
    results = {
        "status": "pass",
        "details": {},
        "issues": []
    }
    
    try:
        # Connect to database
        conn = sqlite3.connect('/home/ubuntu/job_hunt_ecosystem/job_hunt.db')
        cursor = conn.cursor()
        
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
        
        results["details"]["tables"] = {
            "found": len(tables),
            "expected": len(expected_tables),
            "missing": [table for table in expected_tables if table not in tables]
        }
        
        if results["details"]["tables"]["missing"]:
            results["status"] = "fail"
            results["issues"].append(f"Missing tables: {', '.join(results['details']['tables']['missing'])}")
        
        # Check sample data
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            if table not in results["details"]:
                results["details"][table] = {}
            results["details"][table]["record_count"] = count
            
            if count == 0 and table in ['personal_info', 'job_postings']:
                results["status"] = "fail"
                results["issues"].append(f"No records found in essential table: {table}")
        
        conn.close()
        
    except Exception as e:
        results["status"] = "fail"
        results["issues"].append(f"Database validation error: {str(e)}")
    
    return results

def validate_file_structure():
    """Validate the file structure and required directories."""
    results = {
        "status": "pass",
        "details": {},
        "issues": []
    }
    
    # Check required directories
    required_dirs = [
        '/home/ubuntu/job_hunt_ecosystem/resumes',
        '/home/ubuntu/job_hunt_ecosystem/cover_letters',
        '/home/ubuntu/job_hunt_ecosystem/templates',
        '/home/ubuntu/job_hunt_ecosystem/job_descriptions',
        '/home/ubuntu/job_hunt_ecosystem/config',
        '/home/ubuntu/job_hunt_ecosystem/logs'
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    results["details"]["directories"] = {
        "required": len(required_dirs),
        "missing": missing_dirs
    }
    
    if missing_dirs:
        results["status"] = "fail"
        results["issues"].append(f"Missing directories: {', '.join(missing_dirs)}")
    
    # Check required files
    required_files = [
        '/home/ubuntu/job_hunt_ecosystem/job_hunt.db',
        '/home/ubuntu/job_hunt_ecosystem/todo.md',
        '/home/ubuntu/job_hunt_ecosystem/job_scraper.py',
        '/home/ubuntu/job_hunt_ecosystem/document_generator.py',
        '/home/ubuntu/job_hunt_ecosystem/application_automation.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    results["details"]["files"] = {
        "required": len(required_files),
        "missing": missing_files
    }
    
    if missing_files:
        results["status"] = "fail"
        results["issues"].append(f"Missing files: {', '.join(missing_files)}")
    
    # Check configuration files
    config_files = [
        '/home/ubuntu/job_hunt_ecosystem/config/job_boards.json',
        '/home/ubuntu/job_hunt_ecosystem/config/resume_config.json',
        '/home/ubuntu/job_hunt_ecosystem/config/cover_letter_config.json'
    ]
    
    missing_configs = []
    for config in config_files:
        if not os.path.exists(config):
            missing_configs.append(config)
    
    results["details"]["config_files"] = {
        "required": len(config_files),
        "missing": missing_configs
    }
    
    if missing_configs:
        results["status"] = "fail"
        results["issues"].append(f"Missing configuration files: {', '.join(missing_configs)}")
    
    return results

def validate_configuration():
    """Validate configuration files."""
    results = {
        "status": "pass",
        "details": {},
        "issues": []
    }
    
    config_files = {
        "job_boards": '/home/ubuntu/job_hunt_ecosystem/config/job_boards.json',
        "resume": '/home/ubuntu/job_hunt_ecosystem/config/resume_config.json',
        "cover_letter": '/home/ubuntu/job_hunt_ecosystem/config/cover_letter_config.json'
    }
    
    for config_name, config_path in config_files.items():
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                results["details"][config_name] = {
                    "valid_json": True,
                    "keys": list(config_data.keys())
                }
            except json.JSONDecodeError:
                results["status"] = "fail"
                results["issues"].append(f"Invalid JSON in {config_name} configuration")
                results["details"][config_name] = {
                    "valid_json": False
                }
        else:
            results["details"][config_name] = {
                "exists": False
            }
    
    return results

def validate_job_scraper():
    """Validate the job scraper module."""
    results = {
        "status": "pass",
        "details": {},
        "issues": []
    }
    
    # Check if the module exists
    if not os.path.exists('/home/ubuntu/job_hunt_ecosystem/job_scraper.py'):
        results["status"] = "fail"
        results["issues"].append("Job scraper module not found")
        return results
    
    # Check if sample job exists in database
    try:
        conn = sqlite3.connect('/home/ubuntu/job_hunt_ecosystem/job_hunt.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM job_postings")
        job_count = cursor.fetchone()[0]
        
        results["details"]["job_count"] = job_count
        
        if job_count == 0:
            results["status"] = "fail"
            results["issues"].append("No job postings found in database")
        
        conn.close()
        
    except Exception as e:
        results["status"] = "fail"
        results["issues"].append(f"Error checking job postings: {str(e)}")
    
    return results

def validate_document_generator():
    """Validate the document generator module."""
    results = {
        "status": "pass",
        "details": {},
        "issues": []
    }
    
    # Check if the module exists
    if not os.path.exists('/home/ubuntu/job_hunt_ecosystem/document_generator.py'):
        results["status"] = "fail"
        results["issues"].append("Document generator module not found")
        return results
    
    # Check if templates exist
    templates_dir = '/home/ubuntu/job_hunt_ecosystem/templates'
    if os.path.exists(templates_dir):
        templates = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
        results["details"]["templates"] = templates
        
        if not templates:
            results["status"] = "fail"
            results["issues"].append("No HTML templates found")
    else:
        results["status"] = "fail"
        results["issues"].append("Templates directory not found")
    
    # Check if generated documents exist
    resume_dir = '/home/ubuntu/job_hunt_ecosystem/resumes'
    cover_letter_dir = '/home/ubuntu/job_hunt_ecosystem/cover_letters'
    
    if os.path.exists(resume_dir):
        resumes = [f for f in os.listdir(resume_dir) if f.endswith('.pdf')]
        results["details"]["resumes"] = resumes
        
        if not resumes:
            results["status"] = "fail"
            results["issues"].append("No generated resumes found")
    else:
        results["status"] = "fail"
        results["issues"].append("Resumes directory not found")
    
    if os.path.exists(cover_letter_dir):
        cover_letters = [f for f in os.listdir(cover_letter_dir) if f.endswith('.pdf')]
        results["details"]["cover_letters"] = cover_letters
        
        if not cover_letters:
            results["status"] = "fail"
            results["issues"].append("No generated cover letters found")
    else:
        results["status"] = "fail"
        results["issues"].append("Cover letters directory not found")
    
    return results

def validate_application_automation():
    """Validate the application automation module."""
    results = {
        "status": "pass",
        "details": {},
        "issues": []
    }
    
    # Check if the module exists
    if not os.path.exists('/home/ubuntu/job_hunt_ecosystem/application_automation.py'):
        results["status"] = "fail"
        results["issues"].append("Application automation module not found")
        return results
    
    # Check if logs directory exists
    logs_dir = '/home/ubuntu/job_hunt_ecosystem/logs'
    if not os.path.exists(logs_dir):
        results["status"] = "fail"
        results["issues"].append("Logs directory not found")
    
    # Check if application tracking table exists
    try:
        conn = sqlite3.connect('/home/ubuntu/job_hunt_ecosystem/job_hunt.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='application_tracking';")
        if not cursor.fetchone():
            results["status"] = "fail"
            results["issues"].append("Application tracking table not found in database")
        
        conn.close()
        
    except Exception as e:
        results["status"] = "fail"
        results["issues"].append(f"Error checking application tracking: {str(e)}")
    
    return results

def validate_integration():
    """Validate the integration between modules."""
    results = {
        "status": "pass",
        "details": {},
        "issues": []
    }
    
    # Check if all required modules exist
    required_modules = [
        '/home/ubuntu/job_hunt_ecosystem/job_scraper.py',
        '/home/ubuntu/job_hunt_ecosystem/document_generator.py',
        '/home/ubuntu/job_hunt_ecosystem/application_automation.py'
    ]
    
    missing_modules = []
    for module in required_modules:
        if not os.path.exists(module):
            missing_modules.append(module)
    
    if missing_modules:
        results["status"] = "fail"
        results["issues"].append(f"Missing modules: {', '.join(missing_modules)}")
        return results
    
    # Check database for integration points
    try:
        conn = sqlite3.connect('/home/ubuntu/job_hunt_ecosystem/job_hunt.db')
        cursor = conn.cursor()
        
        # Check if we have user data
        cursor.execute("SELECT COUNT(*) FROM personal_info")
        user_count = cursor.fetchone()[0]
        
        # Check if we have job postings
        cursor.execute("SELECT COUNT(*) FROM job_postings")
        job_count = cursor.fetchone()[0]
        
        # Check if we have job applications
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_applications';")
        has_applications_table = cursor.fetchone() is not None
        
        if has_applications_table:
            cursor.execute("SELECT COUNT(*) FROM job_applications")
            application_count = cursor.fetchone()[0]
        else:
            application_count = 0
        
        results["details"]["integration_points"] = {
            "user_count": user_count,
            "job_count": job_count,
            "application_count": application_count
        }
        
        if user_count == 0:
            results["status"] = "fail"
            results["issues"].append("No user data found for integration")
        
        if job_count == 0:
            results["status"] = "fail"
            results["issues"].append("No job postings found for integration")
        
        conn.close()
        
    except Exception as e:
        results["status"] = "fail"
        results["issues"].append(f"Error checking integration points: {str(e)}")
    
    return results

def generate_system_report():
    """Generate a comprehensive system report."""
    validation_results = validate_system_workflow()
    
    report = f"""
# Job Hunt Ecosystem - System Report

## System Overview

The Job Hunt Ecosystem is a comprehensive solution designed to automate the job application process. It includes modules for:

1. **User Data Management**: Stores personal details, work experience, skills, and other information
2. **Job Scraping**: Collects job postings from various sources
3. **Document Generation**: Creates tailored resumes and cover letters
4. **Application Automation**: Submits applications and tracks their status

## Validation Results

Overall Status: **{validation_results["status"] if "status" in validation_results else "Unknown"}**

### Database Validation
Status: **{validation_results["database"]["status"]}**
{f"Issues: {', '.join(validation_results['database']['issues'])}" if validation_results["database"]["issues"] else "No issues found."}

### File Structure Validation
Status: **{validation_results["file_structure"]["status"]}**
{f"Issues: {', '.join(validation_results['file_structure']['issues'])}" if validation_results["file_structure"]["issues"] else "No issues found."}

### Configuration Validation
Status: **{validation_results["configuration"]["status"]}**
{f"Issues: {', '.join(validation_results['configuration']['issues'])}" if validation_results["configuration"]["issues"] else "No issues found."}

### Module Validation

#### Job Scraper
Status: **{validation_results["modules"]["job_scraper"]["status"]}**
{f"Issues: {', '.join(validation_results['modules']['job_scraper']['issues'])}" if validation_results["modules"]["job_scraper"]["issues"] else "No issues found."}

#### Document Generator
Status: **{validation_results["modules"]["document_generator"]["status"]}**
{f"Issues: {', '.join(validation_results['modules']['document_generator']['issues'])}" if validation_results["modules"]["document_generator"]["issues"] else "No issues found."}

#### Application Automation
Status: **{validation_results["modules"]["application_automation"]["status"]}**
{f"Issues: {', '.join(validation_results['modules']['application_automation']['issues'])}" if validation_results["modules"]["application_automation"]["issues"] else "No issues found."}

### Integration Validation
Status: **{validation_results["integration"]["status"]}**
{f"Issues: {', '.join(validation_results['integration']['issues'])}" if validation_results["integration"]["issues"] else "No issues found."}

## System Components

### 1. User Data Management

The system stores comprehensive user information including:
- Personal details and contact information
- Work experience and achievements
- Education history
- Skills (technical, soft, and languages)
- Projects and their details
- Professional anecdotes for cover letters
- References

### 2. Job Scraping Module

The job scraping module can collect job postings from:
- LinkedIn
- Indeed
- Glassdoor
- Other job boards (configurable)

It filters jobs based on:
- H1-B visa sponsorship availability
- Excluded keywords
- Job titles and skills matching

### 3. Document Generation Module

The document generation module creates:
- Customized resumes tailored to specific job descriptions
- Personalized cover letters highlighting relevant skills and experiences
- Multiple template options for different styles and formats

### 4. Application Automation Module

The application automation module:
- Submits applications through various platforms (LinkedIn, Indeed, company websites)
- Tracks application status and history
- Provides statistics on application performance
- Logs all activities for review

## Usage Instructions

### Setting Up User Data

1. Update the user form template with your personal information
2. Run the data structure design script to set up the database
3. Import your LinkedIn profile data for comprehensive information

### Configuring Job Scraping

1. Edit the job boards configuration file to specify target job titles and locations
2. Set keywords for H1-B sponsorship filtering
3. Configure excluded keywords to avoid irrelevant postings

### Generating Documents

1. Use the document generator to create resumes and cover letters
2. Customize templates as needed in the templates directory
3. Review generated documents in the resumes and cover letters directories

### Automating Applications

1. Configure application settings in the application configuration file
2. Set up credentials for job platforms (LinkedIn, Indeed)
3. Enable auto-apply feature when ready
4. Monitor application status and statistics

## Next Steps and Recommendations

1. **User Interface Development**: Create a web-based interface for easier management
2. **Enhanced Automation**: Implement more sophisticated browser automation for application submission
3. **AI Integration**: Add machine learning for better job matching and document optimization
4. **Notification System**: Implement email or mobile notifications for application updates
5. **Interview Preparation**: Add features for interview scheduling and preparation

## Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # Save report to file
    with open('/home/ubuntu/job_hunt_ecosystem/system_report.md', 'w') as f:
        f.write(report)
    
    return report

if __name__ == "__main__":
    validation_results = validate_system_workflow()
    print(f"Validation status: {validation_results['status']}")
    
    if validation_results["issues"]:
        print("Issues found:")
        for issue in validation_results["issues"]:
            print(f"- {issue}")
    else:
        print("No issues found.")
    
    report = generate_system_report()
    print(f"System report generated: /home/ubuntu/job_hunt_ecosystem/system_report.md")
