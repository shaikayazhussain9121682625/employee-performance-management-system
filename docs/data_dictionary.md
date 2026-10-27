# Data Dictionary - Employee Performance Management System

## 1. Overview

This document describes the CSV datasets generated for the Employee Performance Management System, including their purpose, columns, and relationships.

All generated records are synthetic. The generation seed is `20261022`. The reference date is `2026-10-26`, and the generator version is `3.0`. Dataset counts and generation metadata are recorded in `data/generated_v3/source_manifest.json`.

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
| `manager_assignment_history.csv` | 3,030 | Effective-dated employee-to-manager assignment history |
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
- Generator version: `3.0`.
- Seed: `20261022`.
- Reference date: `2026-10-26`.
- Generation metadata: `data/generated/source_manifest.json`.
- Generator: `scripts/generate_data.py`.
- Validation: `scripts/validate_data.py`.
- Database verification: `scripts/verify_database.py`.

Use the source manifest and validation scripts as the primary evidence for generated record counts and reproducibility.

## 7. Technical Field Specifications

This section documents field types, nullability, uniqueness, units, and validation expectations. CSV files do not enforce database constraints themselves. "Required" means the field is expected to contain a value in generated records; it does not automatically mean the database or application enforces that rule.

### 7.1 Type conventions

| Type | Meaning |
|---|---|
| String | Text identifier or descriptive text |
| Integer | Whole number |
| Decimal | Numeric value that may contain a fractional part |
| Date | Date formatted as YYYY-MM-DD |
| Timestamp | Date and time value |
| Nullable | Empty values may be represented where explicitly allowed |
| Primary key | Unique identifier for a record |
| Foreign key | Identifier that references a record in another dataset |

### 7.2 Managers

| Field | Type | Required | Uniqueness / validation |
|---|---|---|---|
| manager_id | String | Yes | Primary key; immutable identifier |
| full_name | String | Yes | Non-empty synthetic name |
| email | String | Yes | Unique email; validate email format |
| department | String | Yes | Non-empty department |

### 7.3 Employees

| Field | Type | Required | Uniqueness / validation |
|---|---|---|---|
| employee_id | String | Yes | Primary key; expected format EMP- followed by six digits |
| full_name | String | Yes | Non-empty synthetic name |
| email | String | Yes | Unique email; validate email format |
| department | String | Yes | Non-empty department |
| job_title | String | Yes | Non-empty job title |
| hire_date | Date | Yes | Valid date |
| employment_status | String | Yes | Observed values: active, inactive |
| manager_id | String | Yes in generated data | Must reference an existing manager |

### 7.4 Review cycles

| Field | Type | Required | Uniqueness / validation |
|---|---|---|---|
| cycle_id | String | Yes | Primary key |
| name | String | Yes | Non-empty cycle name |
| start_date | Date | Yes | Valid date |
| end_date | Date | Yes | Must not precede start_date |
| status | String | Yes | Validator permits planned, active, closed; observed values: active, closed |

### 7.5 Competencies

| Field | Type | Required | Uniqueness / validation |
|---|---|---|---|
| competency_id | String | Yes | Primary key |
| name | String | Yes | Unique, non-empty name |
| description | String | Optional | Descriptive text |

### 7.6 Goals

| Field | Type | Required | Uniqueness / validation |
|---|---|---|---|
| goal_id | String | Yes | Primary key; expected format GOAL-EMP-000001-00001 |
| employee_id | String | Yes | Must reference an existing employee |
| cycle_id | String | Yes | Must reference an existing review cycle |
| title | String | Yes | Non-empty goal title |
| status | String | Yes | Permitted: not_started, in_progress, completed |
| progress_percent | Integer | Yes | Percentage from 0 to 100 |
| created_date | Date | Yes | Valid date |

### 7.7 Key results

| Field | Type | Required | Uniqueness / validation |
|---|---|---|---|
| key_result_id | String | Yes | Primary key |
| goal_id | String | Yes | Must reference an existing goal |
| description | String | Yes | Non-empty description |
| target_value | Decimal | Yes | Must be greater than zero |
| current_value | Decimal | Yes | Must be zero or greater and no greater than target_value |
| unit | String | Yes | Measurement unit, such as a count or percentage |

### 7.8 Check-ins

