import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useJobs } from '../hooks/useJobs';
import { useDocuments } from '../hooks/useDocuments';
import { useAI } from '../hooks/useAI';
import { useAuth } from '../hooks/useAuth';

// Components
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import JobDetailCard from '../components/JobDetailCard';
import MatchAnalysis from '../components/MatchAnalysis';
import DocumentGenerator from '../components/DocumentGenerator';
import ApplicationForm from '../components/ApplicationForm';

const JobDetail = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { getJob, loading: jobLoading, error: jobError } = useJobs();
  const { analyzeJob, loading: aiLoading, error: aiError } = useAI();
  const { resumes, coverLetters, loading: docLoading } = useDocuments();
  
  const [job, setJob] = useState(null);
  const [jobAnalysis, setJobAnalysis] = useState(null);
  const [activeTab, setActiveTab] = useState('details');
  
  // Fetch job details on component mount
  useEffect(() => {
    const fetchJobDetails = async () => {
      try {
        const jobData = await getJob(jobId);
        setJob(jobData);
        
        // Analyze job with AI
        if (jobData && user) {
          const analysis = await analyzeJob(jobData, user);
          setJobAnalysis(analysis);
        }
      } catch (error) {
        console.error('Error fetching job details:', error);
      }
    };
    
    fetchJobDetails();
  }, [jobId, user]);
  
  // Loading state
  if (jobLoading || aiLoading || docLoading) {
    return <LoadingSpinner message="Loading job details..." />;
  }
  
  // Error state
  if (jobError || aiError) {
    return <ErrorAlert message={jobError || aiError} />;
  }
  
  // No job found
  if (!job) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold mb-4">Job Not Found</h2>
        <p className="text-gray-600 mb-6">The job you're looking for doesn't exist or has been removed.</p>
        <button 
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
          onClick={() => navigate('/jobs')}
        >
          Back to Jobs
        </button>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <button 
          className="text-blue-500 hover:text-blue-700 flex items-center"
          onClick={() => navigate('/jobs')}
        >
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Jobs
        </button>
      </div>
      
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6">
          <h1 className="text-3xl font-bold mb-2">{job.title}</h1>
          <div className="text-gray-600 mb-4">{job.company} • {job.location}</div>
          
          {/* Tab navigation */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="flex -mb-px">
              <button
                className={`mr-8 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'details'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('details')}
              >
                Job Details
              </button>
              <button
                className={`mr-8 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'match'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('match')}
              >
                Match Analysis
              </button>
              <button
                className={`mr-8 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'documents'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('documents')}
              >
                Generate Documents
              </button>
              <button
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'apply'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setActiveTab('apply')}
              >
                Apply
              </button>
            </nav>
          </div>
          
          {/* Tab content */}
          <div className="py-4">
            {activeTab === 'details' && (
              <JobDetailCard job={job} />
            )}
            
            {activeTab === 'match' && (
              <MatchAnalysis 
                job={job} 
                analysis={jobAnalysis} 
                user={user} 
              />
            )}
            
            {activeTab === 'documents' && (
              <DocumentGenerator 
                job={job} 
                user={user} 
                existingResumes={resumes}
                existingCoverLetters={coverLetters}
              />
            )}
            
            {activeTab === 'apply' && (
              <ApplicationForm 
                job={job} 
                user={user} 
                resumes={resumes}
                coverLetters={coverLetters}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetail;
