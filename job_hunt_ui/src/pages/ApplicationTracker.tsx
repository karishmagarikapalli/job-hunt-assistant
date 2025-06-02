import React, { useState, useEffect } from 'react';
import { useJobs } from '../hooks/useJobs';
import { useDocuments } from '../hooks/useDocuments';

// Import components (these would be created separately)
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import ApplicationCard from '../components/ApplicationCard';
import ApplicationStats from '../components/ApplicationStats';
import ApplicationFilters from '../components/ApplicationFilters';

// Mock API for applications (would be replaced with real API)
const applicationsAPI = {
  getApplications: async () => {
    // This would be a real API call
    return {
      data: {
        applications: [
          {
            id: 1,
            job_posting_id: 101,
            status: 'submitted',
            application_date: '2025-05-15T10:30:00',
            company: 'Tech Solutions Inc.',
            position: 'Senior Full Stack Developer',
            resume_id: 1,
            cover_letter_id: 1
          },
          {
            id: 2,
            job_posting_id: 102,
            status: 'interview',
            application_date: '2025-05-10T14:45:00',
            company: 'Data Innovations',
            position: 'Solution Engineer',
            resume_id: 2,
            cover_letter_id: 2
          },
          {
            id: 3,
            job_posting_id: 103,
            status: 'rejected',
            application_date: '2025-05-05T09:15:00',
            company: 'Cloud Systems',
            position: 'Full Stack Developer',
            resume_id: 3,
            cover_letter_id: 3
          }
        ],
        stats: {
          total: 3,
          submitted: 1,
          interview: 1,
          rejected: 1,
          offer: 0
        }
      }
    };
  }
};

const ApplicationTracker = () => {
  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'all',
    search: ''
  });
  
  useEffect(() => {
    const fetchApplications = async () => {
      setLoading(true);
      try {
        const response = await applicationsAPI.getApplications();
        setApplications(response.data.applications);
        setStats(response.data.stats);
      } catch (err) {
        setError('Failed to load applications');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchApplications();
  }, []);
  
  // Filter applications based on current filters
  const filteredApplications = applications.filter(app => {
    // Filter by status
    if (filters.status !== 'all' && app.status !== filters.status) {
      return false;
    }
    
    // Filter by search term
    if (filters.search && !app.company.toLowerCase().includes(filters.search.toLowerCase()) && 
        !app.position.toLowerCase().includes(filters.search.toLowerCase())) {
      return false;
    }
    
    // Filter by date range (simplified for now)
    if (filters.dateRange !== 'all') {
      const appDate = new Date(app.application_date);
      const now = new Date();
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(now.getDate() - 30);
      
      if (filters.dateRange === 'month' && appDate < thirtyDaysAgo) {
        return false;
      }
    }
    
    return true;
  });
  
  const handleFilterChange = (newFilters) => {
    setFilters({ ...filters, ...newFilters });
  };
  
  if (loading && applications.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading applications...</p>
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
          <h1 className="text-2xl font-semibold mb-6">Application Tracker</h1>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h2 className="text-lg font-medium mb-4">Application Stats</h2>
                {stats && <ApplicationStats stats={stats} />}
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-medium mb-4">Filters</h2>
                <ApplicationFilters 
                  filters={filters} 
                  onFilterChange={handleFilterChange} 
                />
              </div>
            </div>
            
            <div className="lg:col-span-3">
              <div className="bg-white rounded-lg shadow">
                <div className="p-4 border-b">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">
                      Showing {filteredApplications.length} of {applications.length} applications
                    </span>
                    <div className="flex items-center">
                      <span className="text-sm text-gray-600 mr-2">Sort by:</span>
                      <select className="border rounded p-1 text-sm">
                        <option value="date">Date (newest first)</option>
                        <option value="company">Company</option>
                        <option value="status">Status</option>
                      </select>
                    </div>
                  </div>
                </div>
                
                {filteredApplications.length === 0 ? (
                  <div className="p-6 text-center">
                    <p className="text-gray-600">No applications found matching your criteria.</p>
                  </div>
                ) : (
                  <div className="divide-y">
                    {filteredApplications.map(application => (
                      <ApplicationCard 
                        key={application.id} 
                        application={application} 
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default ApplicationTracker;
