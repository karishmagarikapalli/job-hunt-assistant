import json
import os
import sqlite3
from datetime import datetime

# Define the database structure for the job hunt ecosystem

def create_database_structure():
    """Create the SQLite database structure for the job hunt ecosystem"""
    
    # Connect to SQLite database (will create if it doesn't exist)
    conn = sqlite3.connect('/home/ubuntu/job_hunt_ecosystem/job_hunt.db')
    cursor = conn.cursor()
    
    # Create tables for user information
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS personal_info (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        phone TEXT,
        street_address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        country TEXT,
        linkedin_url TEXT,
        portfolio_url TEXT,
        github_url TEXT,
        visa_status TEXT,
        requires_sponsorship BOOLEAN,
        authorized_to_work BOOLEAN,
        visa_expiration_date TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')
    
    # Create table for job preferences
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_preferences (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        remote_preference TEXT,
        min_salary REAL,
        preferred_salary REAL,
        willing_to_relocate BOOLEAN,
        start_date_availability TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES personal_info(id)
    )
    ''')
    
    # Create table for target roles
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS target_roles (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        role_name TEXT,
        FOREIGN KEY (user_id) REFERENCES personal_info(id)
    )
    ''')
    
    # Create table for target industries
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS target_industries (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        industry_name TEXT,
        FOREIGN KEY (user_id) REFERENCES personal_info(id)
    )
    ''')
    
    # Create table for preferred locations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS preferred_locations (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        location TEXT,
        FOREIGN KEY (user_id) REFERENCES personal_info(id)
    )
    ''')
    
    # Create table for work experience
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS work_experience (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        company TEXT,
        title TEXT,
        location TEXT,
        start_date TEXT,
        end_date TEXT,
        description TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES personal_info(id)
    )
    ''')
    
    # Create table for work experience technologies
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS work_technologies (
        id INTEGER PRIMARY KEY,
        experience_id INTEGER,
        technology TEXT,
        FOREIGN KEY (experience_id) REFERENCES work_experience(id)
    )
    ''')
    
    # Create table for work achievements
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS work_achievements (
        id INTEGER PRIMARY KEY,
        experience_id INTEGER,
        achievement TEXT,
        FOREIGN KEY (experience_id) REFERENCES work_experience(id)
    )
    ''')
    
    # Create table for education
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS education (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        institution TEXT,
        degree TEXT,
        field_of_study TEXT,
        location TEXT,
        start_date TEXT,
        end_date TEXT,
        gpa TEXT,
        description TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES personal_info(id)
    )
    ''')
    
    # Create table for skills
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        skill_name TEXT,
        skill_type TEXT,  -- 'technical', 'soft', 'language'
        proficiency_level TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES personal_info(id)
    )
    ''')
    
    # Create table for certifications
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS certifications (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT,
        issuing_organization TEXT,
        issue_date TEXT,
        expiration_date TEXT,
        credential_id TEXT,
        credential_url TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES personal_info(id)
    )
    ''')
    
    # Create table for projects
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT,
        description TEXT,
        url TEXT,
        start_date TEXT,
        end_date TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES personal_info(id)
    )
    ''')
    
    # Create table for project technologies
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_technologies (
        id INTEGER PRIMARY KEY,
        project_id INTEGER,
        technology TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
    ''')
    
    # Create table for project highlights
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_highlights (
        id INTEGER PRIMARY KEY,
        project_id INTEGER,
        highlight TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
    ''')
    
    # Create table for professional anecdotes (STAR stories)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS professional_anecdotes (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title TEXT,
        situation TEXT,
        task TEXT,
        action TEXT,
        result TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES personal_info(id)
    )
    ''')
    
    # Create table for anecdote skills demonstrated
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS anecdote_skills (
        id INTEGER PRIMARY KEY,
        anecdote_id INTEGER,
        skill TEXT,
        FOREIGN KEY (anecdote_id) REFERENCES professional_anecdotes(id)
    )
    ''')
    
    # Create table for reference contacts (renamed from references to avoid SQL keyword conflict)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reference_contacts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT,
        relationship TEXT,
        company TEXT,
        email TEXT,
        phone TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES personal_info(id)
    )
    ''')
    
    # Create table for job postings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_postings (
        id INTEGER PRIMARY KEY,
        title TEXT,
        company TEXT,
        location TEXT,
        job_type TEXT,
        description TEXT,
        requirements TEXT,
        salary_range TEXT,
        application_url TEXT,
        source_website TEXT,
        date_posted TEXT,
        date_scraped TIMESTAMP,
        status TEXT DEFAULT 'new',  -- 'new', 'applied', 'rejected', 'interview', 'offer', 'declined'
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')
    
    # Create table for job applications
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_applications (
        id INTEGER PRIMARY KEY,
        job_id INTEGER,
        resume_path TEXT,
        cover_letter_path TEXT,
        application_date TIMESTAMP,
        status TEXT DEFAULT 'submitted',  -- 'submitted', 'rejected', 'interview', 'offer', 'accepted', 'declined'
        notes TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES job_postings(id)
    )
    ''')
    
    # Create table for application tracking
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS application_tracking (
        id INTEGER PRIMARY KEY,
        application_id INTEGER,
        status TEXT,
        date TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (application_id) REFERENCES job_applications(id)
    )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database structure created successfully.")

def create_file_structure():
    """Create the file structure for storing resumes, cover letters, and other documents"""
    
    # Create directories for various file types
    directories = [
        '/home/ubuntu/job_hunt_ecosystem/resumes',
        '/home/ubuntu/job_hunt_ecosystem/cover_letters',
        '/home/ubuntu/job_hunt_ecosystem/templates',
        '/home/ubuntu/job_hunt_ecosystem/job_descriptions',
        '/home/ubuntu/job_hunt_ecosystem/config'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
    
    # Create configuration file for job boards to scrape
    job_boards_config = {
        "job_boards": [
            {
                "name": "LinkedIn",
                "url": "https://www.linkedin.com/jobs/",
                "enabled": True
            },
            {
                "name": "Indeed",
                "url": "https://www.indeed.com/",
                "enabled": True
            },
            {
                "name": "Glassdoor",
                "url": "https://www.glassdoor.com/",
                "enabled": True
            },
            {
                "name": "Monster",
                "url": "https://www.monster.com/",
                "enabled": False
            },
            {
                "name": "ZipRecruiter",
                "url": "https://www.ziprecruiter.com/",
                "enabled": False
            }
        ],
        "search_terms": [
            "Software Developer",
            "Full Stack Developer",
            "Software Engineer",
            "Senior Software Developer",
            "Senior Full Stack Developer"
        ],
        "locations": [],
        "remote_only": False,
        "h1b_sponsorship_keywords": [
            "h1b",
            "h-1b",
            "visa sponsorship",
            "sponsorship available",
            "will sponsor",
            "visa"
        ],
        "exclude_keywords": [
            "clearance",
            "security clearance",
            "US citizen",
            "citizenship required"
        ],
        "scrape_frequency": "daily"
    }
    
    # Save job boards configuration
    with open('/home/ubuntu/job_hunt_ecosystem/config/job_boards.json', 'w') as f:
        json.dump(job_boards_config, f, indent=4)
    
    # Create resume template configuration
    resume_config = {
        "templates": [
            {
                "name": "Modern",
                "file": "modern_template.html",
                "description": "Clean, modern design with subtle styling"
            },
            {
                "name": "Professional",
                "file": "professional_template.html",
                "description": "Traditional professional layout"
            },
            {
                "name": "Creative",
                "file": "creative_template.html",
                "description": "Bold design for creative roles"
            },
            {
                "name": "Technical",
                "file": "technical_template.html",
                "description": "Focused on technical skills and projects"
            }
        ],
        "default_template": "Professional",
        "sections": [
            "contact",
            "summary",
            "experience",
            "skills",
            "education",
            "projects",
            "certifications"
        ],
        "optional_sections": [
            "publications",
            "awards",
            "languages",
            "interests"
        ]
    }
    
    # Save resume configuration
    with open('/home/ubuntu/job_hunt_ecosystem/config/resume_config.json', 'w') as f:
        json.dump(resume_config, f, indent=4)
    
    # Create cover letter template configuration
    cover_letter_config = {
        "templates": [
            {
                "name": "Standard",
                "file": "standard_cover_letter.html",
                "description": "Professional standard cover letter"
            },
            {
                "name": "Modern",
                "file": "modern_cover_letter.html",
                "description": "Contemporary design with clean layout"
            },
            {
                "name": "Technical",
                "file": "technical_cover_letter.html",
                "description": "Emphasizes technical skills and achievements"
            }
        ],
        "default_template": "Standard",
        "sections": [
            "header",
            "greeting",
            "introduction",
            "body",
            "skills_match",
            "company_connection",
            "call_to_action",
            "closing"
        ],
        "anecdotes_per_letter": 1,
        "max_length_words": 400
    }
    
    # Save cover letter configuration
    with open('/home/ubuntu/job_hunt_ecosystem/config/cover_letter_config.json', 'w') as f:
        json.dump(cover_letter_config, f, indent=4)
    
    print("File structure and configuration files created successfully.")

if __name__ == "__main__":
    create_database_structure()
    create_file_structure()
    print("Data storage structure design completed.")
