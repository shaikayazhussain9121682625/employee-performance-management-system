# Employee Performance Management System — Database Schema

## 1. Purpose and Scope

This document describes the implemented SQLAlchemy database schema and the relationships between its entities. The application uses SQLite through Flask-SQLAlchemy. Generated data is synthetic.

The database contains 11 tables: managers, employees, review_cycles, goals, key_results, check_ins, competencies, reviews, feedback, development_plans, and event_history.

The generated CSV/JSON datasets and the SQL seed export are documented separately. The ground-truth labels are stored in `data/generated/ground_truth.csv` and `data/generated/ground_truth.json` and must not be used as application input features.

## 2. Entities and Keys

| Entity | Primary key | Foreign keys and relationships |
|---|---|---|
| Manager | `manager_id` | One manager may supervise many employees. |
| Employee | `employee_id` | Optional `manager_id` references `managers.manager_id`. |
| ReviewCycle | `cycle_id` | One cycle may contain many goals. |
| Goal | `goal_id` | Required `employee_id` and `cycle_id`; belongs to one employee and one cycle. |
| KeyResult | `key_result_id` | Required `goal_id`; belongs to one goal. |
| CheckIn | `check_in_id` | Required `employee_id` and `cycle_id`. |
| Competency | `competency_id` | Competency name is unique. |
| Review | `review_id` | Required `employee_id`, `cycle_id`, and `reviewer_id`. Reviewer references a manager. |
| Feedback | `feedback_id` | Required `employee_id` and `cycle_id`; optional `competency_id`. |
| DevelopmentPlan | `development_plan_id` | Required `employee_id` and `review_id`. |
| EventHistory | `event_id` | Required `cycle_id`; affected entity is recorded using `entity_type` and `record_id`. |

All listed primary keys are declared by the SQLAlchemy models. Employee and manager email addresses are unique. Competency names are unique.

## 3. Relationship Cardinalities

- Manager to Employee: one-to-many; an employee may have no assigned manager because `manager_id` is nullable.
- Employee to Goal: one-to-many.
- ReviewCycle to Goal: one-to-many.
- Goal to KeyResult: one-to-many in the ORM relationship. Key results require a parent goal.
- Employee to CheckIn: one-to-many.
- ReviewCycle to CheckIn: one-to-many.
- Employee to Review: one-to-many.
- Manager to Review: one-to-many through `reviewer_id`.
- Employee to Feedback: one-to-many.
- Competency to Feedback: one-to-many; feedback may omit its competency.
- ReviewCycle to Feedback: one-to-many.
- Employee to DevelopmentPlan: one-to-many.
- Review to DevelopmentPlan: one-to-many.
- ReviewCycle to EventHistory: one-to-many.

The implemented schema does not define a direct many-to-many bridge table. A future many-to-many relationship, such as employees and peer reviewers, should use an explicit association table if it becomes a requirement.

## 4. Field Types and Nullability

The SQLAlchemy model file `backend/models/__init__.py` is the authoritative source for implemented column types and nullability.

- `String(n)`: bounded string column with the specified maximum length.
- `Text`: text column without a model-defined maximum length.
- `Date`: calendar date.
- `DateTime`: timestamp.
- `Float`: floating-point numeric value.
- `nullable=False`: required database field.
- `nullable=True`: optional database field.
- `unique=True`: unique constraint.
- `primary_key=True`: primary-key constraint.

Important optional fields include `Employee.manager_id`, `Competency.description`, `CheckIn.notes`, `CheckIn.rationale`, `Feedback.competency_id`, `Feedback.author_id`, `Feedback.evidence_reference`, `EventHistory.actor_id`, and `EventHistory.reason`.

The models do not declare database-level CHECK constraints for all status values, progress ranges, rating ranges, or date-ordering rules. Those rules must be enforced and tested in application or data-validation logic.

## 5. Lifecycle and Integrity Rules

The project requires the following business rules:

1. Primary keys must be unique and stable.
2. Foreign-key values must reference existing parent records.
3. Review-cycle end dates must not precede start dates.
4. Normal progress percentages must be within the documented percentage scale.
5. A reviewer must have an appropriate relationship to the employee.
6. Changes to a closed review cycle must not be accepted silently.
7. Feedback should preserve author attribution and supporting evidence.
8. Important state changes should be recorded with timestamps, actors, and reasons.
9. Derived values should be calculated from source records rather than assigned independently.
10. Deliberate edge cases must remain labelled and distinguishable from unexpected defects.

These are intended business rules; the existence of a model column does not mean every rule is automatically enforced by the database.

## 6. Event History and Audit Limitations

`EventHistory` contains `event_id`, `cycle_id`, `entity_type`, `record_id`, `event_type`, `actor_id`, `event_time`, and `reason`.

The `cycle_id` field has a foreign key to `review_cycles`. The combination of `entity_type` and `record_id` identifies the affected record at the application level; it is not a foreign key to every possible entity table.

The current model does not enforce append-only history, immutable event records, version sequencing, or mandatory reasons for all state changes. These capabilities must not be claimed as fully implemented without additional code and tests.

## 7. Feedback Attribution and Development Plan Approvals

Feedback currently stores `author_id` as a nullable string without a foreign-key constraint. This allows the deliberate missing-author test case, but it does not guarantee that a non-null author identifies a valid person. Reviewer type and self/manager/peer feedback type are not separate model fields.

Development plans currently store an employee, review, objective, action, target date, and status. Approval identity, approval timestamps, and approval-event history are not defined as dedicated fields in the current model.

These are documented implementation limitations, not guarantees of existing functionality.

## 8. Deliberate Edge Cases

The generated dataset includes five labelled test cases:

1. Goal identifier and recorded owner mismatch.
2. Check-in progress above the normal scale without a rationale.
3. Reviewer not matching the employee's assigned manager.
4. Feedback without author attribution and an evidence reference.
5. A change in a closed review cycle without a reason.

The corresponding ground-truth files document expected labels. Validation should report these deliberate cases separately from unexpected errors. The current validator reports findings; this does not mean all related business rules are enforced at write time.

## 9. Data and Reproducibility

- Generator: `scripts/generate_data.py`
- Validator: `scripts/validate_data.py`
- Database verification: `scripts/verify_database.py`
- SQL export: `scripts/export_sql.py`
- SQL restore verification: `scripts/verify_sql_export.py`
- Source manifest: `data/generated/source_manifest.json`
- Data dictionary: `docs/data_dictionary.md`

The configured seed is `20261022`. The generated source manifest records the generator version, seed, reference date, and synthetic-data provenance.

## 10. Known Limitations and Future Improvements

- Add explicit database or service-level validation for status enums, date ordering, progress limits, and score ranges.
- Enforce reviewer-to-employee relationship rules during review creation.
- Add an author relationship for feedback while retaining a documented way to test missing attribution.
- Introduce append-only audit events and protect history from silent modification.
- Add explicit approval records and lifecycle transitions for development plans.
- Add relationship tables if self, peer, or cross-functional reviewer assignments require many-to-many associations.
- Extend automated tests to verify each required business rule and its deliberate exception cases.
