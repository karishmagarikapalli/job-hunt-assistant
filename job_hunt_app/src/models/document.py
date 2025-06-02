from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Document(db.Model):
    """Document model for storing resumes and cover letters"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(20), nullable=False)  # resume, cover_letter
    name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    template_used = db.Column(db.String(100), nullable=True)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=True)
    ai_optimized = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='documents')
    job_posting = db.relationship('JobPosting', backref='documents')
    
    def __repr__(self):
        return f'<Document {self.name} ({self.document_type})>'
    
    def to_dict(self):
        """Convert document object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'document_type': self.document_type,
            'name': self.name,
            'file_path': self.file_path,
            'template_used': self.template_used,
            'job_posting_id': self.job_posting_id,
            'ai_optimized': self.ai_optimized,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AIModel(db.Model):
    """AI model tracking for job matching and document optimization"""
    __tablename__ = 'ai_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # job_matching, resume_optimization, cover_letter_generation
    version = db.Column(db.String(20), nullable=False)
    parameters = db.Column(db.Text, nullable=True)  # JSON string of model parameters
    performance_metrics = db.Column(db.Text, nullable=True)  # JSON string of performance metrics
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AIModel {self.name} v{self.version}>'
    
    def to_dict(self):
        """Convert AI model object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type,
            'version': self.version,
            'parameters': self.parameters,
            'performance_metrics': self.performance_metrics,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AIJobMatch(db.Model):
    """AI job matching results"""
    __tablename__ = 'ai_job_matches'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    ai_model_id = db.Column(db.Integer, db.ForeignKey('ai_models.id'), nullable=False)
    match_score = db.Column(db.Float, nullable=False)
    match_details = db.Column(db.Text, nullable=True)  # JSON string of match details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='job_matches')
    job_posting = db.relationship('JobPosting', backref='ai_matches')
    ai_model = db.relationship('AIModel', backref='job_matches')
    
    def __repr__(self):
        return f'<AIJobMatch User:{self.user_id} Job:{self.job_posting_id} Score:{self.match_score}>'
    
    def to_dict(self):
        """Convert AI job match object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_posting_id': self.job_posting_id,
            'ai_model_id': self.ai_model_id,
            'match_score': self.match_score,
            'match_details': self.match_details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
