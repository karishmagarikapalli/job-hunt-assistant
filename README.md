# Job Hunt Ecosystem

A comprehensive AI-powered job hunting system that scrapes job postings, generates tailored resumes and cover letters, and automates job applications.

## Features

- **Job Scraping**: Automatically collect job postings from multiple sources including company career pages
- **AI Job Matching**: Match your skills and experience with job requirements
- **Document Generation**: Create tailored resumes and cover letters for specific job postings
- **Application Automation**: Submit applications on your behalf
- **H1-B Sponsorship Filter**: Focus on jobs that offer visa sponsorship
- **Full-time Job Focus**: Target full-time positions
- **Expanded Role Targeting**: Support for various roles including Solution Engineering

## System Architecture

- **Backend**: Flask REST API with SQLite database
- **Frontend**: React application with TypeScript and Tailwind CSS
- **AI Modules**: Python-based job matching and document generation
- **Automation**: Playwright-based browser automation

## Prerequisites

- **Python**: Version 3.11 or higher
- **Node.js**: Version 20.18.0 or higher
- **npm**: Version 9.0.0 or higher
- **Git**: Version 2.30.0 or higher

### Python Dependencies
- Flask (2.0.0+)
- SQLAlchemy (1.4.0+)
- BeautifulSoup4 (4.9.0+)
- Requests (2.25.0+)
- Scikit-learn (1.6.0+)
- Jinja2 (3.0.0+)
- Playwright (1.20.0+)
- WeasyPrint (54.0+)

### Node.js Dependencies
- React (18.0.0+)
- TypeScript (4.5.0+)
- Tailwind CSS (3.0.0+)
- Axios (0.27.0+)

## Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/job-hunt-ecosystem.git
cd job-hunt-ecosystem
```

### Backend Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:

```bash
pip install -r job_hunt_app/requirements.txt
```

3. Initialize the database:

```bash
python job_hunt_app/src/data_structure_design.py
```

### Frontend Setup

1. Install Node.js dependencies:

```bash
cd job_hunt_ui
npm install
```

## Running the Application

### Start the Backend Server

```bash
cd job_hunt_app
python src/main.py
```

The backend server will start at http://localhost:5000

### Start the Frontend Development Server

In a new terminal:

```bash
cd job_hunt_ui
npm start
```

The frontend will be available at http://localhost:3000

## Configuration

### User Profile Setup

1. Navigate to the Profile page
2. Enter your personal details, work experience, education, and skills
3. Specify your H1-B sponsorship requirement

### Job Search Configuration

1. Go to the Settings page
2. Configure job boards and company websites to scrape
3. Set up job filters (location, job type, etc.)
4. Customize automation settings

## Usage

### Finding Jobs

1. Navigate to the Jobs page
2. Click "Scrape Jobs" to collect new job postings
3. Browse and filter job listings
4. Click on a job to view details and match score

### Generating Documents

1. From a job details page, click "Generate Documents"
2. Select a resume template
3. Select a cover letter template
4. Review and edit the generated documents
5. Save the documents for future use

### Applying to Jobs

1. From a job details page, click "Apply"
2. Select the resume and cover letter to use
3. Configure application settings
4. Click "Submit Application"
5. Monitor application status in the Applications page

## Troubleshooting

### Common Issues

- **Database Errors**: Ensure the database is properly initialized
- **API Connection Issues**: Check that the backend server is running
- **Frontend Not Loading**: Verify Node.js and npm versions
- **Automation Failures**: Check Playwright installation and browser dependencies

### Logs

Check the following log files for detailed error information:

- `job_hunt_app/src/logs/app.log`: Main application logs
- `job_hunt_app/src/logs/job_matcher.log`: AI job matching logs
- `job_hunt_app/src/logs/document_generator.log`: Document generation logs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