| Field | Type | Required | Uniqueness / validation |
|---|---|---|---|
| check_in_id | String | Yes | Primary key |
| employee_id | String | Yes | Must reference an existing employee |
| cycle_id | String | Yes | Must reference an existing review cycle |
| check_in_date | Date | Yes | Valid date |
| progress_percent | Integer | Yes | Normally 0 to 100; out-of-range values without rationale are reported as expected or unexpected findings by validation |
| notes | String | Optional | Check-in notes |
| rationale | String | Optional | Explanation for reported progress; required by the validator when progress is outside 0 to 100 |

### 7.9 Reviews

| Field | Type | Required | Uniqueness / validation |
|---|---|---|---|
| review_id | String | Yes | Primary key; expected format REV-2026-000001 |
| employee_id | String | Yes | Must reference an existing employee |
| cycle_id | String | Yes | Must reference an existing review cycle |
| reviewer_id | String | Yes | Must reference an existing manager and match the employee's assigned manager under the current validator |
| score | Integer | Yes | Scale from 1 to 5 |
| status | String | Yes | Permitted: draft, submitted, approved |
| review_date | Date | Yes | Valid date |

### 7.10 Feedback

| Field | Type | Required | Uniqueness / validation |
|---|---|---|---|
| feedback_id | String | Yes | Primary key |
| employee_id | String | Yes | Must reference an existing employee |
| competency_id | String | Expected | Must reference an existing competency under the current validator |
| cycle_id | String | Yes | Must reference an existing review cycle |
| author_id | String | Expected | Must reference an existing manager under the current validator |
| evidence_reference | String | Expected | Non-empty evidence reference under the current validator |
| rating | Integer | Yes | Scale from 1 to 5 |
| comments | String | Yes | Feedback text |
| feedback_date | Date | Yes | Valid date |

The feedback validator treats a missing author or evidence reference as a finding. The deliberately injected untraceable feedback case is retained as a test fixture.

### 7.11 Development plans

| Field | Type | Required | Uniqueness / validation |
|---|---|---|---|
| development_plan_id | String | Yes | Primary key |
| employee_id | String | Yes | Must reference an existing employee |
| review_id | String | Yes | Must reference an existing review |
| objective | String | Yes | Non-empty development objective |
| action | String | Yes | Non-empty planned action |
| target_date | Date | Yes | Valid date |
| status | String | Yes | Observed value: planned; the validator does not currently enforce a development-plan status enumeration |

### 7.12 Event history

| Field | Type | Required | Uniqueness / validation |
|---|---|---|---|
| event_id | String | Yes | Primary key |
| cycle_id | String | Yes | Must reference an existing review cycle |
| entity_type | String | Yes | Entity affected by the event |
| record_id | String | Yes | Identifier of the affected record |
| event_type | String | Yes | Recorded event type |
| actor_id | String | Expected | Validator requires a non-empty actor ID |
| event_time | Timestamp | Yes | Valid timestamp |
| reason | String | Conditional | Required by the validator for an update in a closed cycle |

The current validator checks the event's cycle and reason, but does not verify that record_id references an existing record in the declared entity_type.

### 7.13 Ground truth

| Field | Type | Required | Uniqueness / validation |
|---|---|---|---|
| case_id | String | Yes | Expected unique case identifier; the validator checks the five anomaly types but does not separately enforce case_id uniqueness |
| entity_type | String | Yes | Must identify a supported entity type |
| record_id | String | Yes | Must reference an existing record of the declared entity type |
| anomaly_type | String | Yes | Exactly the five expected anomaly types must be present |
| expected_label | String | Yes | Validator expects invalid |
| description | String | Yes | Explanation of the deliberate test case |

### 7.14 Cross-dataset validation rules

The current validator checks primary-key uniqueness, required identifier values, selected foreign-key relationships, status values for review cycles/goals/reviews, numeric ranges, goal ID format and owner consistency, feedback traceability, event history rules, ground-truth references, and manifest row counts.

The current validator does not comprehensively enforce every possible field constraint. In particular, it does not currently validate every date field's format, every status enumeration, all foreign-key relationships, all date ordering, or derived goal progress against key-result values.

### 7.15 Units and interpretation

- Goal and check-in progress: percentage, normally 0-100.
- Review score: integer rating from 1-5.
- Feedback rating: integer rating from 1-5.
- Key-result values: numeric values interpreted using the associated unit field.
- Dates: calendar dates.
- Event times: timestamps.

### 7.16 Implementation note

This dictionary describes the generated CSV schema and the current validation script. A documented expectation is not necessarily enforced by the database schema or application. Where enforcement is incomplete, this document explicitly identifies the gap rather than implying that the system already prevents invalid data.
