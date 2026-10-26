# Data Dictionary — Employee Performance Management System

## 1. Overview

This document describes the CSV datasets generated for the Employee Performance Management System, including their purpose, columns, and relationships.

All generated records are synthetic. The generation seed is `20261022`. Dataset counts and generation metadata are recorded in `data/generated/source_manifest.json`.

## 2. Dataset Summary

| Dataset | Records | Purpose |
|---|---:|---|
| `managers.csv` | 500 | Manager details |
| `employees.csv` | 3,000 | Employee records |
| `review_cycles.csv` | 2 | Performance review periods |
| `competencies.csv` | 8 | Competency definitions |
| `goals.csv` | 10,000 | Employee goals and progress |
| `key_results.csv` | 20,000 | Measurable results associated with goals |
| `check_ins.csv` | 20,000 | Employee progress check-ins |
| `reviews.csv` | 3,000 | Performance review records |
| `feedback.csv` | 5,000 | Competency and performance feedback |
| `development_plans.csv` | 3,000 | Employee development actions |
| `event_history.csv` | 2 | Recorded events and reasons |
| `ground_truth.csv` | 5 | Expected labels for injected edge cases |

The project also generates `ground_truth.json` as a separate representation of expected edge-case labels.

## 3. Field Definitions

### 3.1 `managers.csv`

Purpose: Stores manager identity and department information.

| Column | Description |
|---|---|
| `manager_id` | Unique manager identifier |
| `full_name` | Synthetic manager name |
| `email` | Manager email address |
| `department` | Manager's department |

### 3.2 `employees.csv`

Purpose: Stores employee details and reporting relationships.

| Column | Description |
|---|---|
| `employee_id` | Unique employee identifier |
| `full_name` | Synthetic employee name |
| `email` | Employee email address |
| `department` | Employee's department |
| `job_title` | Employee's job title |
| `hire_date` | Employee hire date |
| `employment_status` | Employment status |
| `manager_id` | Identifier of the assigned manager |

### 3.3 `review_cycles.csv`

Purpose: Defines performance review periods.

| Column | Description |
|---|---|
| `cycle_id` | Unique review-cycle identifier |
| `name` | Review-cycle name |
| `start_date` | Cycle start date |
| `end_date` | Cycle end date |
| `status` | Review-cycle status |

### 3.4 `competencies.csv`

Purpose: Defines competencies used for performance feedback.

| Column | Description |
|---|---|
| `competency_id` | Unique competency identifier |
| `name` | Competency name |
| `description` | Competency description |

### 3.5 `goals.csv`

Purpose: Records employee goals and their progress.

| Column | Description |
|---|---|
| `goal_id` | Unique goal identifier |
| `employee_id` | Employee associated with the goal |
| `cycle_id` | Review cycle associated with the goal |
| `title` | Goal title |
| `status` | Goal status |
| `progress_percent` | Recorded goal progress percentage |
| `created_date` | Goal creation date |

### 3.6 `key_results.csv`

Purpose: Stores measurable results associated with goals.

| Column | Description |
|---|---|
| `key_result_id` | Unique key-result identifier |
| `goal_id` | Associated goal identifier |
| `description` | Key-result description |
| `target_value` | Intended target value |
| `current_value` | Current measured value |
| `unit` | Measurement unit |

### 3.7 `check_ins.csv`

Purpose: Records employee progress updates.

| Column | Description |
|---|---|
| `check_in_id` | Unique check-in identifier |
| `employee_id` | Employee associated with the check-in |
| `cycle_id` | Related review cycle |
| `check_in_date` | Check-in date |
| `progress_percent` | Reported progress percentage |
| `notes` | Check-in notes |
| `rationale` | Explanation supporting the reported progress, where applicable |

### 3.8 `reviews.csv`

Purpose: Records employee performance reviews.

| Column | Description |
|---|---|
| `review_id` | Unique review identifier |
| `employee_id` | Employee being reviewed |
| `cycle_id` | Associated review cycle |
| `reviewer_id` | Manager identifier recorded as reviewer |
| `score` | Recorded review score |
| `status` | Review status |
| `review_date` | Review date |

### 3.9 `feedback.csv`

Purpose: Records employee feedback and its attribution or evidence references.

| Column | Description |
|---|---|
| `feedback_id` | Unique feedback identifier |
| `employee_id` | Employee receiving feedback |
| `competency_id` | Related competency identifier, where present |
| `cycle_id` | Associated review cycle |
| `author_id` | Identifier recorded for the feedback author |
| `evidence_reference` | Reference to supporting evidence, where present |
| `rating` | Recorded feedback rating |
| `comments` | Feedback comments |
| `feedback_date` | Feedback date |

### 3.10 `development_plans.csv`

Purpose: Records employee development objectives and actions.

| Column | Description |
|---|---|
| `development_plan_id` | Unique development-plan identifier |
| `employee_id` | Employee associated with the plan |
| `review_id` | Related review identifier |
| `objective` | Development objective |
| `action` | Planned development action |
| `target_date` | Target completion date |
| `status` | Development-plan status |

### 3.11 `event_history.csv`

Purpose: Records events affecting tracked entities.

| Column | Description |
|---|---|
| `event_id` | Unique event identifier |
| `cycle_id` | Associated review cycle |
| `entity_type` | Type of entity affected |
| `record_id` | Identifier of the affected record |
| `event_type` | Recorded event type |
| `actor_id` | Identifier recorded for the actor |
| `event_time` | Event timestamp |
| `reason` | Recorded reason for the event, where provided |

### 3.12 `ground_truth.csv`

Purpose: Stores expected labels for deliberately injected edge cases. This file is for validation and evaluation, not an application input feature.

| Column | Description |
|---|---|
| `case_id` | Unique edge-case identifier |
| `entity_type` | Type of entity containing the case |
| `record_id` | Identifier of the affected record |
| `anomaly_type` | Category of the injected anomaly |
| `expected_label` | Expected classification or label |
| `description` | Explanation of the case |

## 4. Relationships

The principal relationships represented by the datasets are:

- A manager may supervise multiple employees.
- An employee may have multiple goals, check-ins, reviews, feedback records, and development plans.
- A review cycle may contain multiple goals, check-ins, reviews, feedback records, and events.
- A goal may have multiple key results.
- A competency may be referenced by multiple feedback records.
- A development plan references an employee and a review.
- Ground-truth cases reference affected records but are kept separate from application data.

The precise database constraints and cardinalities should be read alongside `docs/schema.md` and the SQLAlchemy models.

## 5. Data Quality Considerations

The generated dataset includes five deliberately injected edge cases:

1. Goal identifier and recorded owner mismatch.
2. Check-in progress outside the permitted range without a rationale.
3. Reviewer not matching the employee's assigned manager.
4. Feedback missing author attribution and evidence reference.
5. Goal change in a closed review cycle without a reason.

These cases are expected test inputs. They should not be confused with unexpected generator or import errors.

## 6. Provenance and Reproducibility

- Data type: Synthetic.
- Generator version: `2.0`.
- Seed: `20261022`.
- Reference date: `2026-10-26`.
- Generation metadata: `data/generated/source_manifest.json`.
- Generator: `scripts/generate_data.py`.
- Validation: `scripts/validate_data.py`.
- Database verification: `scripts/verify_database.py`.

Use the source manifest and validation scripts as the primary evidence for generated record counts and reproducibility.
