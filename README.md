# Employee Performance Management System

## 1. Project Overview

The Employee Performance Management System is a full-stack application for managing employee goals, tracking progress, reviewing performance, and identifying data-quality issues.

The system uses synthetic employee data and rule-based validation to identify exceptions that require human review. It does not automatically correct suspicious records.

## 2. Objectives

- Track employee and manager information.
- Manage review cycles, goals, and key results.
- Monitor check-ins and performance progress.
- Store reviews, competency feedback, and development plans.
- Detect data inconsistencies and missing traceability.
- Maintain event history for review and audit purposes.
- Generate reproducible synthetic datasets.
- Validate data integrity and application APIs.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, Flask |
| Database | SQLite, Flask-SQLAlchemy |
| Data processing | Pandas |
| Synthetic data | Faker |
| Testing | Python unittest |

## 4. Dataset

The generated dataset contains:

| Entity | Records |
|---|---:|
| Managers | 500 |
| Employees | 3,000 |
| Review cycles | 2 |
| Competencies | 8 |
| Goals | 10,000 |
| Key results | 20,000 |
| Check-ins | 20,000 |
| Reviews | 3,000 |
| Feedback records | 5,000 |
| Development plans | 3,000 |
| Event history | 2 |

The ground-truth files contain five labelled edge cases and are kept separate from the application database.

## 5. Data Quality and Exception Detection

The system detects five types of data-quality issues:

1. Goal owner mismatch.
2. Check-in progress outside the permitted range without a rationale.
3. Reviewer not matching the employee's assigned manager.
4. Feedback missing author attribution and evidence reference.
5. Changes to goals in a closed review cycle without a reason.

Each finding includes a rule identifier, record identifier, severity, explanation, and recommended action.

Findings require human review. The system does not invent missing information or silently correct records.

## 6. Project Structure

```text
employee-performance-system/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── extensions.py
│   ├── import_data.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── tests/
│   │   └── test_api.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── index.html
├── data/
│   └── generated/
├── docs/
│   └── schema.md
├── scripts/
│   ├── generate_data.py
│   ├── validate_data.py
│   └── verify_database.py
└── README.md
```

## 7. Setup Instructions

### Prerequisites

- Python 3.12 or compatible version.
- Node.js and npm.
- Git.

### Backend setup

From the project root, activate the virtual environment and install dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

Start the backend:

```powershell
python backend/app.py
```

The backend runs at `http://127.0.0.1:5000`.

### Frontend setup

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

## 8. Data Generation and Validation

From the project root, generate the dataset using the fixed seed:

```powershell
python scripts/generate_data.py --seed 20261022 --employees 3000 --managers 500 --goals 10000 --checkins 20000 --feedback 5000
```

Validate the generated dataset:

```powershell
python scripts/validate_data.py
```

Verify database counts and foreign-key integrity:

```powershell
python scripts/verify_database.py
```

**Note:** Regenerating data does not automatically mean the existing SQLite database has been refreshed. Follow the import procedure when rebuilding the database.

## 9. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API status |
| GET | `/api/health` | Health check |
| GET | `/api/dashboard/summary` | Dashboard metrics |
| GET | `/api/employees/` | List and search employees |
| GET | `/api/employees/<employee_id>` | Retrieve an employee |
| GET | `/api/goals/` | List and filter goals |
| GET | `/api/goals/<goal_id>` | Retrieve a goal and its key results |
| GET | `/api/exceptions/` | Retrieve data-quality findings |

## 10. Automated Testing

Run the backend API tests from the project root:

```powershell
python -m unittest discover -s backend/tests -v
```

The current test suite contains seven tests covering API health, dashboard totals, employee and goal endpoints, and exception detection.

**Verified locally:** All seven tests passed.

## 11. Reproducibility and Integrity

The project uses a fixed random seed for synthetic data generation. Repeated generation with the same configuration was checked for consistent output checksums.

Database counts and foreign-key integrity were also verified.

## 12. Privacy and Limitations

The dataset is synthetic and intended for development and demonstration. Exception detection is rule-based, so findings should be reviewed by an authorized person before any record is changed.

The application is a prototype and should undergo security, authorization, deployment, and additional business-rule testing before production use.

## 13. Future Improvements

- Add authentication and role-based authorization.
- Add create, update, and close workflows for goals and reviews.
- Add review-cycle lifecycle enforcement.
- Add exception filtering, assignment, and resolution tracking.
- Expand automated tests and continuous integration.
- Deploy the frontend and backend to suitable hosting platforms.
