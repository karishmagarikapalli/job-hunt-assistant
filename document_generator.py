import json
import os
import sqlite3
from datetime import datetime
import re
from jinja2 import Template, Environment, FileSystemLoader
import weasyprint

class DocumentGenerator:
    """
    A class to generate customized resumes and cover letters based on job descriptions
    and user information.
    """
    
    def __init__(self, db_path='/home/ubuntu/job_hunt_ecosystem/job_hunt.db',
                 templates_dir='/home/ubuntu/job_hunt_ecosystem/templates',
                 resume_config_path='/home/ubuntu/job_hunt_ecosystem/config/resume_config.json',
                 cover_letter_config_path='/home/ubuntu/job_hunt_ecosystem/config/cover_letter_config.json'):
        """
        Initialize the document generator with paths to database, templates, and configurations.
        
        Args:
            db_path: Path to the SQLite database
            templates_dir: Directory containing HTML templates
            resume_config_path: Path to resume configuration file
            cover_letter_config_path: Path to cover letter configuration file
        """
        self.db_path = db_path
        self.templates_dir = templates_dir
        
        # Create templates directory if it doesn't exist
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        
        # Load configurations
        with open(resume_config_path, 'r') as f:
            self.resume_config = json.load(f)
        
        with open(cover_letter_config_path, 'r') as f:
            self.cover_letter_config = json.load(f)
        
        # Initialize Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
        # Create default templates if they don't exist
        self.create_default_templates()
    
    def connect_db(self):
        """Connect to the SQLite database and return connection and cursor."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        return conn, cursor
    
    def create_default_templates(self):
        """Create default HTML templates for resumes and cover letters if they don't exist."""
        # Create professional resume template
        professional_resume = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ user.first_name }} {{ user.last_name }} - Resume</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            font-size: 12px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
            color: #2c3e50;
        }
        .contact-info {
            text-align: center;
            margin-bottom: 20px;
            font-size: 11px;
        }
        .section {
            margin-bottom: 20px;
        }
        .section-title {
            font-size: 16px;
            font-weight: bold;
            border-bottom: 1px solid #2c3e50;
            color: #2c3e50;
            padding-bottom: 5px;
            margin-bottom: 10px;
        }
        .experience-item, .education-item, .project-item {
            margin-bottom: 15px;
        }
        .item-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }
        .item-title {
            font-weight: bold;
        }
        .item-subtitle {
            font-style: italic;
        }
        .item-date {
            color: #7f8c8d;
        }
        .skills-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .skill-category {
            margin-bottom: 10px;
        }
        .skill-category-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .skill-item {
            background-color: #f0f0f0;
            padding: 3px 8px;
            border-radius: 3px;
            display: inline-block;
            margin-right: 5px;
            margin-bottom: 5px;
        }
        ul {
            padding-left: 20px;
            margin: 5px 0;
        }
        li {
            margin-bottom: 3px;
        }
        .summary {
            margin-bottom: 20px;
            text-align: justify;
        }
        @media print {
            body {
                font-size: 12px;
            }
            .container {
                padding: 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ user.first_name }} {{ user.last_name }}</h1>
            <div class="item-subtitle">{{ user.headline }}</div>
        </div>
        
        <div class="contact-info">
            {% if user.email %}{{ user.email }}{% endif %}
            {% if user.email and user.phone %} | {% endif %}
            {% if user.phone %}{{ user.phone }}{% endif %}
            {% if (user.email or user.phone) and user.location %} | {% endif %}
            {% if user.location %}{{ user.location }}{% endif %}
            {% if (user.email or user.phone or user.location) and user.linkedin_url %} | {% endif %}
            {% if user.linkedin_url %}<a href="{{ user.linkedin_url }}">LinkedIn</a>{% endif %}
            {% if (user.email or user.phone or user.location or user.linkedin_url) and user.github_url %} | {% endif %}
            {% if user.github_url %}<a href="{{ user.github_url }}">GitHub</a>{% endif %}
            {% if user.visa_status %} | {{ user.visa_status }}{% endif %}
        </div>
        
        {% if user.summary %}
        <div class="section">
            <div class="section-title">SUMMARY</div>
            <div class="summary">{{ user.summary }}</div>
        </div>
        {% endif %}
        
        {% if user.experience %}
        <div class="section">
            <div class="section-title">EXPERIENCE</div>
            {% for exp in user.experience %}
            <div class="experience-item">
                <div class="item-header">
                    <div class="item-title">{{ exp.title }}</div>
                    <div class="item-date">{{ exp.start_date }} - {{ exp.end_date }}</div>
                </div>
                <div class="item-subtitle">{{ exp.company }}{% if exp.location %}, {{ exp.location }}{% endif %}</div>
                {% if exp.description %}
                <div class="item-description">{{ exp.description }}</div>
                {% endif %}
                {% if exp.achievements %}
                <ul>
                    {% for achievement in exp.achievements %}
                    <li>{{ achievement }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
                {% if exp.technologies %}
                <div><em>Technologies: {{ exp.technologies|join(", ") }}</em></div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if user.education %}
        <div class="section">
            <div class="section-title">EDUCATION</div>
            {% for edu in user.education %}
            <div class="education-item">
                <div class="item-header">
                    <div class="item-title">{{ edu.degree }}{% if edu.field_of_study %} in {{ edu.field_of_study }}{% endif %}</div>
                    <div class="item-date">{{ edu.start_date }} - {{ edu.end_date }}</div>
                </div>
                <div class="item-subtitle">{{ edu.institution }}{% if edu.location %}, {{ edu.location }}{% endif %}</div>
                {% if edu.gpa %}<div>GPA: {{ edu.gpa }}</div>{% endif %}
                {% if edu.description %}<div>{{ edu.description }}</div>{% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if user.skills %}
        <div class="section">
            <div class="section-title">SKILLS</div>
            {% if user.skills.technical %}
            <div class="skill-category">
                <div class="skill-category-title">Technical Skills:</div>
                <div class="skills-list">
                    {% for skill in user.skills.technical %}
                    <div class="skill-item">{{ skill }}</div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if user.skills.soft %}
            <div class="skill-category">
                <div class="skill-category-title">Soft Skills:</div>
                <div class="skills-list">
                    {% for skill in user.skills.soft %}
                    <div class="skill-item">{{ skill }}</div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if user.skills.languages %}
            <div class="skill-category">
                <div class="skill-category-title">Languages:</div>
                <div class="skills-list">
                    {% for language in user.skills.languages %}
                    <div class="skill-item">{{ language }}</div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        {% if user.projects %}
        <div class="section">
            <div class="section-title">PROJECTS</div>
            {% for project in user.projects %}
            <div class="project-item">
                <div class="item-header">
                    <div class="item-title">{{ project.name }}</div>
                    {% if project.start_date or project.end_date %}
                    <div class="item-date">
                        {% if project.start_date %}{{ project.start_date }}{% endif %}
                        {% if project.start_date and project.end_date %} - {% endif %}
                        {% if project.end_date %}{{ project.end_date }}{% endif %}
                    </div>
                    {% endif %}
                </div>
                {% if project.description %}<div>{{ project.description }}</div>{% endif %}
                {% if project.highlights %}
                <ul>
                    {% for highlight in project.highlights %}
                    <li>{{ highlight }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
                {% if project.technologies %}
                <div><em>Technologies: {{ project.technologies|join(", ") }}</em></div>
                {% endif %}
                {% if project.url %}<div><a href="{{ project.url }}">{{ project.url }}</a></div>{% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if user.certifications %}
        <div class="section">
            <div class="section-title">CERTIFICATIONS</div>
            <ul>
                {% for cert in user.certifications %}
                <li>
                    <strong>{{ cert.name }}</strong> - {{ cert.issuing_organization }}
                    {% if cert.issue_date %} ({{ cert.issue_date }}{% if cert.expiration_date %} - {{ cert.expiration_date }}{% endif %}){% endif %}
                </li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""
        
        # Create standard cover letter template
        standard_cover_letter = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ user.first_name }} {{ user.last_name }} - Cover Letter</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            font-size: 12px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            margin-bottom: 30px;
        }
        .date {
            margin-bottom: 20px;
        }
        .recipient {
            margin-bottom: 20px;
        }
        .greeting {
            margin-bottom: 20px;
        }
        .content {
            margin-bottom: 20px;
            text-align: justify;
        }
        .closing {
            margin-bottom: 40px;
        }
        .signature {
            margin-bottom: 10px;
        }
        .contact-info {
            font-size: 11px;
        }
        @media print {
            body {
                font-size: 12px;
            }
            .container {
                padding: 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>{{ user.first_name }} {{ user.last_name }}</div>
            {% if user.email %}
            <div>{{ user.email }}</div>
            {% endif %}
            {% if user.phone %}
            <div>{{ user.phone }}</div>
            {% endif %}
            {% if user.location %}
            <div>{{ user.location }}</div>
            {% endif %}
        </div>
        
        <div class="date">{{ current_date }}</div>
        
        <div class="recipient">
            {% if job.hiring_manager %}
            <div>{{ job.hiring_manager }}</div>
            {% endif %}
            <div>{{ job.company }}</div>
            {% if job.company_address %}
            <div>{{ job.company_address }}</div>
            {% endif %}
        </div>
        
        <div class="greeting">
            {% if job.hiring_manager %}
            Dear {{ job.hiring_manager }},
            {% else %}
            Dear Hiring Manager,
            {% endif %}
        </div>
        
        <div class="content">
            <p>{{ introduction }}</p>
            
            <p>{{ body }}</p>
            
            <p>{{ skills_match }}</p>
            
            {% if company_connection %}
            <p>{{ company_connection }}</p>
            {% endif %}
            
            <p>{{ call_to_action }}</p>
        </div>
        
        <div class="closing">Sincerely,</div>
        
        <div class="signature">{{ user.first_name }} {{ user.last_name }}</div>
        
        <div class="contact-info">
            {% if user.email %}{{ user.email }}{% endif %}
            {% if user.email and user.phone %} | {% endif %}
            {% if user.phone %}{{ user.phone }}{% endif %}
            {% if (user.email or user.phone) and user.linkedin_url %} | {% endif %}
            {% if user.linkedin_url %}<a href="{{ user.linkedin_url }}">LinkedIn</a>{% endif %}
        </div>
    </div>
</body>
</html>
"""
        
        # Save templates if they don't exist
        professional_template_path = os.path.join(self.templates_dir, 'professional_template.html')
        if not os.path.exists(professional_template_path):
            with open(professional_template_path, 'w') as f:
                f.write(professional_resume)
        
        standard_cover_letter_path = os.path.join(self.templates_dir, 'standard_cover_letter.html')
        if not os.path.exists(standard_cover_letter_path):
            with open(standard_cover_letter_path, 'w') as f:
                f.write(standard_cover_letter)
    
    def get_user_data(self, user_id=1):
        """
        Retrieve user data from the database.
        
        Args:
            user_id: ID of the user to retrieve data for
            
        Returns:
            Dictionary containing user data
        """
        conn, cursor = self.connect_db()
        
        # Get personal info
        cursor.execute('''
        SELECT * FROM personal_info WHERE id = ?
        ''', (user_id,))
        personal_info = cursor.fetchone()
        
        if not personal_info:
            conn.close()
            raise ValueError(f"No user found with ID {user_id}")
        
        # Convert to dictionary
        user_data = dict(personal_info)
        
        # Get job preferences
        cursor.execute('''
        SELECT * FROM job_preferences WHERE user_id = ?
        ''', (user_id,))
        job_preferences = cursor.fetchone()
        
        if job_preferences:
            user_data['job_preferences'] = dict(job_preferences)
        
        # Get target roles
        cursor.execute('''
        SELECT role_name FROM target_roles WHERE user_id = ?
        ''', (user_id,))
        target_roles = [row[0] for row in cursor.fetchall()]
        
        if target_roles:
            user_data['target_roles'] = target_roles
        
        # Get work experience
        cursor.execute('''
        SELECT * FROM work_experience WHERE user_id = ? ORDER BY start_date DESC
        ''', (user_id,))
        experiences = []
        
        for exp_row in cursor.fetchall():
            exp = dict(exp_row)
            
            # Get technologies for this experience
            cursor.execute('''
            SELECT technology FROM work_technologies WHERE experience_id = ?
            ''', (exp['id'],))
            technologies = [row[0] for row in cursor.fetchall()]
            
            if technologies:
                exp['technologies'] = technologies
            
            # Get achievements for this experience
            cursor.execute('''
            SELECT achievement FROM work_achievements WHERE experience_id = ?
            ''', (exp['id'],))
            achievements = [row[0] for row in cursor.fetchall()]
            
            if achievements:
                exp['achievements'] = achievements
            
            experiences.append(exp)
        
        if experiences:
            user_data['experience'] = experiences
        
        # Get education
        cursor.execute('''
        SELECT * FROM education WHERE user_id = ? ORDER BY start_date DESC
        ''', (user_id,))
        education = [dict(row) for row in cursor.fetchall()]
        
        if education:
            user_data['education'] = education
        
        # Get skills
        cursor.execute('''
        SELECT skill_name, skill_type, proficiency_level FROM skills WHERE user_id = ?
        ''', (user_id,))
        
        skills = {
            'technical': [],
            'soft': [],
            'language': []
        }
        
        for row in cursor.fetchall():
            skill_type = row[1]
            if skill_type in skills:
                skills[skill_type].append(row[0])
        
        if any(skills.values()):
            user_data['skills'] = skills
        
        # Get projects
        cursor.execute('''
        SELECT * FROM projects WHERE user_id = ? ORDER BY start_date DESC
        ''', (user_id,))
        projects = []
        
        for proj_row in cursor.fetchall():
            proj = dict(proj_row)
            
            # Get technologies for this project
            cursor.execute('''
            SELECT technology FROM project_technologies WHERE project_id = ?
            ''', (proj['id'],))
            technologies = [row[0] for row in cursor.fetchall()]
            
            if technologies:
                proj['technologies'] = technologies
            
            # Get highlights for this project
            cursor.execute('''
            SELECT highlight FROM project_highlights WHERE project_id = ?
            ''', (proj['id'],))
            highlights = [row[0] for row in cursor.fetchall()]
            
            if highlights:
                proj['highlights'] = highlights
            
            projects.append(proj)
        
        if projects:
            user_data['projects'] = projects
        
        # Get certifications
        cursor.execute('''
        SELECT * FROM certifications WHERE user_id = ? ORDER BY issue_date DESC
        ''', (user_id,))
        certifications = [dict(row) for row in cursor.fetchall()]
        
        if certifications:
            user_data['certifications'] = certifications
        
        # Get professional anecdotes
        cursor.execute('''
        SELECT * FROM professional_anecdotes WHERE user_id = ?
        ''', (user_id,))
        anecdotes = []
        
        for anec_row in cursor.fetchall():
            anec = dict(anec_row)
            
            # Get skills demonstrated in this anecdote
            cursor.execute('''
            SELECT skill FROM anecdote_skills WHERE anecdote_id = ?
            ''', (anec['id'],))
            skills_demonstrated = [row[0] for row in cursor.fetchall()]
            
            if skills_demonstrated:
                anec['skills_demonstrated'] = skills_demonstrated
            
            anecdotes.append(anec)
        
        if anecdotes:
            user_data['anecdotes'] = anecdotes
        
        conn.close()
        return user_data
    
    def get_job_data(self, job_id):
        """
        Retrieve job posting data from the database.
        
        Args:
            job_id: ID of the job posting to retrieve
            
        Returns:
            Dictionary containing job posting data
        """
        conn, cursor = self.connect_db()
        
        cursor.execute('''
        SELECT * FROM job_postings WHERE id = ?
        ''', (job_id,))
        
        job_data = cursor.fetchone()
        
        if not job_data:
            conn.close()
            raise ValueError(f"No job posting found with ID {job_id}")
        
        conn.close()
        return dict(job_data)
    
    def analyze_job_description(self, job_description):
        """
        Analyze job description to extract key requirements and skills.
        
        Args:
            job_description: Text of the job description
            
        Returns:
            Dictionary containing extracted information
        """
        # This is a simplified implementation
        # In a real implementation, you would use NLP techniques or AI to extract information
        
        analysis = {
            'skills': [],
            'years_experience': None,
            'education_level': None,
            'job_type': None,
            'keywords': []
        }
        
        # Extract skills (simplified approach)
        common_tech_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 
            'node.js', 'express', 'django', 'flask', 'spring', 'aws', 'azure', 'gcp',
            'docker', 'kubernetes', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql',
            'html', 'css', 'git', 'ci/cd', 'jenkins', 'terraform', 'agile', 'scrum'
        ]
        
        for skill in common_tech_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', job_description.lower()):
                analysis['skills'].append(skill)
        
        # Extract years of experience (simplified approach)
        experience_patterns = [
            r'(\d+)\+?\s*(?:years|yrs)(?:\s*of)?\s*experience',
            r'experience\s*(?:of)?\s*(\d+)\+?\s*(?:years|yrs)'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, job_description.lower())
            if match:
                analysis['years_experience'] = int(match.group(1))
                break
        
        # Extract education level (simplified approach)
        education_patterns = {
            "bachelor's": r"bachelor'?s|bs|b\.s\.|undergraduate",
            "master's": r"master'?s|ms|m\.s\.|graduate",
            "phd": r"phd|ph\.d\.|doctorate"
        }
        
        for level, pattern in education_patterns.items():
            if re.search(pattern, job_description.lower()):
                analysis['education_level'] = level
                break
        
        # Extract job type (simplified approach)
        job_types = {
            "full-time": r"full[ -]time|full time",
            "part-time": r"part[ -]time|part time",
            "contract": r"contract|contractor",
            "internship": r"internship|intern"
        }
        
        for job_type, pattern in job_types.items():
            if re.search(pattern, job_description.lower()):
                analysis['job_type'] = job_type
                break
        
        return analysis
    
    def match_skills(self, user_skills, job_skills):
        """
        Match user skills with job requirements.
        
        Args:
            user_skills: List of user's skills
            job_skills: List of skills required for the job
            
        Returns:
            Dictionary containing matching results
        """
        if not user_skills or not job_skills:
            return {
                'matching_skills': [],
                'missing_skills': job_skills if job_skills else [],
                'match_percentage': 0
            }
        
        # Convert to lowercase for case-insensitive matching
        user_skills_lower = [skill.lower() for skill in user_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Find matching skills
        matching_skills = [skill for skill in job_skills if skill.lower() in user_skills_lower]
        
        # Find missing skills
        missing_skills = [skill for skill in job_skills if skill.lower() not in user_skills_lower]
        
        # Calculate match percentage
        match_percentage = len(matching_skills) / len(job_skills) * 100 if job_skills else 0
        
        return {
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'match_percentage': match_percentage
        }
    
    def generate_resume(self, user_id=1, job_id=None, template_name=None, output_path=None):
        """
        Generate a customized resume based on user data and job description.
        
        Args:
            user_id: ID of the user
            job_id: ID of the job posting (optional)
            template_name: Name of the template to use (optional)
            output_path: Path to save the generated resume (optional)
            
        Returns:
            Path to the generated resume
        """
        # Get user data
        user_data = self.get_user_data(user_id)
        
        # Get job data if provided
        job_data = None
        job_analysis = None
        if job_id:
            job_data = self.get_job_data(job_id)
            job_analysis = self.analyze_job_description(job_data['description'])
        
        # Determine template to use
        if not template_name:
            template_name = self.resume_config['default_template']
        
        template_file = None
        for template in self.resume_config['templates']:
            if template['name'] == template_name:
                template_file = template['file']
                break
        
        if not template_file:
            template_file = 'professional_template.html'  # Default fallback
        
        # Load template
        template = self.env.get_template(template_file)
        
        # Customize resume based on job if provided
        if job_data and job_analysis:
            # Prioritize relevant skills
            if 'skills' in user_data and 'technical' in user_data['skills'] and job_analysis['skills']:
                # Move matching skills to the front of the list
                technical_skills = user_data['skills']['technical']
                for skill in job_analysis['skills']:
                    if skill.lower() in [s.lower() for s in technical_skills]:
                        # Move to front
                        technical_skills.remove(skill)
                        technical_skills.insert(0, skill)
            
            # Prioritize relevant experience
            if 'experience' in user_data and job_analysis['skills']:
                # Sort experiences based on relevance to job skills
                for exp in user_data['experience']:
                    exp['relevance_score'] = 0
                    if 'technologies' in exp:
                        for tech in exp['technologies']:
                            if tech.lower() in [s.lower() for s in job_analysis['skills']]:
                                exp['relevance_score'] += 1
                
                user_data['experience'].sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                
                # Remove the temporary relevance score
                for exp in user_data['experience']:
                    if 'relevance_score' in exp:
                        del exp['relevance_score']
        
        # Render template
        html_content = template.render(user=user_data, job=job_data)
        
        # Determine output path
        if not output_path:
            resume_dir = '/home/ubuntu/job_hunt_ecosystem/resumes'
            if not os.path.exists(resume_dir):
                os.makedirs(resume_dir)
            
            filename = f"{user_data['first_name']}_{user_data['last_name']}_Resume"
            if job_data:
                company_name = re.sub(r'[^\w\s-]', '', job_data['company']).strip()
                job_title = re.sub(r'[^\w\s-]', '', job_data['title']).strip()
                filename += f"_{company_name}_{job_title}"
            
            filename = filename.replace(' ', '_') + '.pdf'
            output_path = os.path.join(resume_dir, filename)
        
        # Generate PDF
        weasyprint.HTML(string=html_content).write_pdf(output_path)
        
        return output_path
    
    def generate_cover_letter(self, user_id=1, job_id=None, template_name=None, output_path=None):
        """
        Generate a customized cover letter based on user data and job description.
        
        Args:
            user_id: ID of the user
            job_id: ID of the job posting
            template_name: Name of the template to use (optional)
            output_path: Path to save the generated cover letter (optional)
            
        Returns:
            Path to the generated cover letter
        """
        if not job_id:
            raise ValueError("Job ID is required to generate a cover letter")
        
        # Get user data
        user_data = self.get_user_data(user_id)
        
        # Get job data
        job_data = self.get_job_data(job_id)
        job_analysis = self.analyze_job_description(job_data['description'])
        
        # Determine template to use
        if not template_name:
            template_name = self.cover_letter_config['default_template']
        
        template_file = None
        for template in self.cover_letter_config['templates']:
            if template['name'] == template_name:
                template_file = template['file']
                break
        
        if not template_file:
            template_file = 'standard_cover_letter.html'  # Default fallback
        
        # Load template
        template = self.env.get_template(template_file)
        
        # Extract user skills
        user_skills = []
        if 'skills' in user_data:
            if 'technical' in user_data['skills']:
                user_skills.extend(user_data['skills']['technical'])
            if 'soft' in user_data['skills']:
                user_skills.extend(user_data['skills']['soft'])
        
        # Match skills
        skill_match = self.match_skills(user_skills, job_analysis['skills'])
        
        # Generate cover letter sections
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Introduction paragraph
        introduction = f"I am writing to express my interest in the {job_data['title']} position at {job_data['company']}. With my background as a {user_data.get('headline', 'Software Developer')} and experience in {', '.join(skill_match['matching_skills'][:3]) if skill_match['matching_skills'] else 'software development'}, I am excited about the opportunity to contribute to your team."
        
        # Body paragraph - use experience and anecdotes
        body = "Throughout my career, I have developed a strong foundation in software development with a focus on delivering high-quality solutions. "
        
        if 'experience' in user_data and user_data['experience']:
            latest_exp = user_data['experience'][0]
            body += f"Most recently at {latest_exp['company']}, I {latest_exp['description'].split('.')[0] if 'description' in latest_exp and latest_exp['description'] else 'contributed to various projects'}. "
        
        if 'anecdotes' in user_data and user_data['anecdotes']:
            anecdote = user_data['anecdotes'][0]
            body += f"In a previous role, {anecdote['situation']} I was tasked with {anecdote['task']} I {anecdote['action']} which resulted in {anecdote['result']}"
        
        # Skills match paragraph
        skills_match = f"My technical expertise aligns well with your requirements, particularly in {', '.join(skill_match['matching_skills']) if skill_match['matching_skills'] else 'software development'}. "
        
        if skill_match['match_percentage'] > 70:
            skills_match += "I am confident that my skill set is an excellent match for this position. "
        else:
            skills_match += "I am eager to apply these skills to the challenges at your company. "
        
        if skill_match['missing_skills']:
            skills_match += f"I am also actively expanding my knowledge in {', '.join(skill_match['missing_skills'][:2])} to continuously grow as a professional."
        
        # Company connection
        company_connection = f"I am particularly drawn to {job_data['company']} because of its reputation for innovation and commitment to excellence. The opportunity to contribute to your projects and grow with your team is exciting."
        
        # Call to action
        call_to_action = "I would welcome the opportunity to discuss how my background and skills would be a good fit for this position. Thank you for considering my application. I look forward to the possibility of working with your team."
        
        # Render template
        html_content = template.render(
            user=user_data,
            job=job_data,
            current_date=current_date,
            introduction=introduction,
            body=body,
            skills_match=skills_match,
            company_connection=company_connection,
            call_to_action=call_to_action
        )
        
        # Determine output path
        if not output_path:
            cover_letter_dir = '/home/ubuntu/job_hunt_ecosystem/cover_letters'
            if not os.path.exists(cover_letter_dir):
                os.makedirs(cover_letter_dir)
            
            company_name = re.sub(r'[^\w\s-]', '', job_data['company']).strip()
            job_title = re.sub(r'[^\w\s-]', '', job_data['title']).strip()
            filename = f"{user_data['first_name']}_{user_data['last_name']}_CoverLetter_{company_name}_{job_title}.pdf"
            filename = filename.replace(' ', '_')
            output_path = os.path.join(cover_letter_dir, filename)
        
        # Generate PDF
        weasyprint.HTML(string=html_content).write_pdf(output_path)
        
        return output_path

# Example usage
if __name__ == "__main__":
    # Create a sample user in the database for testing
    def create_sample_user():
        conn = sqlite3.connect('/home/ubuntu/job_hunt_ecosystem/job_hunt.db')
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM personal_info WHERE first_name = ? AND last_name = ?', ('Karishma', 'G'))
        user = cursor.fetchone()
        
        if user:
            print(f"Sample user already exists with ID: {user[0]}")
            conn.close()
            return user[0]
        
        # Insert personal info
        cursor.execute('''
        INSERT INTO personal_info (
            first_name, last_name, email, phone, street_address, city, state, zip_code, country,
            linkedin_url, portfolio_url, github_url, visa_status, requires_sponsorship,
            authorized_to_work, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Karishma', 'G', 'karishma.g@example.com', '555-123-4567', '123 Main St', 'Dallas', 'TX', '75001', 'United States',
            'https://www.linkedin.com/in/karishma-garikapalli/', '', '', 'H1-B', True,
            True, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        user_id = cursor.lastrowid
        
        # Insert job preferences
        cursor.execute('''
        INSERT INTO job_preferences (
            user_id, remote_preference, min_salary, preferred_salary, willing_to_relocate,
            start_date_availability, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 'Hybrid', 120000, 150000, False,
            'Immediate', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        # Insert target roles
        for role in ['Sr. Fullstack Developer', 'Software Developer', 'Software Engineer']:
            cursor.execute('INSERT INTO target_roles (user_id, role_name) VALUES (?, ?)', (user_id, role))
        
        # Insert work experience
        cursor.execute('''
        INSERT INTO work_experience (
            user_id, company, title, location, start_date, end_date, description,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 'Republic Services', 'Sr. Fullstack Developer', 'Remote', '2025-05', 'Present',
            'Built a configurable RAG pipeline for an internal project.',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        exp_id = cursor.lastrowid
        
        # Insert technologies for this experience
        for tech in ['Python', 'React', 'Node.js', 'AWS', 'RAG', 'LLM']:
            cursor.execute('INSERT INTO work_technologies (experience_id, technology) VALUES (?, ?)', (exp_id, tech))
        
        # Insert skills
        for skill, skill_type in [
            ('Python', 'technical'), ('Java', 'technical'), ('JavaScript', 'technical'),
            ('React', 'technical'), ('Node.js', 'technical'), ('AWS', 'technical'),
            ('SQL', 'technical'), ('NoSQL', 'technical'), ('Git', 'technical'),
            ('Docker', 'technical'), ('Kubernetes', 'technical'), ('REST APIs', 'technical'),
            ('Communication', 'soft'), ('Problem Solving', 'soft'), ('Teamwork', 'soft'),
            ('English', 'language'), ('Hindi', 'language'), ('Telugu', 'language')
        ]:
            cursor.execute('''
            INSERT INTO skills (user_id, skill_name, skill_type, proficiency_level, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id, skill, skill_type, 'Advanced', 
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
        
        # Insert a professional anecdote
        cursor.execute('''
        INSERT INTO professional_anecdotes (
            user_id, title, situation, task, action, result, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 'Optimizing API Performance',
            'Our team was facing performance issues with a critical API that was causing slow response times for users.',
            'I was tasked with identifying the bottlenecks and optimizing the API to improve response times.',
            'I conducted a thorough analysis of the codebase, identified inefficient database queries, implemented caching strategies, and refactored the code to follow best practices.',
            'The API response time improved by 70%, significantly enhancing user experience and reducing server load.',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        conn.commit()
        conn.close()
        
        print(f"Sample user created with ID: {user_id}")
        return user_id
    
    # Create a sample job posting for testing
    def create_sample_job():
        conn = sqlite3.connect('/home/ubuntu/job_hunt_ecosystem/job_hunt.db')
        cursor = conn.cursor()
        
        # Check if job already exists
        cursor.execute('SELECT id FROM job_postings WHERE title = ? AND company = ?', 
                      ('Senior Full Stack Developer', 'Tech Innovations Inc.'))
        job = cursor.fetchone()
        
        if job:
            print(f"Sample job already exists with ID: {job[0]}")
            conn.close()
            return job[0]
        
        # Insert job posting
        cursor.execute('''
        INSERT INTO job_postings (
            title, company, location, job_type, description, requirements, salary_range,
            application_url, source_website, date_posted, date_scraped, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Senior Full Stack Developer', 'Tech Innovations Inc.', 'Remote, US', 'Full-time',
            '''
            Tech Innovations Inc. is seeking a Senior Full Stack Developer to join our growing team. 
            This role will be responsible for developing and maintaining web applications, 
            collaborating with cross-functional teams, and mentoring junior developers.
            
            We offer a competitive salary, comprehensive benefits, and the opportunity to work on 
            cutting-edge projects. This position offers H1B visa sponsorship for qualified candidates.
            ''',
            '''
            - 5+ years of experience in full stack development
            - Strong proficiency in React, Node.js, and Python
            - Experience with AWS cloud services
            - Knowledge of database design and optimization (SQL and NoSQL)
            - Bachelor's degree in Computer Science or related field
            - Excellent problem-solving and communication skills
            ''',
            '$120,000 - $150,000',
            'https://example.com/careers/senior-full-stack-developer',
            'Example Job Board',
            '2025-05-28',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'new',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"Sample job created with ID: {job_id}")
        return job_id
    
    # Create sample data and test document generation
    try:
        user_id = create_sample_user()
        job_id = create_sample_job()
        
        generator = DocumentGenerator()
        
        # Generate resume
        resume_path = generator.generate_resume(user_id, job_id)
        print(f"Resume generated: {resume_path}")
        
        # Generate cover letter
        cover_letter_path = generator.generate_cover_letter(user_id, job_id)
        print(f"Cover letter generated: {cover_letter_path}")
        
    except Exception as e:
        print(f"Error: {e}")
