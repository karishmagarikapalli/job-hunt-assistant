from flask import Blueprint, request, jsonify
from functools import wraps
import os
import json

from src.models.document import db, Document
from src.routes.auth import token_required

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/resumes', methods=['GET'])
@token_required
def get_resumes(current_user):
    """Get all resumes for the current user"""
    resumes = Document.query.filter_by(
        user_id=current_user.id, 
        document_type='resume'
    ).order_by(Document.created_at.desc()).all()
    
    return jsonify({
        'resumes': [resume.to_dict() for resume in resumes],
        'count': len(resumes)
    }), 200

@documents_bp.route('/resumes/<int:resume_id>', methods=['GET'])
@token_required
def get_resume(current_user, resume_id):
    """Get resume by ID"""
    resume = Document.query.filter_by(
        id=resume_id,
        user_id=current_user.id,
        document_type='resume'
    ).first()
    
    if not resume:
        return jsonify({'message': 'Resume not found!'}), 404
    
    return jsonify({
        'resume': resume.to_dict()
    }), 200

@documents_bp.route('/resumes/generate', methods=['POST'])
@token_required
def generate_resume(current_user):
    """Generate a resume for a specific job"""
    data = request.get_json()
    
    # Validate required fields
    if not data or 'job_posting_id' not in data:
        return jsonify({'message': 'Job posting ID is required!'}), 400
    
    job_posting_id = data['job_posting_id']
    template = data.get('template', 'default')
    ai_optimize = data.get('ai_optimize', True)
    
    # This would normally trigger the document generation process
    # For now, we'll just create a placeholder document
    
    # Create document record
    resume = Document(
        user_id=current_user.id,
        document_type='resume',
        name=f"Resume for Job #{job_posting_id}",
        file_path=f"/resumes/user_{current_user.id}_job_{job_posting_id}.pdf",
        template_used=template,
        job_posting_id=job_posting_id,
        ai_optimized=ai_optimize
    )
    
    db.session.add(resume)
    db.session.commit()
    
    return jsonify({
        'message': 'Resume generation initiated!',
        'resume': resume.to_dict()
    }), 202

@documents_bp.route('/cover-letters', methods=['GET'])
@token_required
def get_cover_letters(current_user):
    """Get all cover letters for the current user"""
    cover_letters = Document.query.filter_by(
        user_id=current_user.id, 
        document_type='cover_letter'
    ).order_by(Document.created_at.desc()).all()
    
    return jsonify({
        'cover_letters': [cl.to_dict() for cl in cover_letters],
        'count': len(cover_letters)
    }), 200

@documents_bp.route('/cover-letters/<int:cover_letter_id>', methods=['GET'])
@token_required
def get_cover_letter(current_user, cover_letter_id):
    """Get cover letter by ID"""
    cover_letter = Document.query.filter_by(
        id=cover_letter_id,
        user_id=current_user.id,
        document_type='cover_letter'
    ).first()
    
    if not cover_letter:
        return jsonify({'message': 'Cover letter not found!'}), 404
    
    return jsonify({
        'cover_letter': cover_letter.to_dict()
    }), 200

@documents_bp.route('/cover-letters/generate', methods=['POST'])
@token_required
def generate_cover_letter(current_user):
    """Generate a cover letter for a specific job"""
    data = request.get_json()
    
    # Validate required fields
    if not data or 'job_posting_id' not in data:
        return jsonify({'message': 'Job posting ID is required!'}), 400
    
    job_posting_id = data['job_posting_id']
    template = data.get('template', 'default')
    ai_optimize = data.get('ai_optimize', True)
    
    # This would normally trigger the document generation process
    # For now, we'll just create a placeholder document
    
    # Create document record
    cover_letter = Document(
        user_id=current_user.id,
        document_type='cover_letter',
        name=f"Cover Letter for Job #{job_posting_id}",
        file_path=f"/cover_letters/user_{current_user.id}_job_{job_posting_id}.pdf",
        template_used=template,
        job_posting_id=job_posting_id,
        ai_optimized=ai_optimize
    )
    
    db.session.add(cover_letter)
    db.session.commit()
    
    return jsonify({
        'message': 'Cover letter generation initiated!',
        'cover_letter': cover_letter.to_dict()
    }), 202

@documents_bp.route('/templates', methods=['GET'])
@token_required
def get_templates(current_user):
    """Get available document templates"""
    document_type = request.args.get('type', 'all')
    
    # This would normally fetch templates from the filesystem or database
    # For now, we'll return placeholder data
    
    resume_templates = [
        {
            'id': 'professional',
            'name': 'Professional',
            'description': 'Clean and professional template suitable for corporate roles',
            'preview_url': '/static/templates/resume/professional.png'
        },
        {
            'id': 'creative',
            'name': 'Creative',
            'description': 'Modern and creative template for design and marketing roles',
            'preview_url': '/static/templates/resume/creative.png'
        },
        {
            'id': 'technical',
            'name': 'Technical',
            'description': 'Focused template highlighting technical skills for engineering roles',
            'preview_url': '/static/templates/resume/technical.png'
        }
    ]
    
    cover_letter_templates = [
        {
            'id': 'standard',
            'name': 'Standard',
            'description': 'Traditional cover letter format suitable for most roles',
            'preview_url': '/static/templates/cover_letter/standard.png'
        },
        {
            'id': 'modern',
            'name': 'Modern',
            'description': 'Contemporary design with a professional tone',
            'preview_url': '/static/templates/cover_letter/modern.png'
        },
        {
            'id': 'minimal',
            'name': 'Minimal',
            'description': 'Clean and concise format focusing on content',
            'preview_url': '/static/templates/cover_letter/minimal.png'
        }
    ]
    
    if document_type == 'resume':
        return jsonify({'templates': resume_templates}), 200
    elif document_type == 'cover_letter':
        return jsonify({'templates': cover_letter_templates}), 200
    else:
        return jsonify({
            'resume_templates': resume_templates,
            'cover_letter_templates': cover_letter_templates
        }), 200
