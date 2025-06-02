import { useState } from 'react';
import { aiAPI } from '../lib/api';

// Define AI types
export interface AIModel {
  id: number;
  name: string;
  model_type: string;
  version: string;
  parameters: string;
  performance_metrics: string;
  created_at: string;
  updated_at: string;
}

export interface JobMatch {
  id: number;
  user_id: number;
  job_posting_id: number;
  ai_model_id: number;
  match_score: number;
  match_details: string;
  created_at: string;
}

export interface JobAnalysis {
  job_posting_id: number;
  key_skills: Array<{ skill: string; importance: number }>;
  required_experience: string;
  education_level: string;
  company_culture: string;
  job_level: string;
  keywords: string[];
  suggested_resume_focus: string[];
  suggested_cover_letter_points: string[];
}

// Custom hook for AI features
export const useAI = () => {
  const [models, setModels] = useState<AIModel[]>([]);
  const [jobMatches, setJobMatches] = useState<JobMatch[]>([]);
  const [jobAnalysis, setJobAnalysis] = useState<JobAnalysis | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Match jobs to user profile
  const matchJobs = async (params: { job_ids: number[]; model_id?: number }) => {
    setLoading(true);
    setError(null);
    try {
      const response = await aiAPI.matchJobs(params);
      setJobMatches(response.data.matches);
      return response.data.matches;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to match jobs');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Optimize resume for a specific job
  const optimizeResume = async (params: { job_posting_id: number; resume_id: number }) => {
    setLoading(true);
    setError(null);
    try {
      const response = await aiAPI.optimizeResume(params);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to optimize resume');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Generate a tailored cover letter
  const generateAICoverLetter = async (params: { 
    job_posting_id: number; 
    tone?: string;
    focus_points?: string[];
  }) => {
    setLoading(true);
    setError(null);
    try {
      const response = await aiAPI.generateCoverLetter(params);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to generate cover letter');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Analyze job description
  const analyzeJob = async (params: { job_posting_id: number }) => {
    setLoading(true);
    setError(null);
    try {
      const response = await aiAPI.analyzeJob(params);
      setJobAnalysis(response.data.analysis);
      return response.data.analysis;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to analyze job');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Get available AI models
  const getModels = async (type?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await aiAPI.getModels(type);
      setModels(response.data.models);
      return response.data.models;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to get AI models');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    models,
    jobMatches,
    jobAnalysis,
    loading,
    error,
    matchJobs,
    optimizeResume,
    generateAICoverLetter,
    analyzeJob,
    getModels
  };
};
