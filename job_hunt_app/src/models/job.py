from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class JobPosting(db.Model):
    """Job posting model for storing scraped job data"""
    __tablename__ = 'job_postings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    job_type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    application_url = db.Column(db.String(512), nullable=True)
    source_website = db.Column(db.String(100), nullable=True)
    date_posted = db.Column(db.String(50), nullable=True)
    date_scraped = db.Column(db.DateTime, default=datetime.utcnow)
    salary_range = db.Column(db.String(100), nullable=True)
    h1b_sponsorship = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='new')  # new, viewed, applied, rejected, saved
    match_score = db.Column(db.Float, default=0.0)  # AI-generated match score
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('JobApplication', backref='job_posting', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<JobPosting {self.title} at {self.company}>'
    
    def to_dict(self):
        """Convert job posting object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'job_type': self.job_type,
            'description': self.description,
            'application_url': self.application_url,
            'source_website': self.source_website,
            'date_posted': self.date_posted,
            'date_scraped': self.date_scraped.isoformat() if self.date_scraped else None,
            'salary_range': self.salary_range,
            'h1b_sponsorship': self.h1b_sponsorship,
            'status': self.status,
            'match_score': self.match_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class JobApplication(db.Model):
    """Job application model for tracking application status"""
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    resume_id = db.Column(db.Integer, nullable=True)
    cover_letter_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, submitted, interview, rejected, offer
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_status_change = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    automated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<JobApplication {self.id} for job {self.job_posting_id}>'
    
    def to_dict(self):
        """Convert job application object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_posting_id': self.job_posting_id,
            'resume_id': self.resume_id,
            'cover_letter_id': self.cover_letter_id,
            'status': self.status,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'last_status_change': self.last_status_change.isoformat() if self.last_status_change else None,
            'notes': self.notes,
            'automated': self.automated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
