import React, { useState, useEffect } from 'react';
import { useDocuments } from '../hooks/useDocuments';

// Import components (these would be created separately)
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import DocumentList from '../components/DocumentList';
import TemplateSelector from '../components/TemplateSelector';

const DocumentManager = () => {
  const { 
    resumes, 
    coverLetters, 
    templates, 
    loading, 
    error, 
    fetchResumes, 
    fetchCoverLetters, 
    fetchTemplates 
  } = useDocuments();
  
  const [activeTab, setActiveTab] = useState('resumes');
  const [showTemplateSelector, setShowTemplateSelector] = useState(false);
  const [templateType, setTemplateType] = useState('resume');
  
  useEffect(() => {
    // Fetch documents and templates on component mount
    fetchResumes();
    fetchCoverLetters();
    fetchTemplates();
  }, []);
  
  const handleCreateNew = (type: string) => {
    setTemplateType(type);
    setShowTemplateSelector(true);
  };
  
  if (loading && resumes.length === 0 && coverLetters.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading documents...</p>
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
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-semibold">Document Manager</h1>
            <div className="flex space-x-4">
              <button 
                className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition"
                onClick={() => handleCreateNew('resume')}
              >
                Create Resume
              </button>
              <button 
                className="bg-secondary text-white px-4 py-2 rounded-lg hover:bg-secondary-dark transition"
                onClick={() => handleCreateNew('cover_letter')}
              >
                Create Cover Letter
              </button>
            </div>
          </div>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          
          <div className="bg-white rounded-lg shadow">
            <div className="border-b">
              <nav className="flex">
                <button 
                  className={`px-6 py-3 font-medium ${activeTab === 'resumes' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('resumes')}
                >
                  Resumes ({resumes.length})
                </button>
                <button 
                  className={`px-6 py-3 font-medium ${activeTab === 'cover_letters' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('cover_letters')}
                >
                  Cover Letters ({coverLetters.length})
                </button>
                <button 
                  className={`px-6 py-3 font-medium ${activeTab === 'templates' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('templates')}
                >
                  Templates
                </button>
              </nav>
            </div>
            
            <div className="p-6">
              {activeTab === 'resumes' && (
                <DocumentList 
                  documents={resumes} 
                  type="resume"
                  emptyMessage="No resumes found. Create your first resume to get started."
                />
              )}
              
              {activeTab === 'cover_letters' && (
                <DocumentList 
                  documents={coverLetters} 
                  type="cover_letter"
                  emptyMessage="No cover letters found. Create your first cover letter to get started."
                />
              )}
              
              {activeTab === 'templates' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-medium mb-4">Resume Templates</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {templates.resume_templates.map(template => (
                        <div key={template.id} className="border rounded-lg overflow-hidden hover:shadow-md transition">
                          <img 
                            src={template.preview_url} 
                            alt={template.name} 
                            className="w-full h-40 object-cover"
                          />
                          <div className="p-4">
                            <h4 className="font-medium">{template.name}</h4>
                            <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                            <button 
                              className="mt-3 w-full bg-primary text-white px-3 py-1 rounded hover:bg-primary-dark transition text-sm"
                              onClick={() => handleCreateNew('resume')}
                            >
                              Use Template
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium mb-4">Cover Letter Templates</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {templates.cover_letter_templates.map(template => (
                        <div key={template.id} className="border rounded-lg overflow-hidden hover:shadow-md transition">
                          <img 
                            src={template.preview_url} 
                            alt={template.name} 
                            className="w-full h-40 object-cover"
                          />
                          <div className="p-4">
                            <h4 className="font-medium">{template.name}</h4>
                            <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                            <button 
                              className="mt-3 w-full bg-secondary text-white px-3 py-1 rounded hover:bg-secondary-dark transition text-sm"
                              onClick={() => handleCreateNew('cover_letter')}
                            >
                              Use Template
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {showTemplateSelector && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-auto">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold">
                    {templateType === 'resume' ? 'Create New Resume' : 'Create New Cover Letter'}
                  </h2>
                  <button 
                    className="text-gray-500 hover:text-gray-700"
                    onClick={() => setShowTemplateSelector(false)}
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <TemplateSelector 
                  templates={templateType === 'resume' ? templates.resume_templates : templates.cover_letter_templates}
                  type={templateType}
                  onSelect={(templateId) => {
                    // This would normally open a form to select a job and create the document
                    console.log(`Selected template: ${templateId} for ${templateType}`);
                    setShowTemplateSelector(false);
                  }}
                  onCancel={() => setShowTemplateSelector(false)}
                />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default DocumentManager;
