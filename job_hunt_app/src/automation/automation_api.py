import os
import logging
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from src.routes.auth import token_required
from src.models.job import db, JobPosting, JobApplication
from src.models.document import Document
from .application_manager import ApplicationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'automation_api.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('automation_api')

# Create Blueprint
automation_bp = Blueprint('automation', __name__)

# Global application manager instance
application_manager = None

@automation_bp.route('/status', methods=['GET'])
@token_required
def get_automation_status(current_user):
    """Get automation status"""
    global application_manager
    
    status = {
        'initialized': application_manager is not None,
        'stats': application_manager.get_stats() if application_manager else None
    }
    
    return jsonify(status), 200

@automation_bp.route('/initialize', methods=['POST'])
@token_required
def initialize_automation(current_user):
    """Initialize automation system"""
    global application_manager
    
    # Check if already initialized
    if application_manager:
        return jsonify({
            'message': 'Automation already initialized',
            'status': 'active'
        }), 200
    
    try:
        # Get configuration from request
        data = request.get_json() or {}
        config_path = data.get('config_path')
        
        # Create application manager
        application_manager = ApplicationManager(config_path)
        
        # Start automation
        success = application_manager.start()
        
        if success:
            return jsonify({
                'message': 'Automation initialized successfully',
                'status': 'active'
            }), 200
        else:
            application_manager = None
            return jsonify({
                'message': 'Failed to initialize automation',
                'status': 'error'
            }), 500
    except Exception as e:
        logger.error(f"Error initializing automation: {str(e)}")
        return jsonify({
            'message': f'Error initializing automation: {str(e)}',
            'status': 'error'
        }), 500

@automation_bp.route('/shutdown', methods=['POST'])
@token_required
def shutdown_automation(current_user):
    """Shutdown automation system"""
    global application_manager
    
    if not application_manager:
        return jsonify({
            'message': 'Automation not initialized',
            'status': 'inactive'
        }), 200
    
    try:
        # Stop automation
        success = application_manager.stop()
        
        if success:
            # Get stats before clearing
            stats = application_manager.get_stats()
            
            # Clear application manager
            application_manager = None
            
            return jsonify({
                'message': 'Automation shutdown successfully',
                'status': 'inactive',
                'stats': stats
            }), 200
        else:
            return jsonify({
                'message': 'Failed to shutdown automation',
                'status': 'error'
            }), 500
    except Exception as e:
        logger.error(f"Error shutting down automation: {str(e)}")
        return jsonify({
            'message': f'Error shutting down automation: {str(e)}',
            'status': 'error'
        }), 500

@automation_bp.route('/apply', methods=['POST'])
@token_required
def apply_to_job(current_user):
    """Apply to a job using automation"""
    global application_manager
    
    # Check if automation is initialized
    if not application_manager:
        return jsonify({
            'message': 'Automation not initialized',
            'status': 'error'
        }), 400
    
    # Get request data
    data = request.get_json()
    
    # Validate required fields
    if not data or 'job_id' not in data:
        return jsonify({
            'message': 'Job ID is required',
            'status': 'error'
        }), 400
    
    try:
        # Get job posting
        job_id = data['job_id']
        job_posting = JobPosting.query.get(job_id)
        
        if not job_posting:
            return jsonify({
                'message': f'Job posting with ID {job_id} not found',
                'status': 'error'
            }), 404
        
        # Get resume and cover letter
        resume_id = data.get('resume_id')
        cover_letter_id = data.get('cover_letter_id')
        
        if not resume_id:
            return jsonify({
                'message': 'Resume ID is required',
                'status': 'error'
            }), 400
        
        resume = Document.query.filter_by(id=resume_id, user_id=current_user.id, document_type='resume').first()
        
        if not resume:
            return jsonify({
                'message': f'Resume with ID {resume_id} not found',
                'status': 'error'
            }), 404
        
        cover_letter = None
        if cover_letter_id:
            cover_letter = Document.query.filter_by(id=cover_letter_id, user_id=current_user.id, document_type='cover_letter').first()
            
            if not cover_letter:
                return jsonify({
                    'message': f'Cover letter with ID {cover_letter_id} not found',
                    'status': 'error'
                }), 404
        
        # Prepare user data
        user_data = {
            'first_name': current_user.first_name or '',
            'last_name': current_user.last_name or '',
            'email': current_user.email,
            'phone': data.get('phone', ''),
            'linkedin_url': current_user.linkedin_url or '',
            'current_company': data.get('current_company', '')
        }
        
        # Prepare job data
        job_data = {
            'id': job_posting.id,
            'title': job_posting.title,
            'company': job_posting.company,
            'application_url': job_posting.application_url
        }
        
        # Apply to job
        result = application_manager.apply_to_job(
            job_data=job_data,
            user_data=user_data,
            resume_path=resume.file_path,
            cover_letter_path=cover_letter.file_path if cover_letter else None
        )
        
        # Create application record
        application = JobApplication(
            user_id=current_user.id,
            job_posting_id=job_posting.id,
            resume_id=resume_id,
            cover_letter_id=cover_letter_id,
            status='submitted' if result['success'] else 'failed',
            notes=json.dumps(result),
            automated=True
        )
        
        db.session.add(application)
        db.session.commit()
        
        # Update job status if successful
        if result['success']:
            job_posting.status = 'applied'
            db.session.commit()
        
        return jsonify({
            'message': 'Application submitted successfully' if result['success'] else 'Application failed',
            'status': 'success' if result['success'] else 'error',
            'application_id': application.id,
            'result': result
        }), 200 if result['success'] else 500
    except Exception as e:
        logger.error(f"Error applying to job: {str(e)}")
        return jsonify({
            'message': f'Error applying to job: {str(e)}',
            'status': 'error'
        }), 500

