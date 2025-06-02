from flask import Blueprint, request, jsonify
from functools import wraps
import json

from src.models.job import db, JobPosting, JobApplication
from src.routes.auth import token_required

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/', methods=['GET'])
@token_required
def get_jobs(current_user):
    """Get all job postings with optional filtering"""
    # Get query parameters
    status = request.args.get('status')
    company = request.args.get('company')
    title = request.args.get('title')
    h1b = request.args.get('h1b_sponsorship')
    min_score = request.args.get('min_score')
    
    # Start with base query
    query = JobPosting.query
    
    # Apply filters
    if status:
        query = query.filter(JobPosting.status == status)
    
    if company:
        query = query.filter(JobPosting.company.ilike(f'%{company}%'))
    
    if title:
        query = query.filter(JobPosting.title.ilike(f'%{title}%'))
    
    if h1b:
        h1b_bool = h1b.lower() == 'true'
        query = query.filter(JobPosting.h1b_sponsorship == h1b_bool)
    
    if min_score:
        try:
            min_score_float = float(min_score)
            query = query.filter(JobPosting.match_score >= min_score_float)
        except ValueError:
            pass
    
    # Order by match score (descending) and date scraped (descending)
    jobs = query.order_by(JobPosting.match_score.desc(), JobPosting.date_scraped.desc()).all()
    
    return jsonify({
        'jobs': [job.to_dict() for job in jobs],
        'count': len(jobs)
    }), 200

@jobs_bp.route('/<int:job_id>', methods=['GET'])
@token_required
def get_job(current_user, job_id):
    """Get job posting by ID"""
    job = JobPosting.query.get(job_id)
    
    if not job:
        return jsonify({'message': 'Job not found!'}), 404
    
    return jsonify({
        'job': job.to_dict()
    }), 200

@jobs_bp.route('/scrape', methods=['POST'])
@token_required
def scrape_jobs(current_user):
    """Trigger job scraping"""
    data = request.get_json() or {}
    
    # Get scraping parameters
    search_terms = data.get('search_terms', [])
    locations = data.get('locations', [])
    job_boards = data.get('job_boards', [])
    companies = data.get('companies', [])
    
    # This would normally trigger an async job, but for now we'll just return a success message
    return jsonify({
        'message': 'Job scraping initiated!',
        'parameters': {
            'search_terms': search_terms,
            'locations': locations,
            'job_boards': job_boards,
            'companies': companies
        }
    }), 202

@jobs_bp.route('/<int:job_id>/status', methods=['PUT'])
@token_required
def update_job_status(current_user, job_id):
    """Update job status"""
    job = JobPosting.query.get(job_id)
    
    if not job:
        return jsonify({'message': 'Job not found!'}), 404
    
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({'message': 'Status is required!'}), 400
    
    # Validate status
    valid_statuses = ['new', 'viewed', 'applied', 'rejected', 'saved']
    if data['status'] not in valid_statuses:
        return jsonify({'message': f'Invalid status! Must be one of: {", ".join(valid_statuses)}'}), 400
    
    # Update status
    job.status = data['status']
    db.session.commit()
    
    return jsonify({
        'message': 'Job status updated successfully!',
        'job': job.to_dict()
    }), 200

@jobs_bp.route('/stats', methods=['GET'])
@token_required
def get_job_stats(current_user):
    """Get job statistics"""
    # Count jobs by status
    status_counts = {}
    for status in ['new', 'viewed', 'applied', 'rejected', 'saved']:
        count = JobPosting.query.filter_by(status=status).count()
        status_counts[status] = count
    
    # Count jobs by company (top 5)
    company_counts = db.session.query(
        JobPosting.company, db.func.count(JobPosting.id)
    ).group_by(JobPosting.company).order_by(db.func.count(JobPosting.id).desc()).limit(5).all()
    
    company_stats = {company: count for company, count in company_counts}
    
    # Count jobs by source website
    source_counts = db.session.query(
        JobPosting.source_website, db.func.count(JobPosting.id)
    ).group_by(JobPosting.source_website).all()
    
    source_stats = {source: count for source, count in source_counts if source}
    
    # Get average match score
    avg_score = db.session.query(db.func.avg(JobPosting.match_score)).scalar() or 0
    
    return jsonify({
        'total_jobs': JobPosting.query.count(),
        'status_counts': status_counts,
        'company_stats': company_stats,
        'source_stats': source_stats,
        'average_match_score': float(avg_score)
    }), 200

@jobs_bp.route('/<int:job_id>/applications', methods=['GET'])
@token_required
def get_job_applications(current_user, job_id):
    """Get applications for a specific job"""
    job = JobPosting.query.get(job_id)
    
    if not job:
        return jsonify({'message': 'Job not found!'}), 404
    
    applications = JobApplication.query.filter_by(job_posting_id=job_id, user_id=current_user.id).all()
    
    return jsonify({
        'applications': [app.to_dict() for app in applications],
        'count': len(applications)
    }), 200
