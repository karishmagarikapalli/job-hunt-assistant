import requests
from bs4 import BeautifulSoup
import re
import time
import random
from datetime import datetime

class CompanyWebsiteScraper:
    """
    A class to scrape job postings directly from company career pages.
    """
    
    def __init__(self, headers=None):
        """
        Initialize the company website scraper.
        
        Args:
            headers: Custom headers for HTTP requests
        """
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
        }
    
    def scrape_company(self, company_config, search_term=None, location=None):
        """
        Scrape job postings from a company's career page.
        
        Args:
            company_config: Dictionary containing company configuration
            search_term: Job title or keyword to search for (optional)
            location: Location to search in (optional)
            
        Returns:
            List of job dictionaries
        """
        company_name = company_config["name"]
        career_url = company_config["career_url"]
        
        print(f"Scraping {company_name} career page: {career_url}")
        
        # Determine which scraper to use based on company
        if "scraper_type" in company_config:
            scraper_type = company_config["scraper_type"]
            
            if scraper_type == "workday":
                return self.scrape_workday(company_config, search_term, location)
            elif scraper_type == "greenhouse":
                return self.scrape_greenhouse(company_config, search_term, location)
            elif scraper_type == "lever":
                return self.scrape_lever(company_config, search_term, location)
            elif scraper_type == "smartrecruiters":
                return self.scrape_smartrecruiters(company_config, search_term, location)
            elif scraper_type == "custom":
                return self.scrape_custom(company_config, search_term, location)
        
        # Default generic scraper
        return self.scrape_generic(company_config, search_term, location)
    
    def scrape_generic(self, company_config, search_term=None, location=None):
        """
        Generic scraper for company career pages.
        
        Args:
            company_config: Dictionary containing company configuration
            search_term: Job title or keyword to search for (optional)
            location: Location to search in (optional)
            
        Returns:
            List of job dictionaries
        """
        company_name = company_config["name"]
        career_url = company_config["career_url"]
        
        try:
            # Construct search URL if parameters are provided
            url = career_url
            if search_term or location:
                # Add query parameters if the URL already has parameters
                if "?" in url:
                    url += "&"
                else:
                    url += "?"
                
                if search_term:
                    url += f"q={search_term}"
                    
                if search_term and location:
                    url += "&"
                    
                if location:
                    url += f"location={location}"
            
            # Make request to career page
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job listings
            jobs = []
            
            # Look for common job listing patterns
            job_elements = soup.select(company_config.get("job_selector", ".job-listing, .careers-job, .job-card, .job-item"))
            
            for job_element in job_elements:
                # Extract job details
                job = {
                    "title": self._extract_text(job_element, company_config.get("title_selector", ".job-title, .position-title, h3, h4")),
                    "company": company_name,
                    "location": self._extract_text(job_element, company_config.get("location_selector", ".job-location, .location")),
                    "job_type": self._extract_text(job_element, company_config.get("job_type_selector", ".job-type, .employment-type")),
                    "description": self._extract_text(job_element, company_config.get("description_selector", ".job-description, .description")),
                    "application_url": self._extract_link(job_element, company_config.get("link_selector", "a"), career_url),
                    "source_website": company_name,
                    "date_posted": self._extract_text(job_element, company_config.get("date_selector", ".job-date, .date-posted")),
                    "date_scraped": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Filter for full-time jobs only
                if job["job_type"] and "full" in job["job_type"].lower():
                    jobs.append(job)
                # If job type is not specified, include it anyway and we'll filter later
                elif not job["job_type"]:
                    job["job_type"] = "Full-time"  # Assume full-time as default
                    jobs.append(job)
            
            print(f"Found {len(jobs)} job postings at {company_name}")
            return jobs
            
        except Exception as e:
            print(f"Error scraping {company_name}: {str(e)}")
            return []
    
    def scrape_workday(self, company_config, search_term=None, location=None):
        """
        Scraper for Workday-based career pages.
        
        Args:
            company_config: Dictionary containing company configuration
            search_term: Job title or keyword to search for (optional)
            location: Location to search in (optional)
            
        Returns:
            List of job dictionaries
        """
        company_name = company_config["name"]
        career_url = company_config["career_url"]
        
        try:
            # Workday typically uses a specific URL structure
            url = career_url
            
            # Add search parameters if provided
            if search_term or location:
                # Workday typically uses a different parameter structure
                if search_term:
                    url += f"&keywords={search_term}"
                if location:
                    url += f"&locations={location}"
            
            # Make request to career page
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job listings (Workday specific selectors)
            jobs = []
            
            job_elements = soup.select(".WGDC, .gwt-Label")
            
            for job_element in job_elements:
                # Extract job details
                job = {
                    "title": self._extract_text(job_element, "[data-automation-id='jobTitle']"),
                    "company": company_name,
                    "location": self._extract_text(job_element, "[data-automation-id='locationLabel']"),
                    "job_type": "Full-time",  # Workday often doesn't show job type in listings
                    "description": "",  # Need to visit job page for description
                    "application_url": self._extract_link(job_element, "a", career_url),
                    "source_website": company_name,
                    "date_posted": self._extract_text(job_element, "[data-automation-id='postedOn']"),
                    "date_scraped": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                jobs.append(job)
            
            print(f"Found {len(jobs)} job postings at {company_name} (Workday)")
            return jobs
            
        except Exception as e:
            print(f"Error scraping {company_name} (Workday): {str(e)}")
            return []
    
    def scrape_greenhouse(self, company_config, search_term=None, location=None):
        """
        Scraper for Greenhouse-based career pages.
        
        Args:
            company_config: Dictionary containing company configuration
            search_term: Job title or keyword to search for (optional)
            location: Location to search in (optional)
            
        Returns:
            List of job dictionaries
        """
        company_name = company_config["name"]
        career_url = company_config["career_url"]
        
        try:
            # Greenhouse typically uses a specific URL structure
            url = career_url
            
            # Make request to career page
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job listings (Greenhouse specific selectors)
            jobs = []
            
            job_elements = soup.select(".opening")
            
            for job_element in job_elements:
                title = self._extract_text(job_element, ".opening-title")
                location = self._extract_text(job_element, ".location")
                
                # Filter by search term and location if provided
                if (not search_term or (search_term.lower() in title.lower())) and \
                   (not location or (location and location.lower() in location.lower())):
                    
                    # Extract job details
                    job = {
                        "title": title,
                        "company": company_name,
                        "location": location,
                        "job_type": "Full-time",  # Greenhouse often doesn't show job type in listings
                        "description": "",  # Need to visit job page for description
                        "application_url": self._extract_link(job_element, "a", career_url),
                        "source_website": company_name,
                        "date_posted": "",  # Greenhouse often doesn't show posting date
                        "date_scraped": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Check if it's a full-time job (if specified)
                    department = self._extract_text(job_element, ".department")
                    if "part" not in department.lower():  # Exclude part-time jobs
                        jobs.append(job)
            
            print(f"Found {len(jobs)} job postings at {company_name} (Greenhouse)")
            return jobs
            
        except Exception as e:
            print(f"Error scraping {company_name} (Greenhouse): {str(e)}")
            return []
    
    def scrape_lever(self, company_config, search_term=None, location=None):
        """
        Scraper for Lever-based career pages.
        
        Args:
            company_config: Dictionary containing company configuration
            search_term: Job title or keyword to search for (optional)
            location: Location to search in (optional)
            
        Returns:
            List of job dictionaries
        """
        company_name = company_config["name"]
        career_url = company_config["career_url"]
        
        try:
            # Lever typically uses a specific URL structure
            url = career_url
            
            # Make request to career page
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job listings (Lever specific selectors)
            jobs = []
            
            job_elements = soup.select(".posting")
            
            for job_element in job_elements:
                title = self._extract_text(job_element, "h5")
                location = self._extract_text(job_element, ".location")
                
                # Filter by search term and location if provided
                if (not search_term or (search_term.lower() in title.lower())) and \
                   (not location or (location and location.lower() in location.lower())):
                    
                    # Extract job details
                    job = {
                        "title": title,
                        "company": company_name,
                        "location": location,
                        "job_type": "Full-time",  # Lever often doesn't show job type in listings
                        "description": "",  # Need to visit job page for description
                        "application_url": self._extract_link(job_element, "a", career_url),
                        "source_website": company_name,
                        "date_posted": "",  # Lever often doesn't show posting date
                        "date_scraped": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Check if it's a full-time job (if specified)
                    commitment = self._extract_text(job_element, ".commitment")
                    if not commitment or "full" in commitment.lower():
                        jobs.append(job)
            
            print(f"Found {len(jobs)} job postings at {company_name} (Lever)")
            return jobs
            
        except Exception as e:
            print(f"Error scraping {company_name} (Lever): {str(e)}")
            return []
    
    def scrape_smartrecruiters(self, company_config, search_term=None, location=None):
        """
        Scraper for SmartRecruiters-based career pages.
        
        Args:
            company_config: Dictionary containing company configuration
            search_term: Job title or keyword to search for (optional)
            location: Location to search in (optional)
            
        Returns:
            List of job dictionaries
        """
        company_name = company_config["name"]
        career_url = company_config["career_url"]
        
        try:
            # SmartRecruiters typically uses a specific URL structure
            url = career_url
            
            # Add search parameters if provided
            if search_term or location:
                if "?" in url:
                    url += "&"
                else:
                    url += "?"
                
                if search_term:
                    url += f"search={search_term}"
                    
                if search_term and location:
                    url += "&"
                    
                if location:
                    url += f"location={location}"
            
            # Make request to career page
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job listings (SmartRecruiters specific selectors)
            jobs = []
            
            job_elements = soup.select(".job-list-item")
            
            for job_element in job_elements:
                # Extract job details
                job = {
                    "title": self._extract_text(job_element, ".job-title"),
                    "company": company_name,
                    "location": self._extract_text(job_element, ".job-location"),
                    "job_type": self._extract_text(job_element, ".job-type"),
                    "description": "",  # Need to visit job page for description
                    "application_url": self._extract_link(job_element, "a", career_url),
                    "source_website": company_name,
                    "date_posted": self._extract_text(job_element, ".job-date"),
                    "date_scraped": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Filter for full-time jobs only
                if not job["job_type"] or "full" in job["job_type"].lower():
                    jobs.append(job)
            
            print(f"Found {len(jobs)} job postings at {company_name} (SmartRecruiters)")
            return jobs
            
        except Exception as e:
            print(f"Error scraping {company_name} (SmartRecruiters): {str(e)}")
            return []
    
    def scrape_custom(self, company_config, search_term=None, location=None):
        """
        Custom scraper for company-specific career pages.
        
        Args:
            company_config: Dictionary containing company configuration
            search_term: Job title or keyword to search for (optional)
            location: Location to search in (optional)
            
        Returns:
            List of job dictionaries
        """
        company_name = company_config["name"]
        career_url = company_config["career_url"]
        
        try:
            # Use company-specific configuration
            url = career_url
            
            # Add search parameters if provided and if search_url_template is defined
            if (search_term or location) and "search_url_template" in company_config:
                url = company_config["search_url_template"]
                url = url.replace("{search_term}", search_term or "")
                url = url.replace("{location}", location or "")
            
            # Make request to career page
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job listings using custom selectors
            jobs = []
            
            job_elements = soup.select(company_config.get("job_selector", ".job"))
            
            for job_element in job_elements:
                # Extract job details using custom selectors
                job = {
                    "title": self._extract_text(job_element, company_config.get("title_selector", ".title")),
                    "company": company_name,
                    "location": self._extract_text(job_element, company_config.get("location_selector", ".location")),
                    "job_type": self._extract_text(job_element, company_config.get("job_type_selector", ".job-type")),
                    "description": self._extract_text(job_element, company_config.get("description_selector", ".description")),
                    "application_url": self._extract_link(job_element, company_config.get("link_selector", "a"), career_url),
                    "source_website": company_name,
                    "date_posted": self._extract_text(job_element, company_config.get("date_selector", ".date")),
                    "date_scraped": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Filter for full-time jobs only
                if not job["job_type"] or "full" in job["job_type"].lower():
                    jobs.append(job)
            
            print(f"Found {len(jobs)} job postings at {company_name} (Custom)")
            return jobs
            
        except Exception as e:
            print(f"Error scraping {company_name} (Custom): {str(e)}")
            return []
    
    def _extract_text(self, element, selector):
        """Extract text from an element using a CSS selector."""
        try:
            selected = element.select_one(selector)
            return selected.get_text(strip=True) if selected else ""
        except Exception:
            return ""
    
    def _extract_link(self, element, selector, base_url):
        """Extract link from an element using a CSS selector."""
        try:
            selected = element.select_one(selector)
            if selected and selected.has_attr('href'):
                href = selected['href']
                # Handle relative URLs
                if href.startswith('/'):
                    # Extract domain from base_url
                    domain = re.match(r'https?://[^/]+', base_url)
                    if domain:
                        return domain.group(0) + href
                    return base_url + href
                # Handle absolute URLs
                elif href.startswith('http'):
                    return href
                # Handle other relative URLs
                else:
                    return base_url + '/' + href
            return ""
        except Exception:
            return ""
