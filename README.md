Employee Performance Management System
A full-stack employee performance management prototype for tracking employees, goals, key results, check-ins, performance reviews, competency feedback, development plans, and data-quality exceptions.
The project uses synthetic data only. Its rule-based exception detection highlights suspicious or incomplete records for human review. It does not silently correct records or make automatic employment decisions.
Contents
Project Overview
Features
Technology Stack
Data Model
Dataset
Project Structure
Setup and Run
Generate and Validate Data
Import Data into SQLite
API Endpoints
Data Quality Exceptions
Testing
Reproducibility
AI Prompt History
Limitations
Project Overview
The Employee Performance Management System is a web application designed to organize employee performance information in one place.
It provides a React frontend, a Python Flask backend, and an SQLite database. The system manages employee records, manager assignments, review cycles, goals, key results, check-ins, feedback, reviews, and development plans.
The application also identifies selected data-quality issues using predefined rules.
Features
Employee directory and employee search.
Dashboard with performance summary metrics.
Goal and key-result tracking.
Employee check-ins and performance reviews.
Competency feedback and development plans.
Manager assignment history.
Event history for tracking selected changes.
Rule-based data-quality exception detection.
Synthetic dataset generation using a fixed random seed.
CSV data import into SQLite.
Database integrity verification.
Backend API tests.
Technology Stack
Component	Technology
Frontend	React, Vite, JavaScript, CSS
Backend	Python, Flask
Database	SQLite, Flask-SQLAlchemy
Synthetic Data	Faker
Testing	Python unittest
Version Control	Git
Data Model
The system contains the following entities:
Employee: Stores employee information.
Manager: Stores manager information.
ReviewCycle: Defines performance review periods.
Goal: Stores employee goals.
KeyResult: Tracks measurable goal outcomes.
CheckIn: Records periodic progress updates.
Competency: Defines performance competencies.
Feedback: Stores feedback records.
Review: Stores performance review information.
DevelopmentPlan: Tracks employee development plans.
EventHistory: Records selected system events.
ManagerAssignmentHistory: Tracks manager assignment changes.
The database models define relationships between entities using primary keys and foreign keys.
Refer to `docs/schema.md` for the available schema documentation.
Dataset
The baseline dataset uses random seed `20261022`.
Entity	Baseline Records
Managers	500
Employees	3,000
Review Cycles	2
Competencies	8
Goals	10,000
Key Results	20,000
Check-ins	20,000
Reviews	3,000
Feedback	5,000
Development Plans	3,000
Event History	2
Manager Assignment History	3,030
The generated baseline contains 67,542 application records.
The local application database can contain additional event-history records created during development and testing, so its counts may differ from the baseline.
Five labelled edge cases are generated separately for validation. Ground-truth files are not imported into the application tables.
Project Structure
```text
employee-performance-system/
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ app.py
â”‚   â”œâ”€â”€ config.py
â”‚   â”œâ”€â”€ extensions.py
â”‚   â”œâ”€â”€ import_data.py
â”‚   â”œâ”€â”€ models/
â”‚   â”œâ”€â”€ routes/
â”‚   â”œâ”€â”€ services/
â”‚   â”œâ”€â”€ tests/
â”‚   â””â”€â”€ requirements.txt
â”œâ”€â”€ data/
â”‚   â””â”€â”€ generated_v3/
â”œâ”€â”€ docs/
â”‚   â””â”€â”€ schema.md
â”œâ”€â”€ frontend/
â”‚   â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ package.json
â”‚   â””â”€â”€ index.html
â”œâ”€â”€ prompt-history/
â”‚   â””â”€â”€ prompts.md
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ check_goal_progress.py
â”‚   â”œâ”€â”€ export_sql.py
â”‚   â”œâ”€â”€ generate_data.py
â”‚   â”œâ”€â”€ migrate_workflows.py
â”‚   â”œâ”€â”€ validate_data.py
â”‚   â””â”€â”€ verify_database.py
â”œâ”€â”€ tests/
â”œâ”€â”€ .gitignore
â””â”€â”€ README.md
```
Requirements
Install the following tools before running the project:
Python 3.12 or a compatible version supported by the project dependencies.
Node.js and npm.
Git.
Visual Studio Code (recommended).
The commands below use Windows PowerShell and assume the terminal is opened in the project root.
Setup and Run
1. Open the project folder
```powershell
cd C:\Users\Lenovo\Desktop\employee-performance-system
```
2. Create a Python virtual environment
If the `.venv` directory does not already exist:
```powershell
python -m venv .venv
```
Activate the environment:
```powershell
.\.venv\Scripts\Activate.ps1
```
Install backend dependencies:
```powershell
python -m pip install -r backend/requirements.txt
```
3. Start the backend
From the project root, run:
```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m flask --app app run --debug --port 5000
```
Keep this terminal open while using the application.
Backend address:
`http://127.0.0.1:5000`
Health endpoint:
`http://127.0.0.1:5000/api/health`
4. Start the frontend
Open a second VS Code terminal and run:
```powershell
cd C:\Users\Lenovo\Desktop\employee-performance-system\frontend
npm install
npm run dev
```
Open the local URL displayed by Vite, typically:
`http://localhost:5173/`
Keep both frontend and backend terminals running while testing the application.
5. Build the frontend
From the `frontend` directory, run:
```powershell
npm run build
```
The production build is generated in `frontend/dist/`.
Generate and Validate Synthetic Data
Return to the project root before running the generator.
```powershell
cd C:\Users\Lenovo\Desktop\employee-performance-system
```
Generate the baseline dataset:
```powershell
python scripts/generate_data.py --seed 20261022 --employees 3000 --managers 500 --goals 10000 --checkins 20000 --feedback 5000 --output-dir data/generated_v3
```
Validate the data:
```powershell
python scripts/validate_data.py
```
Important: The validator uses its configured default data directory. Check `scripts/validate_data.py` before assuming it validates the `data/generated_v3` directory specifically.
Import Data into SQLite
The importer supports loading generated CSV files into a separate SQLite database.
Use this command from the project root:
```powershell
python backend/import_data.py --data-dir data/generated_v3 --database data/import_test_v3.db
```
The importer:
Reads the generated CSV files.
Loads tables in dependency order.
Checks the destination database.
Refuses to overwrite an existing destination unless `--allow-existing` is supplied.
Excludes ground-truth files from application tables.
Use a new database filename for a fresh import. Do not use `--allow-existing` unless you have confirmed the destination is safe to reuse.
Database safety: The regular backend configuration points to `data/employee_performance.db`, while the command above writes to `data/import_test_v3.db`. Importing data into the test database does not automatically replace or refresh the main application database.
Back up the existing database before performing any database replacement or migration.
Verify Database Integrity
Run the database verification script from the project root:
```powershell
python scripts/verify_database.py
```
Review its output and confirm which database the script checks.
The project has previously passed its database verification, including foreign-key checks and ground-truth separation. Run verification again after making changes.
API Endpoints
Method	Endpoint	Purpose
GET	`/`	API status
GET	`/api/health`	Backend health check
GET	`/api/dashboard/summary`	Dashboard summary metrics
GET	`/api/employees/`	List and search employees
GET	`/api/employees/<employee_id>`	Retrieve employee details
GET	`/api/goals/`	List and filter goals
GET	`/api/goals/<goal_id>`	Retrieve a goal and its key results
GET	`/api/exceptions/`	Retrieve data-quality findings
Data-Quality Exception Detection
The project includes five labelled edge-case categories.
1. Goal Owner Mismatch
A goal identifier refers to one employee, but its recorded owner refers to another employee.
2. Invalid Check-in Progress
A check-in contains progress outside the permitted range without a documented rationale.
3. Reviewer Relationship Mismatch
A review is recorded by someone who is not the employee's assigned manager under the applicable rule.
4. Closed-Cycle Edit Without a Reason
An event records an edit to a closed review cycle without a reason.
5. Feedback Traceability Issue
Feedback has an invalid or missing author, or lacks an evidence reference.
The latest reported validation detected all five labelled cases, produced six expected findings, and reported zero unexpected findings.
Ground-truth labels are kept separate from application input data. Findings are intended for human review; the system does not automatically correct records or invent missing information.
Testing
Run the backend unit tests from the project root:
```powershell
python -m unittest discover -s backend/tests -v
```
The latest reported run passed all seven tests covering the home endpoint, health endpoint, dashboard summary, employee list, goals, and exception behavior.
The frontend production build has also completed successfully with `npm run build`.
Run the tests again after making code changes.
Reproducibility and Data Integrity
The generator supports a fixed random seed.
The standard baseline seed is `20261022`.
Dataset sizes can be adjusted through command-line parameters.
Ground-truth labels are stored separately from application data.
Database verification checks configured record counts and foreign-key integrity.
Validation checks identifiers and expected edge cases.
For reproducible results, use the same generator version, seed, parameters, and output directory settings.
AI Prompt History
The `prompt-history/prompts.md` file documents reconstructed summaries of AI-assisted planning, development, debugging, and verification.
These summaries are not a verbatim transcript of every prompt or conversation.
Privacy, Limitations, and Future Work
This project uses synthetic data for development and demonstration.
The exception detection rules cover selected data-quality scenarios and do not represent a complete enterprise performance-management solution. Findings require human review.
Authentication, role-based authorization, production deployment hardening, and additional business workflows should not be considered complete unless implemented and separately verified.
Potential future improvements include:
Authentication and role-based access control.
Complete create, update, and close workflows for goals and reviews.
Review-cycle lifecycle enforcement.
Exception assignment and resolution tracking.
Expanded automated testing and continuous integration.
Production deployment of the frontend and backend.
License
Add a license before distributing the project publicly if required by your submission or intended use.
