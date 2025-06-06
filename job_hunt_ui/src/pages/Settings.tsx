import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';

// Import components (these would be created separately)
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import SettingsForm from '../components/SettingsForm';
import AutomationSettings from '../components/AutomationSettings';
import NotificationSettings from '../components/NotificationSettings';
import ApiKeys from '../components/ApiKeys';

const Settings = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('general');
  const [saveStatus, setSaveStatus] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Reset save status after 3 seconds
  useEffect(() => {
    if (saveStatus) {
      const timer = setTimeout(() => {
        setSaveStatus('');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [saveStatus]);
  
  const handleSaveSettings = async (settings) => {
    setLoading(true);
    try {
      // This would be a real API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSaveStatus('success');
    } catch (err) {
      setSaveStatus('error');
      console.error('Error saving settings:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 overflow-auto">
        <Navbar />
        <main className="p-6">
          <h1 className="text-2xl font-semibold mb-6">Settings</h1>
          
          {saveStatus === 'success' && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
              Settings saved successfully!
            </div>
          )}
          
          {saveStatus === 'error' && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              Failed to save settings. Please try again.
            </div>
          )}
          
          <div className="bg-white rounded-lg shadow">
            <div className="border-b">
              <nav className="flex">
                <button 
                  className={`px-6 py-3 font-medium ${activeTab === 'general' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('general')}
                >
                  General
                </button>
                <button 
                  className={`px-6 py-3 font-medium ${activeTab === 'automation' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('automation')}
                >
                  Automation
                </button>
                <button 
                  className={`px-6 py-3 font-medium ${activeTab === 'notifications' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('notifications')}
                >
                  Notifications
                </button>
                <button 
                  className={`px-6 py-3 font-medium ${activeTab === 'api' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('api')}
                >
                  API Keys
                </button>
              </nav>
            </div>
            
            <div className="p-6">
              {activeTab === 'general' && (
                <SettingsForm 
                  initialSettings={{
                    jobBoardsEnabled: true,
                    companyWebsitesEnabled: true,
                    h1bSponsorshipRequired: true,
                    fullTimeOnly: true,
                    targetRoles: ['Full Stack Developer', 'Senior Full Stack Developer', 'Solution Engineer'],
                    preferredLocations: ['Remote', 'San Francisco, CA', 'Seattle, WA']
                  }}
                  onSave={handleSaveSettings}
                  loading={loading}
                />
              )}
              
              {activeTab === 'automation' && (
                <AutomationSettings 
                  initialSettings={{
                    automatedApplicationsEnabled: true,
                    requireApprovalBeforeSubmit: true,
                    maxDailyApplications: 10,
                    minMatchScore: 0.7,
                    autoGenerateDocuments: true,
                    browserAutomationLevel: 'advanced'
                  }}
                  onSave={handleSaveSettings}
                  loading={loading}
                />
              )}
              
              {activeTab === 'notifications' && (
                <NotificationSettings 
                  initialSettings={{
                    emailNotificationsEnabled: true,
                    emailAddress: user?.email,
                    notifyOnNewJobs: true,
                    notifyOnApplicationStatus: true,
                    notifyOnInterviewRequests: true,
                    dailySummary: true
                  }}
                  onSave={handleSaveSettings}
                  loading={loading}
                />
              )}
              
              {activeTab === 'api' && (
                <ApiKeys 
                  keys={[
                    { service: 'LinkedIn', key: '••••••••••••••••', status: 'active' },
                    { service: 'Indeed', key: '••••••••••••••••', status: 'active' },
                    { service: 'Glassdoor', key: '••••••••••••••••', status: 'inactive' }
                  ]}
                  onSave={handleSaveSettings}
                  loading={loading}
                />
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Settings;
