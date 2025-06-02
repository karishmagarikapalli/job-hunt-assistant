import { useState, useEffect } from 'react';
import { documentsAPI } from '../lib/api';

// Define document types
export interface Document {
  id: number;
  user_id: number;
  document_type: string;
  name: string;
  file_path: string;
  template_used: string;
  job_posting_id: number | null;
  ai_optimized: boolean;
  created_at: string;
  updated_at: string;
}

export interface Template {
  id: string;
  name: string;
  description: string;
  preview_url: string;
}

// Custom hook for document management
export const useDocuments = () => {
  const [resumes, setResumes] = useState<Document[]>([]);
  const [coverLetters, setCoverLetters] = useState<Document[]>([]);
  const [currentDocument, setCurrentDocument] = useState<Document | null>(null);
  const [templates, setTemplates] = useState<{
    resume_templates: Template[];
    cover_letter_templates: Template[];
  }>({
    resume_templates: [],
    cover_letter_templates: []
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch all resumes
  const fetchResumes = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await documentsAPI.getResumes();
      setResumes(response.data.resumes);
      return response.data.resumes;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch resumes');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Fetch a single resume
  const fetchResume = async (resumeId: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await documentsAPI.getResume(resumeId);
      setCurrentDocument(response.data.resume);
      return response.data.resume;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch resume');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Generate a resume
  const generateResume = async (params: { job_posting_id: number; template?: string; ai_optimize?: boolean }) => {
    setLoading(true);
    setError(null);
    try {
      const response = await documentsAPI.generateResume(params);
      // Add the new resume to the list
      setResumes(prev => [response.data.resume, ...prev]);
      return response.data.resume;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to generate resume');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Fetch all cover letters
  const fetchCoverLetters = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await documentsAPI.getCoverLetters();
      setCoverLetters(response.data.cover_letters);
      return response.data.cover_letters;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch cover letters');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Fetch a single cover letter
  const fetchCoverLetter = async (coverId: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await documentsAPI.getCoverLetter(coverId);
      setCurrentDocument(response.data.cover_letter);
      return response.data.cover_letter;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch cover letter');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Generate a cover letter
  const generateCoverLetter = async (params: { job_posting_id: number; template?: string; ai_optimize?: boolean }) => {
    setLoading(true);
    setError(null);
    try {
      const response = await documentsAPI.generateCoverLetter(params);
      // Add the new cover letter to the list
      setCoverLetters(prev => [response.data.cover_letter, ...prev]);
      return response.data.cover_letter;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to generate cover letter');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Fetch document templates
  const fetchTemplates = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await documentsAPI.getTemplates('all');
      setTemplates({
        resume_templates: response.data.resume_templates || [],
        cover_letter_templates: response.data.cover_letter_templates || []
      });
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch templates');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    resumes,
    coverLetters,
    currentDocument,
    templates,
    loading,
    error,
    fetchResumes,
    fetchResume,
    generateResume,
    fetchCoverLetters,
    fetchCoverLetter,
    generateCoverLetter,
    fetchTemplates
  };
};