@automation_bp.route('/batch-apply', methods=['POST'])
@token_required
def batch_apply_to_jobs(current_user):
    """Apply to multiple jobs using automation"""
    global application_manager
    
    # Check if automation is initialized
    if not application_manager:
        return jsonify({
            'message': 'Automation not initialized',
            'status': 'error'
        }), 400
    
    # Get request data
    data = request.get_json()
    
    # Validate required fields
    if not data or 'job_ids' not in data or not data['job_ids']:
        return jsonify({
            'message': 'Job IDs are required',
            'status': 'error'
        }), 400
    
    if 'resume_id' not in data:
        return jsonify({
            'message': 'Resume ID is required',
            'status': 'error'
        }), 400
    
    try:
        job_ids = data['job_ids']
        resume_id = data['resume_id']
        cover_letter_id = data.get('cover_letter_id')
        
        # Verify resume exists
        resume = Document.query.filter_by(id=resume_id, user_id=current_user.id, document_type='resume').first()
        
        if not resume:
            return jsonify({
                'message': f'Resume with ID {resume_id} not found',
                'status': 'error'
            }), 404
        
        # Verify cover letter if provided
        cover_letter = None
        if cover_letter_id:
            cover_letter = Document.query.filter_by(id=cover_letter_id, user_id=current_user.id, document_type='cover_letter').first()
            
            if not cover_letter:
                return jsonify({
                    'message': f'Cover letter with ID {cover_letter_id} not found',
                    'status': 'error'
                }), 404
        
        # Prepare user data
        user_data = {
            'first_name': current_user.first_name or '',
            'last_name': current_user.last_name or '',
            'email': current_user.email,
            'phone': data.get('phone', ''),
            'linkedin_url': current_user.linkedin_url or '',
            'current_company': data.get('current_company', '')
        }
        
        # Process jobs in batch
        results = []
        for job_id in job_ids:
            # Get job posting
            job_posting = JobPosting.query.get(job_id)
            
            if not job_posting:
                results.append({
                    'job_id': job_id,
                    'success': False,
                    'message': f'Job posting with ID {job_id} not found'
                })
                continue
            
            # Prepare job data
            job_data = {
                'id': job_posting.id,
                'title': job_posting.title,
                'company': job_posting.company,
                'application_url': job_posting.application_url
            }
            
            # Apply to job
            result = application_manager.apply_to_job(
                job_data=job_data,
                user_data=user_data,
                resume_path=resume.file_path,
                cover_letter_path=cover_letter.file_path if cover_letter else None
            )
            
            # Create application record
            application = JobApplication(
                user_id=current_user.id,
                job_posting_id=job_posting.id,
                resume_id=resume_id,
                cover_letter_id=cover_letter_id,
                status='submitted' if result['success'] else 'failed',
                notes=json.dumps(result),
                automated=True
            )
            
            db.session.add(application)
            
            # Update job status if successful
            if result['success']:
                job_posting.status = 'applied'
            
            # Add to results
            results.append({
                'job_id': job_id,
                'success': result['success'],
                'application_id': application.id,
                'message': 'Application submitted successfully' if result['success'] else 'Application failed',
                'details': result
            })
        
        # Commit all changes
        db.session.commit()
        
        # Calculate summary
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        return jsonify({
            'message': f'Batch application completed: {successful} successful, {failed} failed',
            'status': 'success',
            'results': results,
            'summary': {
                'total': len(results),
                'successful': successful,
                'failed': failed
            }
        }), 200
    except Exception as e:
        logger.error(f"Error in batch application: {str(e)}")
        return jsonify({
            'message': f'Error in batch application: {str(e)}',
            'status': 'error'
        }), 500
