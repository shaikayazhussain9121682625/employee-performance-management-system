# AI Prompt History

## Project: Employee Performance Management System

### 1. Purpose

This document records how AI assistance was used during the planning, implementation, debugging, and testing of the Employee Performance Management System.

AI assistance was used to explain requirements, suggest implementation steps, generate code drafts, troubleshoot issues, and prepare documentation. Generated code was tested locally before being treated as working.

## 2. Planning and Requirements

### Prompt 1: Understand the assessment and plan the project

**Prompt summary:**

Review the project requirements, explain them from scratch in beginner-friendly language, and create a detailed 72-hour implementation plan. Identify the required features, deliverables, tools, data entities, validation rules, and submission requirements. Do not omit requirements.

**Purpose:** Understand the assessment and organize the work into manageable stages.

**Outcome:** Planned a full-stack employee performance application, synthetic data generation, validation, API development, frontend implementation, testing, and submission documentation.

## 3. Synthetic Data Generation

### Prompt 2: Generate reproducible synthetic data

**Prompt summary:**

Help implement a Python synthetic-data generator for managers, employees, review cycles, goals, key results, check-ins, competencies, reviews, feedback, development plans, and event history. Use a fixed seed and generate the required record volumes.

**Purpose:** Create realistic, reproducible test data without using real employee information.

**Outcome:** Generated CSV and JSON artifacts using seed `20261022`, including 3,000 employees, 500 managers, 10,000 goals, and 20,000 check-ins.

### Prompt 3: Include labelled edge cases

**Prompt summary:**

Introduce labelled data-quality edge cases, preserve expected labels separately from application input data, and implement checks for record relationships, progress ranges, traceability, and review-cycle changes.

**Purpose:** Test whether the system can identify inconsistent or incomplete records.

**Outcome:** Created five labelled edge cases and separate `ground_truth.csv` and `ground_truth.json` files.

### Prompt 4: Validate generated data

**Prompt summary:**

Create validation checks for primary-key uniqueness, foreign-key integrity, allowed values, date ordering, arithmetic consistency, lifecycle rules, duplicate records, and expected edge cases. Verify reproducibility using the same seed.

**Purpose:** Demonstrate data quality and repeatability.

**Outcome:** The validator reported PASS, with six findings, zero unexpected findings, and five expected edge cases represented in the ground truth.

## 4. Backend Development

### Prompt 5: Create the database models

**Prompt summary:**

Implement Flask-SQLAlchemy models aligned with the project schema. Define entity relationships, primary keys, foreign keys, and the fields needed for goals, check-ins, reviews, feedback, development plans, and event history.

**Purpose:** Build the database structure for the application.

**Outcome:** Created the database models and successfully imported them in a local Python test.

### Prompt 6: Import synthetic data

**Prompt summary:**

Implement a CSV-to-SQLite import script with explicit field mappings and a safe import order that respects entity relationships. Keep ground-truth labels out of the application tables.

**Purpose:** Load the generated data into the application database.

**Outcome:** Imported 64,512 records across the application tables. The database verification script confirmed expected counts and no foreign-key violations.

### Prompt 7: Implement API endpoints

**Prompt summary:**

Create Flask endpoints for employee listing and search, goals and key results, dashboard summaries, and data-quality exceptions. Return structured JSON responses suitable for a React frontend.

**Purpose:** Provide application data to the frontend.

**Outcome:** Implemented and locally tested the employee, goal, dashboard summary, and exception endpoints.

### Prompt 8: Detect data-quality exceptions

**Prompt summary:**

Implement rule-based exception detection for goal-owner mismatches, progress outside the permitted range without a rationale, unauthorized reviewer relationships, incomplete feedback traceability, and changes in closed review cycles without reasons.

**Purpose:** Identify suspicious records and recommend human review rather than automatically correcting them.

**Outcome:** The exceptions endpoint returned five expected findings: four high-severity and one medium-severity.

## 5. Frontend Development

### Prompt 9: Build the React dashboard

**Prompt summary:**

Create a professional React dashboard that retrieves data from the Flask backend and displays employee and manager totals, goal metrics, average progress, department distribution, and an employee directory with search.

**Purpose:** Make the system understandable and usable through a browser interface.

**Outcome:** Implemented and locally checked the dashboard using React, Vite, and CSS.

### Prompt 10: Add an exceptions review section

**Prompt summary:**

Extend the existing dashboard without removing its working features. Fetch exception data from the backend and display severity totals, affected record IDs, rule names, explanations, and recommended actions.

**Purpose:** Make data-quality findings visible to reviewers.

**Outcome:** Added an Exceptions & Review Queue section. Confirmed that the frontend displayed the five expected exceptions.

## 6. Automated Testing

### Prompt 11: Create API tests

**Prompt summary:**

Write automated tests for the API health endpoint, home endpoint, dashboard totals, employee listing, goal listing, and exception counts and rules.

**Purpose:** Verify the implemented endpoints and expected dataset results.

**Outcome:** Seven automated tests passed using:

`python -m unittest discover -s backend/tests -v`

## 7. Documentation and Submission Preparation

### Prompt 12: Prepare project documentation

**Prompt summary:**

Draft a root-level README explaining the project overview, technologies, setup, dataset, APIs, validation, tests, limitations, and future improvements.

**Purpose:** Help another developer understand and run the project.

**Outcome:** Created the root-level `README.md`.

### Prompt 13: Record AI prompt history

**Prompt summary:**

Document the AI-assisted planning, implementation, debugging, and testing workflow. Distinguish prompt summaries from exact prompts and record the checks actually performed.

**Purpose:** Make AI usage transparent and provide a development audit trail.

**Outcome:** Created this prompt-history document.

## 8. Verification Evidence

The following checks were performed during development:

- Synthetic data generation completed using a fixed seed.
- Repeated generation produced matching output checksums.
- Data validation reported PASS, with zero unexpected findings.
- SQLite database counts matched the generated dataset.
- Database foreign-key integrity checks passed.
- Backend API endpoints were tested locally.
- The React dashboard and exceptions section were opened and checked in the browser.
- Seven automated API tests passed.

## 9. AI Use and Human Verification

AI assistance was used to help plan the application, draft code, explain implementation steps, troubleshoot issues, and prepare documentation.

The developer ran the commands and tests described above and checked the application locally. The verification results recorded here reflect those checks.

This document contains reconstructed prompt summaries. It should not be interpreted as a complete verbatim export of every conversation or command.

## 10. Remaining Verification

Before submission, verify the following:

- Review the final schema and data dictionary against the implementation.
- Confirm that the source manifest documents the dataset's synthetic provenance and generation configuration.
- Confirm that ground-truth labels are excluded from application inputs.
- Verify the final repository contents and `.gitignore`.
- Confirm all assessment-specific deliverables are included.
- Review the final README commands on a clean setup where practical.
