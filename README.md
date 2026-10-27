# Employee Performance Management System

A web application for managing employee performance reviews, review statuses, and employee development plans.

## Features
- Employee performance review workflows
- Review status updates
- Development plan management and approval
- Backend API integration
- Database-backed employee performance records

## Technology Stack
- Frontend: React, JavaScript, CSS
- Backend: Python, Flask
- Database: See the existing backend configuration

## Prerequisites
- Python installed
- Node.js and npm installed
- Git installed

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/shaikayazhussain9121682625/employee-performance-management-system.git
cd employee-performance-management-system
```

### 2. Set up the Python environment
Run these commands from the project root in PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies using the dependency file provided by the project. Check the backend folder for the applicable requirements file.

### 3. Set up the frontend
```powershell
cd frontend
npm install
npm run build
cd ..
```

### 4. Start the application
Use the existing backend entry point and configuration to start the Flask API. Start the frontend using the scripts defined in `frontend/package.json`.

The current workflow frontend is configured to call `http://127.0.0.1:5000`.

## Testing
Run the backend tests from the project root:
```powershell
python -m unittest discover -s backend/tests -v
```

Build the frontend:
```powershell
cd frontend
npm run build
```

## API Workflows
The application includes review and development-plan workflow endpoints. Refer to the backend route files for the current endpoint definitions and request requirements.

## Repository
https://github.com/shaikayazhussain9121682625/employee-performance-management-system

## Notes
Configure required environment variables and database settings before running the application. Never commit passwords, API keys, or other secrets.
