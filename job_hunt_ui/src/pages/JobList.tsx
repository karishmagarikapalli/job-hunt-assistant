import React, { useState, useEffect } from 'react';
import { useJobs } from '../hooks/useJobs';
import { useAuth } from '../hooks/useAuth';
import { useAI } from '../hooks/useAI';
import { aiAPI } from '../lib/api';

// Components
import JobCard from '../components/JobCard';
import JobFilter from '../components/JobFilter';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorAlert from '../components/ErrorAlert';
import MatchScoreIndicator from '../components/MatchScoreIndicator';

const JobList = () => {
  const { user } = useAuth();
  const { jobs, loading: jobsLoading, error: jobsError, fetchJobs } = useJobs();
  const { matchJobs, loading: aiLoading, error: aiError } = useAI();
  
  const [matchedJobs, setMatchedJobs] = useState([]);
  const [filters, setFilters] = useState({
    keywords: '',
    location: '',
    jobType: 'full-time',
    requiresSponsorship: true,
    datePosted: 'any'
  });
  
  // Fetch jobs on component mount and when filters change
  useEffect(() => {
    fetchJobs(filters);
  }, [filters]);
  
  // Match jobs with user profile when jobs are loaded
  useEffect(() => {
    if (jobs.length > 0 && user) {
      handleMatchJobs();
    }
  }, [jobs, user]);
  
  const handleMatchJobs = async () => {
    try {
      const matches = await matchJobs(user, jobs);
      
      // Combine job data with match scores
      const enhancedJobs = jobs.map(job => {
        const match = matches.find(m => m.job_id === job.id) || { match_score: 0 };
        return {
          ...job,
          match_score: match.match_score,
          match_details: match.match_details
        };
      });
      
      // Sort by match score (highest first)
      enhancedJobs.sort((a, b) => b.match_score - a.match_score);
      
      setMatchedJobs(enhancedJobs);
    } catch (error) {
      console.error('Error matching jobs:', error);
    }
  };
  
  const handleFilterChange = (newFilters) => {
    setFilters({ ...filters, ...newFilters });
  };
  
  // Loading state
  if (jobsLoading || aiLoading) {
    return <LoadingSpinner message="Finding the perfect jobs for you..." />;
  }
  
  // Error state
  if (jobsError || aiError) {
    return <ErrorAlert message={jobsError || aiError} />;
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Job Opportunities</h1>
      
      <JobFilter filters={filters} onFilterChange={handleFilterChange} />
      
      <div className="mt-8">
        <p className="text-gray-600 mb-4">
          {matchedJobs.length} jobs found matching your criteria
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {matchedJobs.map(job => (
            <JobCard 
              key={job.id} 
              job={job}
              matchScore={job.match_score}
              matchDetails={job.match_details}
            />
          ))}
        </div>
        
        {matchedJobs.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No jobs found matching your criteria.</p>
            <p className="text-gray-500 mt-2">Try adjusting your filters or adding more skills to your profile.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobList;
