from flask import Blueprint, request, jsonify
from src.ai.job_matcher import JobMatcher
from src.ai.document_generator import DocumentGenerator
import os
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'logs', 'ai_api.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ai_api')

# Create blueprint
ai_bp = Blueprint('ai', __name__)

# Initialize AI modules
job_matcher = JobMatcher()
document_generator = DocumentGenerator()

@ai_bp.route('/match-jobs', methods=['POST'])
def match_jobs():
    """
    Match user profile with job postings.
    
    Request body:
    {
        "user_profile": {...},
        "job_postings": [...]
    }
    
    Returns:
    {
        "matches": [...]
    }
    """
    try:
        data = request.json
        
        if not data or 'user_profile' not in data or 'job_postings' not in data:
            return jsonify({'error': 'Invalid request data. Must include user_profile and job_postings.'}), 400
        
        user_profile = data['user_profile']
        job_postings = data['job_postings']
        
        matches = job_matcher.match_jobs(user_profile, job_postings)
        
        return jsonify({'matches': matches})
    except Exception as e:
        logger.error(f"Error in match_jobs: {str(e)}")
        return jsonify({'error': f"Error matching jobs: {str(e)}"}), 500

@ai_bp.route('/analyze-job', methods=['POST'])
def analyze_job():
    """
    Analyze a job posting for key requirements and insights.
    
    Request body:
    {
        "job_posting": {...},
        "user_profile": {...} (optional)
    }
    
    Returns:
    {
        "analysis": {...}
    }
    """
    try:
        data = request.json
        
        if not data or 'job_posting' not in data:
            return jsonify({'error': 'Invalid request data. Must include job_posting.'}), 400
        
        job_posting = data['job_posting']
        user_profile = data.get('user_profile')
        
        analysis = job_matcher.analyze_job(job_posting, user_profile)
        
        return jsonify({'analysis': analysis})
    except Exception as e:
        logger.error(f"Error in analyze_job: {str(e)}")
        return jsonify({'error': f"Error analyzing job: {str(e)}"}), 500

@ai_bp.route('/generate-resume', methods=['POST'])
def generate_resume():
    """
    Generate a resume based on user profile and job posting.
    
    Request body:
    {
        "user_profile": {...},
        "job_posting": {...} (optional),
        "template_id": "..." (optional),
        "output_format": "..." (optional, default: "html")
    }
    
    Returns:
    {
        "resume": {...}
    }
    """
    try:
        data = request.json
        
        if not data or 'user_profile' not in data:
            return jsonify({'error': 'Invalid request data. Must include user_profile.'}), 400
        
        user_profile = data['user_profile']
        job_posting = data.get('job_posting')
        template_id = data.get('template_id')
        output_format = data.get('output_format', 'html')
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'documents')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output path
        output_filename = f"resume_{user_profile.get('first_name', 'user')}_{user_profile.get('last_name', 'resume')}.{output_format}"
        output_path = os.path.join(output_dir, output_filename)
        
        # Generate resume
        resume = document_generator.generate_resume(
            user_profile=user_profile,
            job_posting=job_posting,
            template_id=template_id,
            output_format=output_format,
            output_path=output_path
        )
        
        # Add download URL
        if 'file_path' in resume:
            resume['download_url'] = f"/static/documents/{os.path.basename(resume['file_path'])}"
        
        return jsonify({'resume': resume})
    except Exception as e:
        logger.error(f"Error in generate_resume: {str(e)}")
        return jsonify({'error': f"Error generating resume: {str(e)}"}), 500

@ai_bp.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """
    Generate a cover letter based on user profile and job posting.
    
    Request body:
    {
        "user_profile": {...},
        "job_posting": {...},
        "template_id": "..." (optional),
        "output_format": "..." (optional, default: "html")
    }
    
    Returns:
    {
        "cover_letter": {...}
    }
    """
    try:
        data = request.json
        
        if not data or 'user_profile' not in data or 'job_posting' not in data:
            return jsonify({'error': 'Invalid request data. Must include user_profile and job_posting.'}), 400
        
        user_profile = data['user_profile']
        job_posting = data['job_posting']
        template_id = data.get('template_id')
        output_format = data.get('output_format', 'html')
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'documents')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output path
        output_filename = f"cover_letter_{user_profile.get('first_name', 'user')}_{user_profile.get('last_name', 'cover_letter')}.{output_format}"
        output_path = os.path.join(output_dir, output_filename)
        
        # Generate cover letter
        cover_letter = document_generator.generate_cover_letter(
            user_profile=user_profile,
            job_posting=job_posting,
            template_id=template_id,
            output_format=output_format,
            output_path=output_path
        )
        
        # Add download URL
        if 'file_path' in cover_letter:
            cover_letter['download_url'] = f"/static/documents/{os.path.basename(cover_letter['file_path'])}"
        
        return jsonify({'cover_letter': cover_letter})
    except Exception as e:
        logger.error(f"Error in generate_cover_letter: {str(e)}")
        return jsonify({'error': f"Error generating cover letter: {str(e)}"}), 500

@ai_bp.route('/get-resume-templates', methods=['GET'])
def get_resume_templates():
    """
    Get available resume templates.
    
    Returns:
    {
        "templates": [...]
    }
    """
    try:
        templates = document_generator.resume_templates
        
        # Convert to list of template info
        template_list = [
            {
                'id': template_id,
                'format': template_info['format'],
                'name': template_id.replace('_', ' ').title()
            }
            for template_id, template_info in templates.items()
        ]
        
        return jsonify({'templates': template_list})
    except Exception as e:
        logger.error(f"Error in get_resume_templates: {str(e)}")
        return jsonify({'error': f"Error getting resume templates: {str(e)}"}), 500

@ai_bp.route('/get-cover-letter-templates', methods=['GET'])
def get_cover_letter_templates():
    """
    Get available cover letter templates.
    
    Returns:
    {
        "templates": [...]
    }
    """
    try:
        templates = document_generator.cover_letter_templates
        
        # Convert to list of template info
        template_list = [
            {
                'id': template_id,
                'format': template_info['format'],
                'name': template_id.replace('_', ' ').title()
            }
            for template_id, template_info in templates.items()
        ]
        
        return jsonify({'templates': template_list})
    except Exception as e:
        logger.error(f"Error in get_cover_letter_templates: {str(e)}")
        return jsonify({'error': f"Error getting cover letter templates: {str(e)}"}), 500
