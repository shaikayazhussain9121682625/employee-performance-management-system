
# Employee Performance Management System — Data Schema

## 1. Purpose

This document describes the entities and relationships used by
the Employee Performance Management System.

All generated records are synthetic.

## 2. Entities

### Employee
- Primary key: employee_id
- Stores employee identity, department, job title, hire date,
  employment status, and manager relationship.

### Manager
- Primary key: manager_id
- Stores manager identity and department.

### ReviewCycle
- Primary key: cycle_id
- Stores review period, start date, end date, and lifecycle status.

### Goal
- Primary key: goal_id
- Foreign keys: employee_id, cycle_id
- Stores the employee's performance goal, status, and dates.

### KeyResult
- Primary key: key_result_id
- Foreign key: goal_id
- Stores a measurable result associated with a goal.

### CheckIn
- Primary key: check_in_id
- Foreign keys: employee_id, cycle_id
- Stores progress updates, notes, and check-in dates.

### Competency
- Primary key: competency_id
- Stores competency definitions and descriptions.

### Feedback
- Primary key: feedback_id
- Foreign keys: employee_id, competency_id, cycle_id
- Stores competency feedback, author, evidence, and date.

### Review
- Primary key: review_id
- Foreign keys: employee_id, cycle_id, reviewer_id
- Stores review decisions, scores, status, and timestamps.

### DevelopmentPlan
- Primary key: development_plan_id
- Foreign keys: employee_id, review_id
- Stores development objectives, actions, and target dates.

## 3. Relationships

- One manager can manage many employees.
- One employee can have many goals.
- One review cycle can contain many goals and check-ins.
- One goal can have many key results.
- One employee can have many check-ins.
- One competency can appear in feedback for many employees.
- One employee can have many reviews across different cycles.
- One review can have many development actions.

## 4. Integrity Rules

- Primary keys must be unique and stable.
- Foreign keys must reference existing records.
- End dates must not precede start dates.
- Progress values must stay within the defined scale.
- Reviewers must have a valid relationship to the employee.
- Closed review cycles must not accept silent edits.
- Feedback must retain author and evidence traceability.
- Changes to important records must be auditable.

## 5. Implementation Note

This is the initial conceptual schema. The final implementation
must define all fields, data types, constraints, optional
relationships, lifecycle states, and audit-history structures.
