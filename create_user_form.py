import json
import os

# Create a comprehensive user information form based on LinkedIn data and additional requirements

# Load LinkedIn data
with open('/home/ubuntu/job_hunt_ecosystem/linkedin_profile_data.json', 'r') as f:
    linkedin_data = json.load(f)

# Extract basic information from LinkedIn
first_name = linkedin_data.get('firstName', '')
last_name = linkedin_data.get('lastName', '')
headline = linkedin_data.get('headline', '')
summary = linkedin_data.get('summary', '')

# Create a comprehensive user information form template
user_form = {
    "personal_information": {
        "first_name": first_name,
        "last_name": last_name,
        "email": "",
        "phone": "",
        "address": {
            "street": "",
            "city": "",
            "state": "",
            "zip_code": "",
            "country": "United States"
        },
        "linkedin_url": "https://www.linkedin.com/in/karishma-garikapalli/",
        "portfolio_url": "",
        "github_url": "",
        "other_websites": []
    },
    "visa_status": {
        "status": "H1-B",
        "requires_sponsorship": True,
        "authorized_to_work": True,
        "visa_expiration_date": ""
    },
    "job_preferences": {
        "target_roles": ["Sr. Fullstack Developer", "Software Developer", "Software Engineer"],
        "target_industries": ["Any"],
        "preferred_locations": [],
        "remote_preference": "",  # "Remote", "Hybrid", "On-site"
        "salary_expectations": {
            "minimum": "",
            "preferred": ""
        },
        "willing_to_relocate": False,
        "start_date_availability": ""
    },
    "work_experience": [
        {
            "company": "Republic Services",
            "title": "Sr. Fullstack Developer",
            "location": "",
            "start_date": "May 2025",
            "end_date": "Present",
            "description": "Built a configurable RAG pipeline for an internal project.",
            "technologies": [],
            "achievements": []
        }
        # Additional work experiences will be populated from LinkedIn data
    ],
    "education": [
        # Will be populated from LinkedIn data
    ],
    "skills": {
        "technical": [],
        "soft": [],
        "languages": [],
        "certifications": []
    },
    "projects": [
        {
            "name": "",
            "description": "",
            "technologies": [],
            "url": "",
            "start_date": "",
            "end_date": "",
            "highlights": []
        }
    ],
    "professional_anecdotes": [
        {
            "title": "",
            "situation": "",
            "task": "",
            "action": "",
            "result": "",
            "skills_demonstrated": []
        }
    ],
    "references": [
        {
            "name": "",
            "relationship": "",
            "company": "",
            "email": "",
            "phone": ""
        }
    ],
    "additional_information": {
        "publications": [],
        "patents": [],
        "awards": [],
        "volunteer_experience": [],
        "interests": []
    }
}

# Save the user form template to a JSON file
with open('/home/ubuntu/job_hunt_ecosystem/user_form_template.json', 'w') as f:
    json.dump(user_form, f, indent=4)

print("User form template created successfully.")
