# GitHub Hosting and Onboarding Guide for Job Hunt Ecosystem

This guide provides step-by-step instructions for hosting your Job Hunt Ecosystem on GitHub and getting it up and running locally.

## GitHub Repository Setup

### 1. Create a New GitHub Repository

1. Log in to your GitHub account
2. Click the "+" icon in the top-right corner and select "New repository"
3. Enter repository details:
   - Name: `job-hunt-ecosystem`
   - Description: "AI-powered job hunting system that scrapes postings, generates tailored resumes and cover letters, and automates applications"
   - Visibility: Choose either Public or Private based on your preference
   - Initialize with: Do NOT initialize with README, .gitignore, or license (we'll push our existing code)
4. Click "Create repository"

### 2. Push Your Local Repository to GitHub

From your local job_hunt_ecosystem directory, run the following commands:

```bash
# Initialize git repository
git init

# Add all files to staging
git add .

# Commit the files
git commit -m "Initial commit: Job Hunt Ecosystem"

# Add the remote GitHub repository
git remote add origin https://github.com/yourusername/job-hunt-ecosystem.git

# Push to GitHub
git push -u origin main
```

Note: Replace `yourusername` with your actual GitHub username.

## Local Setup Instructions

### Prerequisites

- **Python**: Version 3.11 or higher
- **Node.js**: Version 20.18.0 or higher
- **npm**: Version 9.0.0 or higher
- **Git**: Version 2.30.0 or higher
- **SQLite**: Version 3.0.0 or higher

### Clone and Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/job-hunt-ecosystem.git
cd job-hunt-ecosystem
```

2. **Set up the backend**

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r job_hunt_app/requirements.txt

# Initialize the database
chmod +x init_database.sh
./init_database.sh
```

3. **Set up the frontend**

```bash
# Navigate to the frontend directory
cd job_hunt_ui

# Install Node.js dependencies
npm install

# Return to the root directory
cd ..
```

4. **Start the application**

In one terminal (for the backend):
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the Flask backend
cd job_hunt_app
python src/main.py
```

In another terminal (for the frontend):
```bash
# Navigate to the frontend directory
cd job_hunt_ui

# Start the React development server
npm start
```

5. **Access the application**

Open your browser and navigate to:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api/health (should return a JSON response)

## Troubleshooting Common Issues

### Backend Issues

- **Missing dependencies**: Ensure you've activated the virtual environment and installed all dependencies
- **Database errors**: Check that the database initialization script ran successfully
- **Port conflicts**: If port 5000 is in use, modify the port in `job_hunt_app/src/main.py`

### Frontend Issues

- **Node.js version**: Ensure you're using Node.js 20.x or higher
- **Missing dependencies**: Run `npm install` again if you encounter module not found errors
- **Port conflicts**: If port 3000 is in use, React will prompt you to use a different port

### Browser Automation Issues

- **Playwright setup**: Run `playwright install` if you encounter browser automation issues
- **Missing browser dependencies**: Some Linux distributions may require additional packages for browser automation

## Customization

### Configuration Files

- **Backend configuration**: Edit `job_hunt_app/src/config.py` to modify database settings, API keys, etc.
- **Frontend configuration**: Edit `job_hunt_ui/.env` to modify API endpoints and other frontend settings

### Adding Job Boards

To add support for additional job boards:
1. Add the job board details to the database using the API or directly in the database
2. Implement a scraper for the job board in `job_hunt_app/src/scrapers/`
3. Register the scraper in `job_hunt_app/src/scrapers/__init__.py`

## Deployment Options

### Backend Deployment

- **Heroku**: Use the Procfile included in the repository
- **AWS**: Follow the Flask deployment guide for AWS
- **Docker**: A Dockerfile is included for containerized deployment

### Frontend Deployment

- **Netlify**: Connect your GitHub repository to Netlify
- **Vercel**: Connect your GitHub repository to Vercel
- **GitHub Pages**: Run `npm run build` and deploy the build directory

## Maintenance and Updates

- Regularly update dependencies using `pip-compile` for the backend and `npm update` for the frontend
- Check for security vulnerabilities using GitHub's Dependabot
- Keep browser automation tools updated for reliable job application automation

## Contributing

If you'd like to contribute to the project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
