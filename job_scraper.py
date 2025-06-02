import json
import os
import sqlite3
import time
import random
from datetime import datetime
import re
from urllib.parse import urljoin
from company_website_scraper import CompanyWebsiteScraper

class JobScraper:
    """
    A class to scrape job postings from various job boards
    and store them in the database.
    """
    
    def __init__(self, config_path='/home/ubuntu/job_hunt_ecosystem/config/job_boards.json', 
                 db_path='/home/ubuntu/job_hunt_ecosystem/job_hunt.db'):
        """
        Initialize the job scraper with configuration and database connection.
        
        Args:
            config_path: Path to the job boards configuration file
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self.config_path = config_path
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Set up headers for requests to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
        }
    
    def connect_db(self):
        """Connect to the SQLite database and return connection and cursor."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        return conn, cursor
    
    def save_job_posting(self, job_data):
        """
        Save a job posting to the database.
        
        Args:
            job_data: Dictionary containing job posting data
        
        Returns:
            job_id: ID of the inserted job posting
        """
        conn, cursor = self.connect_db()
        
        # Check if job already exists to avoid duplicates
        cursor.execute('''
        SELECT id FROM job_postings 
        WHERE title = ? AND company = ? AND application_url = ?
        ''', (job_data['title'], job_data['company'], job_data['application_url']))
        
        existing_job = cursor.fetchone()
        
        if existing_job:
            conn.close()
            return existing_job[0]  # Return existing job ID
        
        # Insert new job posting
        cursor.execute('''
        INSERT INTO job_postings (
            title, company, location, job_type, description, 
            requirements, salary_range, application_url, 
            source_website, date_posted, date_scraped,
            status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_data['title'],
            job_data['company'],
            job_data['location'],
            job_data['job_type'],
            job_data['description'],
            job_data['requirements'],
            job_data['salary_range'],
            job_data['application_url'],
            job_data['source_website'],
            job_data['date_posted'],
            job_data['date_scraped'],
            'new',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Save job description to file
        self.save_job_description_to_file(job_id, job_data)
        
        return job_id
    
    def save_job_description_to_file(self, job_id, job_data):
        """
        Save the job description to a file for future reference.
        
        Args:
            job_id: ID of the job posting
            job_data: Dictionary containing job posting data
        """
        job_desc_dir = '/home/ubuntu/job_hunt_ecosystem/job_descriptions'
        
        # Create a sanitized filename
        company_name = re.sub(r'[^\w\s-]', '', job_data['company']).strip()
        job_title = re.sub(r'[^\w\s-]', '', job_data['title']).strip()
        filename = f"{job_id}_{company_name}_{job_title}.txt".replace(' ', '_')
        
        # Prepare content
        content = f"""
Job Title: {job_data['title']}
Company: {job_data['company']}
Location: {job_data['location']}
Job Type: {job_data['job_type']}
Date Posted: {job_data['date_posted']}
Date Scraped: {job_data['date_scraped']}
Source: {job_data['source_website']}
Application URL: {job_data['application_url']}
Salary Range: {job_data['salary_range']}

DESCRIPTION:
{job_data['description']}

REQUIREMENTS:
{job_data['requirements']}
"""
        
        # Write to file
        with open(os.path.join(job_desc_dir, filename), 'w') as f:
            f.write(content)
    
    def check_h1b_sponsorship(self, description):
        """
        Check if the job description mentions H1B sponsorship.
        
        Args:
            description: Job description text
            
        Returns:
            Boolean indicating if H1B sponsorship is mentioned
        """
        description_lower = description.lower()
        
        # Check for positive mentions of sponsorship
        for keyword in self.config['h1b_sponsorship_keywords']:
            if keyword.lower() in description_lower:
                # Check for negative phrases
                negative_phrases = [
                    "no h1b", "not sponsor", "no sponsor", "not providing sponsor",
                    "cannot sponsor", "do not sponsor", "doesn't sponsor", "does not sponsor",
                    "no visa", "not eligible for sponsorship"
                ]
                
                for phrase in negative_phrases:
                    if phrase in description_lower:
                        return False
                
                return True
        
        return False
    
    def check_excluded_keywords(self, description):
        """
        Check if the job description contains excluded keywords.
        
        Args:
            description: Job description text
            
        Returns:
            Boolean indicating if excluded keywords are found
        """
        description_lower = description.lower()
        
        for keyword in self.config['exclude_keywords']:
            if keyword.lower() in description_lower:
                return True
        
        return False
    
    def scrape_linkedin_jobs(self, search_term, location=""):
        """
        Scrape job postings from LinkedIn.
        
        Args:
            search_term: Job title or keyword to search for
            location: Location to search in (optional)
            
        Returns:
            List of job IDs that were scraped and saved
        """
        print(f"Scraping LinkedIn jobs for: {search_term} in {location if location else 'any location'}")
        
        # Construct search URL
        base_url = "https://www.linkedin.com/jobs/search/"
        params = {
            "keywords": search_term,
            "location": location,
            "f_TPR": "r86400",  # Last 24 hours
            "position": 1,
            "pageNum": 0
        }
        
        # This is a placeholder for actual implementation
        # In a real implementation, you would need to use a browser automation tool like Selenium
        # or Playwright to handle LinkedIn's dynamic content and authentication
        
        print("Note: LinkedIn scraping requires browser automation and authentication.")
        print("This is a placeholder for the actual implementation.")
        
        # Placeholder for scraped jobs
        return []
    
    def scrape_indeed_jobs(self, search_term, location=""):
        """
        Scrape job postings from Indeed.
        
        Args:
            search_term: Job title or keyword to search for
            location: Location to search in (optional)
            
        Returns:
            List of job IDs that were scraped and saved
        """
        print(f"Scraping Indeed jobs for: {search_term} in {location if location else 'any location'}")
        
        # Construct search URL
        base_url = "https://www.indeed.com/jobs"
        params = {
            "q": search_term,
            "l": location,
            "fromage": 1,  # Last 24 hours
            "sort": "date"
        }
        
        # This is a placeholder for actual implementation
        # In a real implementation, you would need to handle Indeed's anti-scraping measures
        
        print("Note: Indeed scraping requires handling of anti-scraping measures.")
        print("This is a placeholder for the actual implementation.")
        
        # Placeholder for scraped jobs
        return []
    
    def scrape_glassdoor_jobs(self, search_term, location=""):
        """
        Scrape job postings from Glassdoor.
        
        Args:
            search_term: Job title or keyword to search for
            location: Location to search in (optional)
            
        Returns:
            List of job IDs that were scraped and saved
        """
        print(f"Scraping Glassdoor jobs for: {search_term} in {location if location else 'any location'}")
        
        # Construct search URL
        base_url = "https://www.glassdoor.com/Job/jobs.htm"
        params = {
            "sc.keyword": search_term,
            "locT": "C",
            "locId": location,
            "fromAge": 1,  # Last 24 hours
            "sort.type": "date_desc"
        }
        
        # This is a placeholder for actual implementation
        # In a real implementation, you would need to handle Glassdoor's login requirements
        
        print("Note: Glassdoor scraping requires handling of login requirements.")
        print("This is a placeholder for the actual implementation.")
        
        # Placeholder for scraped jobs
        return []
    
    def run_scraper(self):
        """
        Run the job scraper for all enabled job boards and search terms.
        
        Returns:
            Dictionary with statistics about the scraping run
        """
        stats = {
            "total_jobs_scraped": 0,
            "jobs_with_h1b_sponsorship": 0,
            "jobs_excluded": 0,
            "jobs_by_source": {}
        }
        
        # Get enabled job boards
        enabled_job_boards = [board for board in self.config["job_boards"] if board["enabled"]]
        
        # Get company websites to target directly
        enabled_company_websites = [company for company in self.config.get("target_companies", []) if company.get("enabled", True)]
        
        # Iterate through search terms and locations
        for search_term in self.config["search_terms"]:
            locations = self.config["locations"] if self.config["locations"] else [""]
            
            for location in locations:
                # First scrape job boards
                for job_board in enabled_job_boards:
                    board_name = job_board["name"]
                    
                    # Initialize stats for this job board if not exists
                    if board_name not in stats["jobs_by_source"]:
                        stats["jobs_by_source"][board_name] = 0
                    
                    # Call the appropriate scraper method based on job board
                    if board_name == "LinkedIn":
                        job_ids = self.scrape_linkedin_jobs(search_term, location)
                    elif board_name == "Indeed":
                        job_ids = self.scrape_indeed_jobs(search_term, location)
                    elif board_name == "Glassdoor":
                        job_ids = self.scrape_glassdoor_jobs(search_term, location)
                    else:
                        print(f"Scraper for {board_name} not implemented yet.")
                        job_ids = []
                
                # Then scrape company career pages directly
                for company in enabled_company_websites:
                    company_name = company["name"]
                    
                    # Initialize stats for this company if not exists
                    if company_name not in stats["jobs_by_source"]:
                        stats["jobs_by_source"][company_name] = 0
                    
                    # Scrape company career page
                    job_ids = self.scrape_company_website(company, search_term, location)
                    
                    # Update stats
                    stats["jobs_by_source"][company_name] += len(job_ids)
                    stats["total_jobs_scraped"] += len(job_ids)
                    
                    # Update stats
                    stats["jobs_by_source"][board_name] += len(job_ids)
                    stats["total_jobs_scraped"] += len(job_ids)
                    
                    # Add random delay between requests to avoid rate limiting
                    time.sleep(random.uniform(2, 5))
        
        return stats

# Example usage
if __name__ == "__main__":
    scraper = JobScraper()
    
    # For demonstration, let's create a sample job posting
    sample_job = {
        "title": "Senior Full Stack Developer",
        "company": "Example Tech Corp",
        "location": "Remote, US",
        "job_type": "Full-time",
        "description": "We are looking for a Senior Full Stack Developer to join our team. The ideal candidate will have experience with React, Node.js, and AWS. This position offers H1B visa sponsorship for qualified candidates.",
        "requirements": "- 5+ years of experience in full stack development\n- Strong knowledge of React, Node.js, and AWS\n- Experience with microservices architecture\n- Bachelor's degree in Computer Science or related field",
        "salary_range": "$120,000 - $150,000",
        "application_url": "https://example.com/careers/senior-full-stack-developer",
        "source_website": "Example Job Board",
        "date_posted": "2025-05-28",
        "date_scraped": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save the sample job
    job_id = scraper.save_job_posting(sample_job)
    print(f"Sample job saved with ID: {job_id}")
    
    # Run the scraper (this will just print placeholder messages)
    print("\nRunning job scraper...")
    stats = scraper.run_scraper()
    
    print("\nScraping statistics:")
    print(f"Total jobs scraped: {stats['total_jobs_scraped']}")
    print(f"Jobs by source: {stats['jobs_by_source']}")

    def scrape_company_website(self, company_config, search_term=None, location=None):
        """
        Scrape job postings from a company's career page.
        
        Args:
            company_config: Dictionary containing company configuration
            search_term: Job title or keyword to search for (optional)
            location: Location to search in (optional)
            
        Returns:
            List of job IDs that were scraped and saved
        """
        company_name = company_config["name"]
        print(f"Scraping {company_name} career page for: {search_term} in {location if location else 'any location'}")
        
        # Initialize company website scraper
        company_scraper = CompanyWebsiteScraper(headers=self.headers)
        
        # Scrape job postings
        job_postings = company_scraper.scrape_company(company_config, search_term, location)
        
        # Filter for full-time jobs only
        full_time_jobs = []
        for job in job_postings:
            job_type = job.get("job_type", "").lower()
            if not job_type or "full" in job_type:
                # Set job type to Full-time if not specified
                if not job_type:
                    job["job_type"] = "Full-time"
                full_time_jobs.append(job)
        
        print(f"Found {len(full_time_jobs)} full-time job postings at {company_name}")
        
        # Save job postings to database
        job_ids = []
        for job in full_time_jobs:
            # Check if job description mentions H1B sponsorship
            if self.check_h1b_sponsorship(job.get("description", "")):
                # Check if job doesn't contain excluded keywords
                if not self.check_excluded_keywords(job.get("description", "")):
                    # Save job posting
                    job_id = self.save_job_posting(job)
                    job_ids.append(job_id)
        
        return job_ids
