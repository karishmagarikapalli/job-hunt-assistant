import os
import logging
import json
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'logs', 'job_matcher.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('job_matcher')

class JobMatcher:
    """
    AI-powered job matching system that analyzes job postings and user profiles
    to determine compatibility and match scores.
    """
    
    def __init__(self, model_config=None):
        """
        Initialize the job matcher.
        
        Args:
            model_config (dict): Configuration for the matching model
        """
        self.model_config = model_config or {
            'skill_weight': 0.5,
            'experience_weight': 0.3,
            'education_weight': 0.1,
            'title_weight': 0.1,
            'min_match_score': 0.6,
            'vectorizer_params': {
                'max_features': 10000,
                'ngram_range': (1, 2),
                'stop_words': 'english'
            }
        }
        
        # Initialize vectorizer for text similarity
        self.vectorizer = TfidfVectorizer(**self.model_config['vectorizer_params'])
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'logs'), exist_ok=True)
    
    def match_jobs(self, user_profile, job_postings):
        """
        Match user profile with job postings.
        
        Args:
            user_profile (dict): User profile data
            job_postings (list): List of job posting data
        
        Returns:
            list: Sorted list of job matches with scores
        """
        try:
            if not job_postings:
                logger.warning("No job postings provided for matching")
                return []
            
            # Extract user features
            user_skills = self._extract_skills(user_profile)
            user_experience = self._extract_experience(user_profile)
            user_education = self._extract_education(user_profile)
            user_title = user_profile.get('current_title', '')
            
            # Prepare user text for vectorization
            user_text = self._prepare_text_for_vectorization(user_profile)
            
            # Prepare job texts for vectorization
            job_texts = [self._prepare_text_for_vectorization(job) for job in job_postings]
            
            # Combine user and job texts for vectorization
            all_texts = [user_text] + job_texts
            
            # Vectorize texts
            try:
                tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            except Exception as e:
                logger.error(f"Error in vectorization: {str(e)}")
                # Fallback to simple matching if vectorization fails
                return self._fallback_matching(user_profile, job_postings)
            
            # Calculate similarity scores
            user_vector = tfidf_matrix[0]
            job_vectors = tfidf_matrix[1:]
            
            # Calculate cosine similarity between user and jobs
            similarity_scores = cosine_similarity(user_vector, job_vectors).flatten()
            
            # Calculate match scores for each job
            matches = []
            for i, job in enumerate(job_postings):
                # Get text similarity score
                text_similarity = similarity_scores[i]
                
                # Calculate skill match score
                job_skills = self._extract_skills(job)
                skill_match = self._calculate_skill_match(user_skills, job_skills)
                
                # Calculate experience match score
                job_experience = job.get('experience_required', '')
                experience_match = self._calculate_experience_match(user_experience, job_experience)
                
                # Calculate education match score
                job_education = job.get('education_required', '')
                education_match = self._calculate_education_match(user_education, job_education)
                
                # Calculate title match score
                job_title = job.get('title', '')
                title_match = self._calculate_title_match(user_title, job_title)
                
                # Calculate weighted match score
                match_score = (
                    self.model_config['skill_weight'] * skill_match +
                    self.model_config['experience_weight'] * experience_match +
                    self.model_config['education_weight'] * education_match +
                    self.model_config['title_weight'] * title_match +
                    text_similarity * 0.2  # Add text similarity with a weight of 0.2
                )
                
                # Check for H1-B sponsorship requirement
                if user_profile.get('requires_h1b_sponsorship', False) and not job.get('offers_visa_sponsorship', False):
                    match_score *= 0.5  # Reduce score for jobs that don't offer sponsorship
                
                # Check for full-time requirement
                if user_profile.get('prefers_full_time', True) and job.get('job_type', '').lower() != 'full-time':
                    match_score *= 0.7  # Reduce score for non-full-time jobs
                
                # Create match object
                match = {
                    'job_id': job.get('id'),
                    'match_score': round(match_score, 2),
                    'skill_match': round(skill_match, 2),
                    'experience_match': round(experience_match, 2),
                    'education_match': round(education_match, 2),
                    'title_match': round(title_match, 2),
                    'text_similarity': round(float(text_similarity), 2),
                    'match_details': {
                        'matching_skills': list(set(user_skills) & set(job_skills)),
                        'missing_skills': list(set(job_skills) - set(user_skills)),
                        'experience_analysis': self._analyze_experience_match(user_experience, job_experience),
                        'education_analysis': self._analyze_education_match(user_education, job_education),
                        'title_relevance': self._analyze_title_match(user_title, job_title)
                    }
                }
                
                matches.append(match)
            
            # Sort matches by score in descending order
            matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            # Filter matches below minimum score
            min_score = self.model_config.get('min_match_score', 0.6)
            matches = [m for m in matches if m['match_score'] >= min_score]
            
            logger.info(f"Matched {len(matches)} jobs with scores above {min_score}")
            return matches
        except Exception as e:
            logger.error(f"Error in job matching: {str(e)}")
            return self._fallback_matching(user_profile, job_postings)
    
    def _fallback_matching(self, user_profile, job_postings):
        """
        Simple fallback matching when advanced matching fails.
        
        Args:
            user_profile (dict): User profile data
            job_postings (list): List of job posting data
        
        Returns:
            list: Sorted list of job matches with scores
        """
        try:
            matches = []
            user_skills = self._extract_skills(user_profile)
            
            for job in job_postings:
                job_skills = self._extract_skills(job)
                skill_match = self._calculate_skill_match(user_skills, job_skills)
                
                match = {
                    'job_id': job.get('id'),
                    'match_score': round(skill_match, 2),
                    'skill_match': round(skill_match, 2),
                    'experience_match': 0.5,  # Default value
                    'education_match': 0.5,  # Default value
                    'title_match': 0.5,  # Default value
                    'text_similarity': 0.0,
                    'match_details': {
                        'matching_skills': list(set(user_skills) & set(job_skills)),
                        'missing_skills': list(set(job_skills) - set(user_skills)),
                        'experience_analysis': "Fallback matching used",
                        'education_analysis': "Fallback matching used",
                        'title_relevance': "Fallback matching used"
                    }
                }
                
                matches.append(match)
            
            # Sort matches by score in descending order
            matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            # Filter matches below minimum score
            min_score = self.model_config.get('min_match_score', 0.6)
            matches = [m for m in matches if m['match_score'] >= min_score]
            
            logger.info(f"Fallback matching used: matched {len(matches)} jobs")
            return matches
        except Exception as e:
            logger.error(f"Error in fallback matching: {str(e)}")
            return []
    
    def _prepare_text_for_vectorization(self, data_dict):
        """
        Prepare text from data dictionary for vectorization.
        
        Args:
            data_dict (dict): Data dictionary
        
        Returns:
            str: Prepared text
        """
        text_fields = [
            data_dict.get('title', ''),
            data_dict.get('description', ''),
            data_dict.get('skills', ''),
            data_dict.get('experience', ''),
            data_dict.get('education', ''),
            data_dict.get('responsibilities', ''),
            data_dict.get('requirements', '')
        ]
        
        # Join all text fields
        text = ' '.join([str(field) for field in text_fields if field])
        
        # Clean text
        text = text.lower()
        
        return text
    
    def _extract_skills(self, data_dict):
        """
        Extract skills from data dictionary.
        
        Args:
            data_dict (dict): Data dictionary
        
        Returns:
            list: List of skills
        """
        skills = []
        
        # Extract from skills field
        if 'skills' in data_dict:
            if isinstance(data_dict['skills'], list):
                skills.extend(data_dict['skills'])
            elif isinstance(data_dict['skills'], str):
                skills.extend([s.strip() for s in data_dict['skills'].split(',')])
        
        # Extract from description
        if 'description' in data_dict:
            # This is a simplified approach; in a real system, you'd use NLP techniques
            description = data_dict['description'].lower()
            common_skills = [
                'python', 'javascript', 'java', 'c++', 'c#', 'react', 'angular', 'vue',
                'node.js', 'django', 'flask', 'spring', 'sql', 'nosql', 'mongodb',
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd', 'git',
                'agile', 'scrum', 'product management', 'project management',
                'machine learning', 'ai', 'data science', 'data analysis',
                'full stack', 'frontend', 'backend', 'devops', 'cloud', 'security'
            ]
            
            for skill in common_skills:
                if skill in description:
                    skills.append(skill)
        
        # Remove duplicates and return
        return list(set(skills))
    
    def _extract_experience(self, data_dict):
        """
        Extract experience from data dictionary.
        
        Args:
            data_dict (dict): Data dictionary
        
        Returns:
            dict: Experience data
        """
        experience = {
            'years': 0,
            'positions': []
        }
        
        # Extract from experience field
        if 'experience' in data_dict:
            if isinstance(data_dict['experience'], str):
                # Try to extract years from text
                text = data_dict['experience'].lower()
                if 'year' in text:
                    # Extract numbers before "year"
                    import re
                    years_match = re.search(r'(\d+)[\s-]*year', text)
                    if years_match:
                        experience['years'] = int(years_match.group(1))
            elif isinstance(data_dict['experience'], (int, float)):
                experience['years'] = data_dict['experience']
        
        # Extract from work_history
        if 'work_history' in data_dict and isinstance(data_dict['work_history'], list):
            for job in data_dict['work_history']:
                if isinstance(job, dict):
                    position = {
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'duration': job.get('duration', 0)
                    }
                    experience['positions'].append(position)
                    
                    # Add to total years if duration is available
                    if 'duration' in job and isinstance(job['duration'], (int, float)):
                        experience['years'] += job['duration']
        
        return experience
    
    def _extract_education(self, data_dict):
        """
        Extract education from data dictionary.
        
        Args:
            data_dict (dict): Data dictionary
        
        Returns:
            dict: Education data
        """
        education = {
            'highest_degree': None,
            'degrees': []
        }
        
        # Extract from education field
        if 'education' in data_dict:
            if isinstance(data_dict['education'], str):
                education['highest_degree'] = data_dict['education']
            elif isinstance(data_dict['education'], list):
                education['degrees'] = data_dict['education']
                
                # Determine highest degree
                degree_levels = {
                    'high school': 1,
                    'associate': 2,
                    'bachelor': 3,
                    'master': 4,
                    'phd': 5,
                    'doctorate': 5
                }
                
                highest_level = 0
                for degree in data_dict['education']:
                    degree_text = degree.lower() if isinstance(degree, str) else ''
                    for level_name, level_value in degree_levels.items():
                        if level_name in degree_text and level_value > highest_level:
                            highest_level = level_value
                            education['highest_degree'] = degree
        
        # Extract from education_history
        if 'education_history' in data_dict and isinstance(data_dict['education_history'], list):
            for edu in data_dict['education_history']:
                if isinstance(edu, dict):
                    degree = {
                        'degree': edu.get('degree', ''),
                        'institution': edu.get('institution', ''),
                        'year': edu.get('year', '')
                    }
                    education['degrees'].append(degree)
                    
                    # Update highest degree if not set
                    if not education['highest_degree']:
                        education['highest_degree'] = edu.get('degree', '')
        
        return education
    
    def _calculate_skill_match(self, user_skills, job_skills):
        """
        Calculate skill match score.
        
        Args:
            user_skills (list): User skills
            job_skills (list): Job skills
        
        Returns:
            float: Match score between 0 and 1
        """
        if not job_skills:
            return 1.0  # If job doesn't specify skills, assume full match
        
        # Convert to sets for intersection
        user_skills_set = set(s.lower() for s in user_skills)
        job_skills_set = set(s.lower() for s in job_skills)
        
        # Calculate match score
        matching_skills = user_skills_set.intersection(job_skills_set)
        match_score = len(matching_skills) / len(job_skills_set) if job_skills_set else 1.0
        
        return match_score
    
    def _calculate_experience_match(self, user_experience, job_experience):
        """
        Calculate experience match score.
        
        Args:
            user_experience (dict): User experience data
            job_experience (str): Job experience requirement
        
        Returns:
            float: Match score between 0 and 1
        """
        if not job_experience:
            return 1.0  # If job doesn't specify experience, assume full match
        
        # Extract years from job experience
        import re
        years_match = re.search(r'(\d+)[\s-]*year', job_experience.lower())
        required_years = int(years_match.group(1)) if years_match else 0
        
        if required_years == 0:
            return 1.0
        
        user_years = user_experience.get('years', 0)
        
        # Calculate match score
        if user_years >= required_years:
            return 1.0
        elif user_years >= required_years * 0.7:
            return 0.8  # Close enough
        elif user_years >= required_years * 0.5:
            return 0.6  # Somewhat close
        else:
            return 0.4  # Not close
    
    def _calculate_education_match(self, user_education, job_education):
        """
        Calculate education match score.
        
        Args:
            user_education (dict): User education data
            job_education (str): Job education requirement
        
        Returns:
            float: Match score between 0 and 1
        """
        if not job_education:
            return 1.0  # If job doesn't specify education, assume full match
        
        # Define degree levels
        degree_levels = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'phd': 5,
            'doctorate': 5
        }
        
        # Determine required degree level
        required_level = 0
        for level_name, level_value in degree_levels.items():
            if level_name in job_education.lower():
                required_level = level_value
                break
        
        if required_level == 0:
            return 1.0  # If can't determine required level, assume full match
        
        # Determine user's highest degree level
        user_level = 0
        highest_degree = user_education.get('highest_degree', '')
        if highest_degree:
            for level_name, level_value in degree_levels.items():
                if level_name in highest_degree.lower():
                    user_level = level_value
                    break
        
        # Calculate match score
        if user_level >= required_level:
            return 1.0
        elif user_level == required_level - 1:
            return 0.8  # One level below
        elif user_level == required_level - 2:
            return 0.6  # Two levels below
        else:
            return 0.4  # More than two levels below
    
    def _calculate_title_match(self, user_title, job_title):
        """
        Calculate title match score.
        
        Args:
            user_title (str): User's current title
            job_title (str): Job title
        
        Returns:
            float: Match score between 0 and 1
        """
        if not user_title or not job_title:
            return 0.7  # Default score if either title is missing
        
        # Convert to lowercase for comparison
        user_title = user_title.lower()
        job_title = job_title.lower()
        
        # Define common role categories
        role_categories = {
            'developer': ['developer', 'engineer', 'programmer', 'coder', 'software'],
            'data': ['data', 'analyst', 'scientist', 'analytics', 'business intelligence'],
            'design': ['designer', 'ux', 'ui', 'user experience', 'user interface'],
            'product': ['product', 'manager', 'owner', 'management'],
            'devops': ['devops', 'sre', 'reliability', 'operations', 'infrastructure'],
            'qa': ['qa', 'quality', 'tester', 'testing', 'assurance'],
            'fullstack': ['fullstack', 'full stack', 'full-stack'],
            'frontend': ['frontend', 'front end', 'front-end'],
            'backend': ['backend', 'back end', 'back-end'],
            'solution': ['solution', 'architect', 'consultant', 'engineering']
        }
        
        # Determine user's role category
        user_category = None
        for category, keywords in role_categories.items():
            if any(keyword in user_title for keyword in keywords):
                user_category = category
                break
        
        # Determine job's role category
        job_category = None
        for category, keywords in role_categories.items():
            if any(keyword in job_title for keyword in keywords):
                job_category = category
                break
        
        # Calculate match score
        if user_category and job_category and user_category == job_category:
            return 1.0  # Same category
        elif user_category and job_category:
            # Some categories are related
            related_categories = {
                'developer': ['fullstack', 'frontend', 'backend', 'solution'],
                'fullstack': ['developer', 'frontend', 'backend', 'solution'],
                'frontend': ['developer', 'fullstack', 'design'],
                'backend': ['developer', 'fullstack', 'devops'],
                'solution': ['developer', 'fullstack', 'product']
            }
            
            if user_category in related_categories and job_category in related_categories.get(user_category, []):
                return 0.8  # Related category
            else:
                return 0.6  # Different category
        else:
            # Direct text comparison as fallback
            words_user = set(user_title.split())
            words_job = set(job_title.split())
            common_words = words_user.intersection(words_job)
            
            if common_words:
                return 0.7  # Some common words
            else:
                return 0.5  # No common words
    
    def _analyze_experience_match(self, user_experience, job_experience):
        """
        Analyze experience match for detailed feedback.
        
        Args:
            user_experience (dict): User experience data
            job_experience (str): Job experience requirement
        
        Returns:
            str: Analysis text
        """
        if not job_experience:
            return "No specific experience requirement mentioned."
        
        # Extract years from job experience
        import re
        years_match = re.search(r'(\d+)[\s-]*year', job_experience.lower())
        required_years = int(years_match.group(1)) if years_match else 0
        
        if required_years == 0:
            return "No specific years of experience required."
        
        user_years = user_experience.get('years', 0)
        
        if user_years >= required_years:
            return f"You meet the experience requirement of {required_years} years with your {user_years} years of experience."
        else:
            gap = required_years - user_years
            return f"You have {user_years} years of experience, which is {gap} years less than the required {required_years} years."
    
    def _analyze_education_match(self, user_education, job_education):
        """
        Analyze education match for detailed feedback.
        
        Args:
            user_education (dict): User education data
            job_education (str): Job education requirement
        
        Returns:
            str: Analysis text
        """
        if not job_education:
            return "No specific education requirement mentioned."
        
        highest_degree = user_education.get('highest_degree', '')
        
        if not highest_degree:
            return "Your education information is not available for comparison."
        
        # Check if user's degree matches job requirement
        if highest_degree.lower() in job_education.lower():
            return f"Your {highest_degree} degree matches the job requirement."
        else:
            return f"The job requires {job_education}, and your highest degree is {highest_degree}."
    
    def _analyze_title_match(self, user_title, job_title):
        """
        Analyze title match for detailed feedback.
        
        Args:
            user_title (str): User's current title
            job_title (str): Job title
        
        Returns:
            str: Analysis text
        """
        if not user_title:
            return "Your current title is not available for comparison."
        
        if not job_title:
            return "Job title is not available for comparison."
        
        # Convert to lowercase for comparison
        user_title = user_title.lower()
        job_title = job_title.lower()
        
        # Check for exact match
        if user_title == job_title:
            return f"Your current title '{user_title}' exactly matches the job title."
        
        # Check for partial match
        words_user = set(user_title.split())
        words_job = set(job_title.split())
        common_words = words_user.intersection(words_job)
        
        if common_words:
            return f"Your current title '{user_title}' shares some keywords with the job title '{job_title}'."
        else:
            return f"Your current title '{user_title}' is different from the job title '{job_title}'."
    
    def analyze_job(self, job_posting, user_profile=None):
        """
        Analyze a job posting for key requirements and insights.
        
        Args:
            job_posting (dict): Job posting data
            user_profile (dict): Optional user profile for personalized analysis
        
        Returns:
            dict: Job analysis results
        """
        try:
            # Extract key information from job posting
            job_skills = self._extract_skills(job_posting)
            job_experience = job_posting.get('experience_required', '')
            job_education = job_posting.get('education_required', '')
            job_title = job_posting.get('title', '')
            job_description = job_posting.get('description', '')
            
            # Basic analysis
            analysis = {
                'job_id': job_posting.get('id'),
                'key_skills': job_skills,
                'experience_required': job_experience,
                'education_required': job_education,
                'job_level': self._determine_job_level(job_title, job_description),
                'job_type': job_posting.get('job_type', 'Unknown'),
                'keywords': self._extract_keywords(job_description),
                'company_culture': self._analyze_company_culture(job_posting),
                'suggested_resume_focus': self._suggest_resume_focus(job_posting),
                'suggested_cover_letter_points': self._suggest_cover_letter_points(job_posting)
            }
            
            # Add personalized analysis if user profile is provided
            if user_profile:
                user_skills = self._extract_skills(user_profile)
                user_experience = self._extract_experience(user_profile)
                user_education = self._extract_education(user_profile)
                
                analysis['personalized'] = {
                    'matching_skills': list(set(user_skills) & set(job_skills)),
                    'missing_skills': list(set(job_skills) - set(user_skills)),
                    'experience_match': self._analyze_experience_match(user_experience, job_experience),
                    'education_match': self._analyze_education_match(user_education, job_education),
                    'overall_fit': self._calculate_overall_fit(user_profile, job_posting)
                }
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing job: {str(e)}")
            return {
                'job_id': job_posting.get('id'),
                'error': f"Error analyzing job: {str(e)}"
            }
    
    def _determine_job_level(self, title, description):
        """
        Determine job level from title and description.
        
        Args:
            title (str): Job title
            description (str): Job description
        
        Returns:
            str: Job level
        """
        title = title.lower()
        description = description.lower()
        
        # Check for level indicators in title
        if any(word in title for word in ['senior', 'sr', 'lead', 'principal', 'staff']):
            return 'Senior'
        elif any(word in title for word in ['junior', 'jr', 'associate', 'entry']):
            return 'Junior'
        elif any(word in title for word in ['manager', 'director', 'head']):
            return 'Management'
        elif any(word in title for word in ['intern', 'internship']):
            return 'Intern'
        
        # Check description for clues
        if any(word in description for word in ['senior', 'experienced', 'expert', 'lead']):
            return 'Senior'
        elif any(word in description for word in ['junior', 'entry', 'entry-level', 'entry level']):
            return 'Junior'
        
        # Default to mid-level
        return 'Mid-level'
    
    def _extract_keywords(self, text):
        """
        Extract important keywords from text.
        
        Args:
            text (str): Text to analyze
        
        Returns:
            list: Important keywords
        """
        if not text:
            return []
        
        # This is a simplified approach; in a real system, you'd use NLP techniques
        # like TF-IDF or keyword extraction algorithms
        
        # Convert to lowercase and split into words
        words = text.lower().split()
        
        # Remove common stop words
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
                     'when', 'where', 'how', 'who', 'which', 'this', 'that', 'to', 'of',
                     'in', 'for', 'with', 'on', 'at', 'from', 'by', 'about', 'will',
                     'be', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'do', 'does',
                     'did', 'can', 'could', 'should', 'would', 'may', 'might', 'must'}
        
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count word frequencies
        from collections import Counter
        word_counts = Counter(filtered_words)
        
        # Get top keywords
        top_keywords = [word for word, count in word_counts.most_common(10)]
        
        return top_keywords
    
    def _analyze_company_culture(self, job_posting):
        """
        Analyze company culture from job posting.
        
        Args:
            job_posting (dict): Job posting data
        
        Returns:
            str: Company culture analysis
        """
        description = job_posting.get('description', '')
        company = job_posting.get('company', '')
        
        if not description:
            return "No information available about company culture."
        
        # Look for culture indicators
        culture_indicators = {
            'fast-paced': ['fast-paced', 'fast paced', 'dynamic', 'rapidly', 'quickly'],
            'innovative': ['innovative', 'innovation', 'cutting-edge', 'cutting edge', 'state-of-the-art'],
            'collaborative': ['collaborative', 'team', 'teamwork', 'together', 'cooperation'],
            'flexible': ['flexible', 'flexibility', 'work-life balance', 'remote', 'hybrid'],
            'growth-oriented': ['growth', 'learning', 'development', 'career', 'opportunity']
        }
        
        # Check for indicators in description
        found_indicators = []
        for culture, keywords in culture_indicators.items():
            if any(keyword in description.lower() for keyword in keywords):
                found_indicators.append(culture)
        
        if found_indicators:
            return f"{company} appears to have a {', '.join(found_indicators)} culture based on the job description."
        else:
            return f"No specific culture indicators found for {company}."
    
    def _suggest_resume_focus(self, job_posting):
        """
        Suggest resume focus points based on job posting.
        
        Args:
            job_posting (dict): Job posting data
        
        Returns:
            list: Suggested resume focus points
        """
        suggestions = []
        
        # Extract key information
        job_skills = self._extract_skills(job_posting)
        job_title = job_posting.get('title', '')
        job_description = job_posting.get('description', '')
        
        # Suggest focusing on relevant skills
        if job_skills:
            suggestions.append(f"Highlight your experience with {', '.join(job_skills[:5])}.")
        
        # Suggest tailoring to job level
        job_level = self._determine_job_level(job_title, job_description)
        if job_level == 'Senior':
            suggestions.append("Emphasize leadership experience and strategic contributions.")
        elif job_level == 'Junior':
            suggestions.append("Focus on relevant education, internships, and eagerness to learn.")
        elif job_level == 'Management':
            suggestions.append("Highlight team management experience and business impact.")
        
        # Suggest focusing on specific achievements
        suggestions.append("Quantify achievements with specific metrics and outcomes.")
        
        # Suggest matching keywords
        suggestions.append("Include keywords from the job description in your resume.")
        
        return suggestions
    
    def _suggest_cover_letter_points(self, job_posting):
        """
        Suggest cover letter points based on job posting.
        
        Args:
            job_posting (dict): Job posting data
        
        Returns:
            list: Suggested cover letter points
        """
        suggestions = []
        
        # Extract key information
        company = job_posting.get('company', 'the company')
        job_title = job_posting.get('title', 'the position')
        
        # Suggest introduction
        suggestions.append(f"Express your interest in {job_title} at {company}.")
        
        # Suggest highlighting relevant experience
        suggestions.append("Connect your past experience directly to the job requirements.")
        
        # Suggest addressing company culture
        company_culture = self._analyze_company_culture(job_posting)
        if 'No specific culture indicators' not in company_culture:
            suggestions.append(f"Mention how you thrive in a {company_culture.split('appears to have a ')[1].split(' culture')[0]} environment.")
        
        # Suggest addressing specific requirements
        job_skills = self._extract_skills(job_posting)
        if job_skills:
            suggestions.append(f"Address how you've used {', '.join(job_skills[:3])} in previous roles.")
        
        # Suggest conclusion
        suggestions.append("Express enthusiasm for the opportunity to interview and discuss your qualifications further.")
        
        return suggestions
    
    def _calculate_overall_fit(self, user_profile, job_posting):
        """
        Calculate overall fit between user and job.
        
        Args:
            user_profile (dict): User profile data
            job_posting (dict): Job posting data
        
        Returns:
            str: Overall fit assessment
        """
        # Extract key information
        user_skills = self._extract_skills(user_profile)
        job_skills = self._extract_skills(job_posting)
        
        user_experience = self._extract_experience(user_profile)
        job_experience = job_posting.get('experience_required', '')
        
        user_education = self._extract_education(user_profile)
        job_education = job_posting.get('education_required', '')
        
        # Calculate match scores
        skill_match = self._calculate_skill_match(user_skills, job_skills)
        experience_match = self._calculate_experience_match(user_experience, job_experience)
        education_match = self._calculate_education_match(user_education, job_education)
        
        # Calculate overall score
        overall_score = (skill_match * 0.5) + (experience_match * 0.3) + (education_match * 0.2)
        
        # Determine fit level
        if overall_score >= 0.8:
            return "Strong fit - You meet or exceed most requirements for this position."
        elif overall_score >= 0.6:
            return "Good fit - You meet many requirements but may need to highlight transferable skills."
        elif overall_score >= 0.4:
            return "Moderate fit - You meet some requirements but have gaps in key areas."
        else:
            return "Limited fit - This position may require skills or experience you haven't demonstrated."
