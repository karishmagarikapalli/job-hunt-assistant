import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useJobs } from '../hooks/useJobs';
import { useDocuments } from '../hooks/useDocuments';
import { useAI } from '../hooks/useAI';

// Import components (these would be created separately)
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import JobStatistics from '../components/JobStatistics';
import RecentJobs from '../components/RecentJobs';
import ApplicationStatus from '../components/ApplicationStatus';
import DocumentSummary from '../components/DocumentSummary';

const Dashboard = () => {
  const { user } = useAuth();
  const { jobs, fetchJobs, stats, fetchJobStats } = useJobs();
  const { resumes, coverLetters, fetchResumes, fetchCoverLetters } = useDocuments();
  const { jobMatches, matchJobs } = useAI();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);
      try {
        // Fetch all necessary data for dashboard
        await Promise.all([
          fetchJobs({ status: 'new' }),
          fetchJobStats(),
          fetchResumes(),
          fetchCoverLetters()
        ]);
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 overflow-auto">
        <Navbar />
        <main className="p-6">
          <h1 className="text-2xl font-semibold mb-6">Welcome back, {user?.first_name || user?.username}</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium mb-4">Job Search Summary</h2>
              {stats && <JobStatistics stats={stats} />}
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium mb-4">Application Status</h2>
              <ApplicationStatus />
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium mb-4">Document Summary</h2>
              <DocumentSummary 
                resumeCount={resumes.length} 
                coverLetterCount={coverLetters.length} 
              />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium">Recent Job Postings</h2>
              <a href="/jobs" className="text-primary hover:underline">View all</a>
            </div>
            <RecentJobs jobs={jobs.slice(0, 5)} />
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium mb-4">Quick Actions</h2>
              <div className="grid grid-cols-2 gap-4">
                <button 
                  className="bg-primary text-white p-3 rounded-lg hover:bg-primary-dark transition"
                  onClick={() => window.location.href = '/jobs/scrape'}
                >
                  Scrape New Jobs
                </button>
                <button 
                  className="bg-secondary text-white p-3 rounded-lg hover:bg-secondary-dark transition"
                  onClick={() => window.location.href = '/documents'}
                >
                  Manage Documents
                </button>
                <button 
                  className="bg-tertiary text-white p-3 rounded-lg hover:bg-tertiary-dark transition"
                  onClick={() => window.location.href = '/applications'}
                >
                  Track Applications
                </button>
                <button 
                  className="bg-gray-200 text-gray-800 p-3 rounded-lg hover:bg-gray-300 transition"
                  onClick={() => window.location.href = '/settings'}
                >
                  Settings
                </button>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium mb-4">AI Insights</h2>
              <p className="text-gray-600 mb-4">
                Use AI to match your profile with job postings and optimize your application materials.
              </p>
              <button 
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white p-3 rounded-lg hover:from-blue-600 hover:to-purple-700 transition"
                onClick={() => {
                  const jobIds = jobs.map(job => job.id);
                  matchJobs({ job_ids: jobIds });
                }}
              >
                Generate Job Matches
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
