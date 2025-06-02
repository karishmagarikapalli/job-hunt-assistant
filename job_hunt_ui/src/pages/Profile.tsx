import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';

// Import components (these would be created separately)
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import ProfileForm from '../components/ProfileForm';
import LinkedInSection from '../components/LinkedInSection';
import SkillsSection from '../components/SkillsSection';
import ExperienceSection from '../components/ExperienceSection';

const Profile = () => {
  const { user, updateProfile, isLoading, error } = useAuth();
  const [activeTab, setActiveTab] = useState('basic');
  const [saveStatus, setSaveStatus] = useState('');
  
  // Reset save status after 3 seconds
  useEffect(() => {
    if (saveStatus) {
      const timer = setTimeout(() => {
        setSaveStatus('');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [saveStatus]);
  
  const handleProfileUpdate = async (profileData) => {
    try {
      await updateProfile(profileData);
      setSaveStatus('success');
    } catch (err) {
      setSaveStatus('error');
      console.error('Error updating profile:', err);
    }
  };
  
  if (isLoading && !user) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading profile...</p>
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
          <h1 className="text-2xl font-semibold mb-6">Your Profile</h1>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          
          {saveStatus === 'success' && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
              Profile updated successfully!
            </div>
          )}
          
          {saveStatus === 'error' && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              Failed to update profile. Please try again.
            </div>
          )}
          
          <div className="bg-white rounded-lg shadow">
            <div className="border-b">
              <nav className="flex">
                <button 
                  className={`px-6 py-3 font-medium ${activeTab === 'basic' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('basic')}
                >
                  Basic Information
                </button>
                <button 
                  className={`px-6 py-3 font-medium ${activeTab === 'linkedin' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('linkedin')}
                >
                  LinkedIn Data
                </button>
                <button 
                  className={`px-6 py-3 font-medium ${activeTab === 'skills' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('skills')}
                >
                  Skills
                </button>
                <button 
                  className={`px-6 py-3 font-medium ${activeTab === 'experience' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('experience')}
                >
                  Experience
                </button>
              </nav>
            </div>
            
            <div className="p-6">
              {activeTab === 'basic' && (
                <ProfileForm 
                  user={user} 
                  onSubmit={handleProfileUpdate} 
                  isLoading={isLoading}
                />
              )}
              
              {activeTab === 'linkedin' && (
                <LinkedInSection 
                  linkedInUrl={user?.linkedin_url} 
                  onUpdate={handleProfileUpdate}
                />
              )}
              
              {activeTab === 'skills' && (
                <SkillsSection 
                  userId={user?.id}
                />
              )}
              
              {activeTab === 'experience' && (
                <ExperienceSection 
                  userId={user?.id}
                />
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Profile;
