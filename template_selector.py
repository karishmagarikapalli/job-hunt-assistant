import json
import os
import sqlite3
from datetime import datetime
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TemplateSelector:
    """
    A class to intelligently select the best resume and cover letter templates
    based on job posting details.
    """
    
    def __init__(self, db_path='/home/ubuntu/job_hunt_ecosystem/job_hunt.db',
                 templates_dir='/home/ubuntu/job_hunt_ecosystem/templates'):
        """
        Initialize the template selector.
        
        Args:
            db_path: Path to the SQLite database
            templates_dir: Directory containing templates
        """
        self.db_path = db_path
        self.templates_dir = templates_dir
        
        # Ensure templates directory exists
        os.makedirs(os.path.join(templates_dir, 'resume'), exist_ok=True)
        os.makedirs(os.path.join(templates_dir, 'cover_letter'), exist_ok=True)
        
        # Download NLTK resources if not already downloaded
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        # Load template metadata
        self.resume_templates = self._load_template_metadata('resume')
        self.cover_letter_templates = self._load_template_metadata('cover_letter')
    
    def connect_db(self):
        """Connect to the SQLite database and return connection and cursor."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        return conn, cursor
    
    def _load_template_metadata(self, template_type):
        """
        Load template metadata from JSON files.
        
        Args:
            template_type: Type of template ('resume' or 'cover_letter')
            
        Returns:
            List of template metadata dictionaries
        """
        templates = []
        template_dir = os.path.join(self.templates_dir, template_type)
        
        if not os.path.exists(template_dir):
            print(f"Template directory not found: {template_dir}")
            return templates
        
        # Look for metadata files
        for filename in os.listdir(template_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(template_dir, filename), 'r') as f:
                        metadata = json.load(f)
                        
                        # Ensure template file exists
                        template_file = os.path.join(template_dir, metadata.get('filename', ''))
                        if os.path.exists(template_file):
                            templates.append(metadata)
                        else:
                            print(f"Template file not found: {template_file}")
                
                except Exception as e:
                    print(f"Error loading template metadata from {filename}: {str(e)}")
        
        return templates
    
    def select_best_template(self, job_id, template_type='resume'):
        """
        Select the best template for a job posting.
        
        Args:
            job_id: ID of the job posting
            template_type: Type of template ('resume' or 'cover_letter')
            
        Returns:
            Dictionary containing template metadata and filename
        """
        conn, cursor = self.connect_db()
        
        # Get job posting details
        cursor.execute('''
        SELECT * FROM job_postings WHERE id = ?
        ''', (job_id,))
        
        job = cursor.fetchone()
        
        if not job:
            print(f"No job found with ID {job_id}")
            conn.close()
            return None
        
        # Get available templates
        templates = self.resume_templates if template_type == 'resume' else self.cover_letter_templates
        
        if not templates:
            print(f"No {template_type} templates available")
            conn.close()
            return None
        
        # Extract job features for matching
        job_title = job['title'].lower() if job['title'] else ''
        job_description = job['description'].lower() if job['description'] else ''
        job_company = job['company'].lower() if job['company'] else ''
        
        # Combine job features
        job_text = f"{job_title} {job_description} {job_company}"
        
        # Calculate template scores
        template_scores = []
        
        for template in templates:
            score = 0
            
            # Check for industry match
            if 'industries' in template:
                for industry in template['industries']:
                    if industry.lower() in job_company or industry.lower() in job_description:
                        score += 10
            
            # Check for role match
            if 'roles' in template:
                for role in template['roles']:
                    if role.lower() in job_title:
                        score += 15
            
            # Check for keywords match
            if 'keywords' in template:
                for keyword in template['keywords']:
                    if keyword.lower() in job_text:
                        score += 5
            
            # Check for style match based on company
            if 'styles' in template:
                for style in template['styles']:
                    style_name = style.get('name', '').lower()
                    style_keywords = style.get('keywords', [])
                    
                    # Check if company name matches style
                    if style_name in job_company:
                        score += 8
                    
                    # Check if style keywords are in job description
                    for keyword in style_keywords:
                        if keyword.lower() in job_description:
                            score += 3
            
            # Add template with score
            template_scores.append((template, score))
        
        # Sort templates by score (descending)
        template_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get best template
        best_template = template_scores[0][0] if template_scores else None
        
        conn.close()
        
        if best_template:
            print(f"Selected {template_type} template: {best_template.get('name', 'Unknown')}")
            return best_template
        else:
            print(f"No suitable {template_type} template found")
            return None
    
    def analyze_job_posting(self, job_id):
        """
        Analyze a job posting to extract key information for template selection.
        
        Args:
            job_id: ID of the job posting
            
        Returns:
            Dictionary containing analysis results
        """
        conn, cursor = self.connect_db()
        
        # Get job posting details
        cursor.execute('''
        SELECT * FROM job_postings WHERE id = ?
        ''', (job_id,))
        
        job = cursor.fetchone()
        
        if not job:
            print(f"No job found with ID {job_id}")
            conn.close()
            return None
        
        # Extract job features
        job_title = job['title'] if job['title'] else ''
        job_description = job['description'] if job['description'] else ''
        job_company = job['company'] if job['company'] else ''
        
        # Analyze job description
        analysis = {
            'job_id': job_id,
            'title': job_title,
            'company': job_company,
            'keywords': [],
            'skills_mentioned': [],
            'industry': '',
            'formality_level': '',
            'template_recommendations': {
                'resume': '',
                'cover_letter': ''
            }
        }
        
        # Extract keywords using TF-IDF
        if job_description:
            # Tokenize and clean text
            stop_words = set(stopwords.words('english'))
            tokens = word_tokenize(job_description.lower())
            filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
            
            # Extract top keywords
            if filtered_tokens:
                vectorizer = TfidfVectorizer(max_features=20)
                tfidf_matrix = vectorizer.fit_transform([' '.join(filtered_tokens)])
                feature_names = vectorizer.get_feature_names_out()
                
                # Get top keywords
                tfidf_scores = zip(feature_names, tfidf_matrix.toarray()[0])
                sorted_scores = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
                
                analysis['keywords'] = [keyword for keyword, score in sorted_scores[:10]]
        
        # Extract skills mentioned
        common_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue', 
            'Node.js', 'Express', 'Django', 'Flask', 'Spring', 'AWS', 'Azure', 'GCP',
            'Docker', 'Kubernetes', 'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'MySQL',
            'HTML', 'CSS', 'Git', 'CI/CD', 'Jenkins', 'Terraform', 'Agile', 'Scrum',
            'REST', 'API', 'GraphQL', 'Redux', 'Microservices', 'DevOps', 'Linux',
            'C#', 'C++', '.NET', 'Ruby', 'Rails', 'PHP', 'Laravel', 'Swift', 'Kotlin',
            'TensorFlow', 'PyTorch', 'Machine Learning', 'AI', 'Data Science',
            'Hadoop', 'Spark', 'Kafka', 'Elasticsearch', 'Redis', 'RabbitMQ',
            'Communication', 'Leadership', 'Teamwork', 'Problem Solving', 'Critical Thinking'
        ]
        
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', job_description, re.IGNORECASE):
                analysis['skills_mentioned'].append(skill)
        
        # Determine industry
        tech_industries = {
            'Finance': ['bank', 'finance', 'financial', 'investment', 'trading', 'fintech'],
            'Healthcare': ['health', 'medical', 'hospital', 'patient', 'clinical', 'healthcare'],
            'E-commerce': ['retail', 'e-commerce', 'ecommerce', 'shop', 'marketplace'],
            'Enterprise': ['enterprise', 'business', 'corporate', 'solution', 'b2b'],
            'Startup': ['startup', 'start-up', 'seed', 'venture', 'disrupt', 'innovative'],
            'Education': ['education', 'learning', 'teaching', 'school', 'university', 'academic'],
            'Gaming': ['game', 'gaming', 'entertainment', 'interactive'],
            'Media': ['media', 'news', 'content', 'publishing', 'broadcast'],
            'Government': ['government', 'public', 'federal', 'state', 'agency'],
            'Consulting': ['consulting', 'consultant', 'advisory', 'professional services']
        }
        
        industry_scores = {}
        for industry, keywords in tech_industries.items():
            score = 0
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', job_description.lower(), re.IGNORECASE):
                    score += 1
                if re.search(r'\b' + re.escape(keyword) + r'\b', job_company.lower(), re.IGNORECASE):
                    score += 2
            
            if score > 0:
                industry_scores[industry] = score
        
        if industry_scores:
            analysis['industry'] = max(industry_scores.items(), key=lambda x: x[1])[0]
        
        # Determine formality level
        formal_keywords = ['formal', 'professional', 'corporate', 'enterprise', 'established']
        casual_keywords = ['casual', 'startup', 'creative', 'innovative', 'disruptive']
        
        formal_score = 0
        casual_score = 0
        
        for keyword in formal_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', job_description.lower(), re.IGNORECASE):
                formal_score += 1
            if re.search(r'\b' + re.escape(keyword) + r'\b', job_company.lower(), re.IGNORECASE):
                formal_score += 1
        
        for keyword in casual_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', job_description.lower(), re.IGNORECASE):
                casual_score += 1
            if re.search(r'\b' + re.escape(keyword) + r'\b', job_company.lower(), re.IGNORECASE):
                casual_score += 1
        
        if formal_score > casual_score:
            analysis['formality_level'] = 'Formal'
        elif casual_score > formal_score:
            analysis['formality_level'] = 'Casual'
        else:
            analysis['formality_level'] = 'Balanced'
        
        # Select best templates
        resume_template = self.select_best_template(job_id, 'resume')
        cover_letter_template = self.select_best_template(job_id, 'cover_letter')
        
        if resume_template:
            analysis['template_recommendations']['resume'] = resume_template.get('name', '')
        
        if cover_letter_template:
            analysis['template_recommendations']['cover_letter'] = cover_letter_template.get('name', '')
        
        conn.close()
        
        return analysis
    
    def create_template_metadata(self, template_type='resume'):
        """
        Create template metadata for all templates in the directory.
        
        Args:
            template_type: Type of template ('resume' or 'cover_letter')
            
        Returns:
            Number of metadata files created
        """
        template_dir = os.path.join(self.templates_dir, template_type)
        
        if not os.path.exists(template_dir):
            print(f"Template directory not found: {template_dir}")
            return 0
        
        count = 0
        
        # Look for template files
        for filename in os.listdir(template_dir):
            if filename.endswith('.html'):
                # Check if metadata file already exists
                metadata_file = os.path.join(template_dir, filename.replace('.html', '.json'))
                
                if not os.path.exists(metadata_file):
                    # Create metadata
                    template_name = filename.replace('.html', '').replace('_', ' ').title()
                    
                    metadata = {
                        'name': template_name,
                        'filename': filename,
                        'description': f"{template_name} template for {template_type}",
                        'industries': [],
                        'roles': [],
                        'keywords': [],
                        'styles': [
                            {
                                'name': 'Professional',
                                'keywords': ['professional', 'formal', 'corporate']
                            }
                        ],
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Write metadata to file
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=4)
                    
                    count += 1
                    print(f"Created metadata for {filename}")
        
        return count

# Example usage
if __name__ == "__main__":
    selector = TemplateSelector()
    
    # Create template metadata if needed
    selector.create_template_metadata('resume')
    selector.create_template_metadata('cover_letter')
    
    # Test template selection
    job_id = 1  # Replace with actual job ID
    resume_template = selector.select_best_template(job_id, 'resume')
    cover_letter_template = selector.select_best_template(job_id, 'cover_letter')
    
    # Analyze job posting
    analysis = selector.analyze_job_posting(job_id)
    
    if analysis:
        print(f"Job Analysis: {json.dumps(analysis, indent=4)}")
