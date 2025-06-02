import json
import os
import sqlite3
from datetime import datetime
import re

class LinkedInDataEnhancer:
    """
    A class to enhance user profile data using LinkedIn information.
    """
    
    def __init__(self, db_path='/home/ubuntu/job_hunt_ecosystem/job_hunt.db',
                 linkedin_data_path='/home/ubuntu/job_hunt_ecosystem/linkedin_profile_data.json'):
        """
        Initialize the LinkedIn data enhancer.
        
        Args:
            db_path: Path to the SQLite database
            linkedin_data_path: Path to the LinkedIn profile data JSON file
        """
        self.db_path = db_path
        self.linkedin_data_path = linkedin_data_path
        
        # Load LinkedIn data
        if os.path.exists(linkedin_data_path):
            with open(linkedin_data_path, 'r') as f:
                self.linkedin_data = json.load(f)
        else:
            self.linkedin_data = None
            print(f"LinkedIn data file not found at {linkedin_data_path}")
    
    def connect_db(self):
        """Connect to the SQLite database and return connection and cursor."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        return conn, cursor
    
    def enhance_user_profile(self, user_id=1):
        """
        Enhance user profile with LinkedIn data.
        
        Args:
            user_id: ID of the user to enhance
            
        Returns:
            Boolean indicating success
        """
        if not self.linkedin_data:
            print("No LinkedIn data available for enhancement")
            return False
        
        try:
            # Update personal info
            self.update_personal_info(user_id)
            
            # Update work experience
            self.update_work_experience(user_id)
            
            # Update education
            self.update_education(user_id)
            
            # Update skills
            self.update_skills(user_id)
            
            # Update languages
            self.update_languages(user_id)
            
            # Update certifications and courses
            self.update_certifications(user_id)
            
            print(f"Successfully enhanced user profile with LinkedIn data for user ID: {user_id}")
            return True
            
        except Exception as e:
            print(f"Error enhancing user profile: {str(e)}")
            return False
    
    def update_personal_info(self, user_id):
        """Update personal info with LinkedIn data."""
        conn, cursor = self.connect_db()
        
        # Get current personal info
        cursor.execute('SELECT * FROM personal_info WHERE id = ?', (user_id,))
        current_info = cursor.fetchone()
        
        if not current_info:
            print(f"No user found with ID {user_id}")
            conn.close()
            return
        
        # Extract LinkedIn personal info
        first_name = self.linkedin_data.get('firstName', current_info['first_name'])
        last_name = self.linkedin_data.get('lastName', current_info['last_name'])
        headline = self.linkedin_data.get('headline', '')
        summary = self.linkedin_data.get('summary', '')
        
        # Get location info
        location = ''
        if 'geo' in self.linkedin_data and 'full' in self.linkedin_data['geo']:
            location = self.linkedin_data['geo']['full']
        
        # Update personal info
        cursor.execute('''
        UPDATE personal_info SET
            first_name = ?,
            last_name = ?,
            linkedin_url = ?,
            updated_at = ?
        WHERE id = ?
        ''', (
            first_name,
            last_name,
            f"https://www.linkedin.com/in/{self.linkedin_data.get('username', '')}",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            user_id
        ))
        
        conn.commit()
        conn.close()
        
        print(f"Updated personal info for user ID: {user_id}")
    
    def update_work_experience(self, user_id):
        """Update work experience with LinkedIn data."""
        if 'position' not in self.linkedin_data:
            print("No work experience found in LinkedIn data")
            return
        
        conn, cursor = self.connect_db()
        
        # Clear existing work experience
        cursor.execute('DELETE FROM work_experience WHERE user_id = ?', (user_id,))
        
        # Add LinkedIn work experience
        for position in self.linkedin_data['position']:
            # Extract position details
            company = position.get('companyName', '')
            title = position.get('title', '')
            location = position.get('location', '')
            
            # Extract dates
            start_date = ''
            if 'start' in position and 'year' in position['start'] and position['start']['year'] > 0:
                start_year = position['start']['year']
                start_month = position['start']['month'] if 'month' in position['start'] and position['start']['month'] > 0 else 1
                start_date = f"{start_year}-{start_month:02d}"
            
            end_date = 'Present'
            if 'end' in position and 'year' in position['end'] and position['end']['year'] > 0:
                end_year = position['end']['year']
                end_month = position['end']['month'] if 'month' in position['end'] and position['end']['month'] > 0 else 12
                end_date = f"{end_year}-{end_month:02d}"
            
            # Extract description
            description = position.get('description', '')
            
            # Insert work experience
            cursor.execute('''
            INSERT INTO work_experience (
                user_id, company, title, location, start_date, end_date, description,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                company,
                title,
                location,
                start_date,
                end_date,
                description,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            experience_id = cursor.lastrowid
            
            # Extract technologies from description
            if description:
                # Common tech keywords to look for
                tech_keywords = [
                    'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue', 
                    'Node.js', 'Express', 'Django', 'Flask', 'Spring', 'AWS', 'Azure', 'GCP',
                    'Docker', 'Kubernetes', 'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'MySQL',
                    'HTML', 'CSS', 'Git', 'CI/CD', 'Jenkins', 'Terraform', 'Agile', 'Scrum',
                    'REST', 'API', 'GraphQL', 'Redux', 'Microservices', 'DevOps', 'Linux',
                    'C#', 'C++', '.NET', 'Ruby', 'Rails', 'PHP', 'Laravel', 'Swift', 'Kotlin',
                    'TensorFlow', 'PyTorch', 'Machine Learning', 'AI', 'Data Science',
                    'Hadoop', 'Spark', 'Kafka', 'Elasticsearch', 'Redis', 'RabbitMQ'
                ]
                
                for tech in tech_keywords:
                    if re.search(r'\b' + re.escape(tech) + r'\b', description, re.IGNORECASE):
                        cursor.execute('''
                        INSERT INTO work_technologies (experience_id, technology)
                        VALUES (?, ?)
                        ''', (experience_id, tech))
            
            # Extract achievements from description
            if description:
                # Split description into sentences
                sentences = re.split(r'(?<=[.!?])\s+', description)
                
                for sentence in sentences:
                    # Look for achievement indicators
                    if re.search(r'\b(led|improved|increased|decreased|reduced|achieved|implemented|developed|created|built|designed|launched|managed|delivered)\b', sentence, re.IGNORECASE):
                        if len(sentence) > 10:  # Ensure it's a substantial achievement
                            cursor.execute('''
                            INSERT INTO work_achievements (experience_id, achievement)
                            VALUES (?, ?)
                            ''', (experience_id, sentence.strip()))
        
        conn.commit()
        conn.close()
        
        print(f"Updated work experience for user ID: {user_id}")
    
    def update_education(self, user_id):
        """Update education with LinkedIn data."""
        if 'educations' not in self.linkedin_data:
            print("No education found in LinkedIn data")
            return
        
        conn, cursor = self.connect_db()
        
        # Clear existing education
        cursor.execute('DELETE FROM education WHERE user_id = ?', (user_id,))
        
        # Add LinkedIn education
        for edu in self.linkedin_data['educations']:
            # Extract education details
            institution = edu.get('schoolName', '')
            degree = edu.get('degree', '')
            field_of_study = edu.get('fieldOfStudy', '')
            
            # Extract location
            location = ''
            
            # Extract dates
            start_date = ''
            if 'start' in edu and 'year' in edu['start'] and edu['start']['year'] > 0:
                start_year = edu['start']['year']
                start_month = edu['start']['month'] if 'month' in edu['start'] and edu['start']['month'] > 0 else 1
                start_date = f"{start_year}-{start_month:02d}"
            
            end_date = ''
            if 'end' in edu and 'year' in edu['end'] and edu['end']['year'] > 0:
                end_year = edu['end']['year']
                end_month = edu['end']['month'] if 'month' in edu['end'] and edu['end']['month'] > 0 else 12
                end_date = f"{end_year}-{end_month:02d}"
            
            # Extract GPA and description
            gpa = edu.get('grade', '')
            description = edu.get('description', '')
            
            # Insert education
            cursor.execute('''
            INSERT INTO education (
                user_id, institution, degree, field_of_study, location, start_date, end_date,
                gpa, description, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                institution,
                degree,
                field_of_study,
                location,
                start_date,
                end_date,
                gpa,
                description,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
        
        conn.commit()
        conn.close()
        
        print(f"Updated education for user ID: {user_id}")
    
    def update_skills(self, user_id):
        """Update skills with LinkedIn data."""
        conn, cursor = self.connect_db()
        
        # Extract skills from LinkedIn summary and experience
        skills = set()
        
        # Extract from summary
        if 'summary' in self.linkedin_data:
            summary = self.linkedin_data['summary']
            
            # Look for skill section indicators
            skill_sections = re.findall(r'(?:Skills|Technologies|Tech Stack|Expertise)(?:\s*[-:]\s*|\s*:\s*|\s+)([^.]*)', summary, re.IGNORECASE)
            
            for section in skill_sections:
                # Split by commas, semicolons, or other separators
                section_skills = re.split(r'[,;|/]|\s+and\s+', section)
                for skill in section_skills:
                    skill = skill.strip()
                    if skill and len(skill) > 1:  # Ensure it's a substantial skill
                        skills.add(skill)
        
        # Common technical skills to look for
        tech_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue', 
            'Node.js', 'Express', 'Django', 'Flask', 'Spring', 'AWS', 'Azure', 'GCP',
            'Docker', 'Kubernetes', 'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'MySQL',
            'HTML', 'CSS', 'Git', 'CI/CD', 'Jenkins', 'Terraform', 'Agile', 'Scrum',
            'REST', 'API', 'GraphQL', 'Redux', 'Microservices', 'DevOps', 'Linux',
            'C#', 'C++', '.NET', 'Ruby', 'Rails', 'PHP', 'Laravel', 'Swift', 'Kotlin',
            'TensorFlow', 'PyTorch', 'Machine Learning', 'AI', 'Data Science',
            'Hadoop', 'Spark', 'Kafka', 'Elasticsearch', 'Redis', 'RabbitMQ'
        ]
        
        # Common soft skills
        soft_skills = [
            'Communication', 'Leadership', 'Teamwork', 'Problem Solving', 'Critical Thinking',
            'Time Management', 'Adaptability', 'Creativity', 'Collaboration', 'Presentation',
            'Project Management', 'Mentoring', 'Negotiation', 'Conflict Resolution',
            'Customer Service', 'Decision Making', 'Emotional Intelligence'
        ]
        
        # Clear existing skills
        cursor.execute('DELETE FROM skills WHERE user_id = ?', (user_id,))
        
        # Add technical skills
        for skill in tech_skills:
            if 'summary' in self.linkedin_data and re.search(r'\b' + re.escape(skill) + r'\b', self.linkedin_data['summary'], re.IGNORECASE):
                cursor.execute('''
                INSERT INTO skills (user_id, skill_name, skill_type, proficiency_level, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    skill,
                    'technical',
                    'Advanced',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
        
        # Add soft skills
        for skill in soft_skills:
            if 'summary' in self.linkedin_data and re.search(r'\b' + re.escape(skill) + r'\b', self.linkedin_data['summary'], re.IGNORECASE):
                cursor.execute('''
                INSERT INTO skills (user_id, skill_name, skill_type, proficiency_level, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    skill,
                    'soft',
                    'Advanced',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
        
        # Add extracted skills
        for skill in skills:
            # Determine if it's a technical or soft skill
            skill_type = 'technical'
            for soft_skill in soft_skills:
                if re.search(r'\b' + re.escape(soft_skill) + r'\b', skill, re.IGNORECASE):
                    skill_type = 'soft'
                    break
            
            cursor.execute('''
            INSERT INTO skills (user_id, skill_name, skill_type, proficiency_level, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                skill,
                skill_type,
                'Advanced',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
        
        conn.commit()
        conn.close()
        
        print(f"Updated skills for user ID: {user_id}")
    
    def update_languages(self, user_id):
        """Update languages with LinkedIn data."""
        if 'languages' not in self.linkedin_data:
            print("No languages found in LinkedIn data")
            return
        
        conn, cursor = self.connect_db()
        
        # Add LinkedIn languages as skills
        for language in self.linkedin_data['languages']:
            language_name = language.get('name', '')
            proficiency = language.get('proficiency', 'PROFESSIONAL_WORKING')
            
            # Map LinkedIn proficiency to our levels
            proficiency_map = {
                'NATIVE_OR_BILINGUAL': 'Native',
                'FULL_PROFESSIONAL': 'Fluent',
                'PROFESSIONAL_WORKING': 'Proficient',
                'LIMITED_WORKING': 'Intermediate',
                'ELEMENTARY': 'Basic'
            }
            
            proficiency_level = proficiency_map.get(proficiency, 'Proficient')
            
            # Insert language as skill
            cursor.execute('''
            INSERT INTO skills (user_id, skill_name, skill_type, proficiency_level, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                language_name,
                'language',
                proficiency_level,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
        
        conn.commit()
        conn.close()
        
        print(f"Updated languages for user ID: {user_id}")
    
    def update_certifications(self, user_id):
        """Update certifications with LinkedIn data."""
        conn, cursor = self.connect_db()
        
        # Clear existing certifications
        cursor.execute('DELETE FROM certifications WHERE user_id = ?', (user_id,))
        
        # Add LinkedIn certifications and courses
        if 'certifications' in self.linkedin_data:
            for cert in self.linkedin_data['certifications']:
                name = cert.get('name', '')
                issuing_organization = cert.get('authority', '')
                
                # Extract dates
                issue_date = ''
                if 'start' in cert and 'year' in cert['start'] and cert['start']['year'] > 0:
                    issue_year = cert['start']['year']
                    issue_month = cert['start']['month'] if 'month' in cert['start'] and cert['start']['month'] > 0 else 1
                    issue_date = f"{issue_year}-{issue_month:02d}"
                
                expiration_date = ''
                if 'end' in cert and 'year' in cert['end'] and cert['end']['year'] > 0:
                    exp_year = cert['end']['year']
                    exp_month = cert['end']['month'] if 'month' in cert['end'] and cert['end']['month'] > 0 else 12
                    expiration_date = f"{exp_year}-{exp_month:02d}"
                
                # Insert certification
                cursor.execute('''
                INSERT INTO certifications (
                    user_id, name, issuing_organization, issue_date, expiration_date,
                    credential_id, credential_url, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    name,
                    issuing_organization,
                    issue_date,
                    expiration_date,
                    '',  # credential_id
                    '',  # credential_url
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
        
        # Add courses as certifications
        if 'courses' in self.linkedin_data:
            for course in self.linkedin_data['courses']:
                name = course.get('name', '')
                issuing_organization = course.get('authority', '')
                
                # Extract dates
                issue_date = ''
                if 'start' in course and 'year' in course['start'] and course['start']['year'] > 0:
                    issue_year = course['start']['year']
                    issue_month = course['start']['month'] if 'month' in course['start'] and course['start']['month'] > 0 else 1
                    issue_date = f"{issue_year}-{issue_month:02d}"
                
                # Insert course as certification
                cursor.execute('''
                INSERT INTO certifications (
                    user_id, name, issuing_organization, issue_date, expiration_date,
                    credential_id, credential_url, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    name,
                    issuing_organization,
                    issue_date,
                    '',  # expiration_date
                    '',  # credential_id
                    '',  # credential_url
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
        
        conn.commit()
        conn.close()
        
        print(f"Updated certifications for user ID: {user_id}")

# Example usage
if __name__ == "__main__":
    enhancer = LinkedInDataEnhancer()
    enhancer.enhance_user_profile()
