import { useState, useEffect } from 'react';
import { jobsAPI } from '../lib/api';

// Define job types
export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  job_type: string;
  description: string;
  application_url: string;
  source_website: string;
  date_posted: string;
  date_scraped: string;
  salary_range: string;
  h1b_sponsorship: boolean;
  status: string;
  match_score: number;
  created_at: string;
  updated_at: string;
}

export interface JobFilters {
  status?: string;
  company?: string;
  title?: string;
  h1b_sponsorship?: boolean;
  min_score?: number;
}

export interface JobStats {
  total_jobs: number;
  status_counts: Record<string, number>;
  company_stats: Record<string, number>;
  source_stats: Record<string, number>;
  average_match_score: number;
}

// Custom hook for job management
export const useJobs = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [currentJob, setCurrentJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<JobStats | null>(null);
  const [filters, setFilters] = useState<JobFilters>({});

  // Fetch jobs with optional filters
  const fetchJobs = async (jobFilters?: JobFilters) => {
    setLoading(true);
    setError(null);
    try {
      const appliedFilters = jobFilters || filters;
      const response = await jobsAPI.getJobs(appliedFilters);
      setJobs(response.data.jobs);
      return response.data.jobs;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch jobs');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Fetch a single job by ID
  const fetchJob = async (jobId: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await jobsAPI.getJob(jobId);
      setCurrentJob(response.data.job);
      return response.data.job;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch job');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Trigger job scraping
  const scrapeJobs = async (params: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await jobsAPI.scrapeJobs(params);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to scrape jobs');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Update job status
  const updateJobStatus = async (jobId: number, status: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await jobsAPI.updateJobStatus(jobId, status);
      
      // Update job in local state
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId ? { ...job, status } : job
        )
      );
      
      if (currentJob && currentJob.id === jobId) {
        setCurrentJob({ ...currentJob, status });
      }
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to update job status');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Fetch job statistics
  const fetchJobStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await jobsAPI.getJobStats();
      setStats(response.data);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch job statistics');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Update filters and fetch jobs
  const applyFilters = async (newFilters: JobFilters) => {
    setFilters(newFilters);
    return fetchJobs(newFilters);
  };

  // Clear filters
  const clearFilters = () => {
    setFilters({});
    return fetchJobs({});
  };

  return {
    jobs,
    currentJob,
    loading,
    error,
    stats,
    filters,
    fetchJobs,
    fetchJob,
    scrapeJobs,
    updateJobStatus,
    fetchJobStats,
    applyFilters,
    clearFilters,
  };
};
