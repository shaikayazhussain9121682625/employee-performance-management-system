
from datetime import datetime, timezone

from extensions import db


class Manager(db.Model):
    __tablename__ = "managers"

    manager_id = db.Column(db.String(20), primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    department = db.Column(db.String(80), nullable=False)

    employees = db.relationship("Employee", back_populates="manager")


class Employee(db.Model):
    __tablename__ = "employees"

    employee_id = db.Column(db.String(20), primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    department = db.Column(db.String(80), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    employment_status = db.Column(db.String(30), nullable=False)

    manager_id = db.Column(
        db.String(20),
        db.ForeignKey("managers.manager_id"),
        nullable=True,
    )

    manager = db.relationship("Manager", back_populates="employees")
    goals = db.relationship("Goal", back_populates="employee")


class ReviewCycle(db.Model):
    __tablename__ = "review_cycles"

    cycle_id = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    goals = db.relationship("Goal", back_populates="cycle")


class Competency(db.Model):
    __tablename__ = "competencies"

    competency_id = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)


class Goal(db.Model):
    __tablename__ = "goals"

    goal_id = db.Column(db.String(60), primary_key=True)

    employee_id = db.Column(
        db.String(20),
        db.ForeignKey("employees.employee_id"),
        nullable=False,
    )

    cycle_id = db.Column(
        db.String(30),
        db.ForeignKey("review_cycles.cycle_id"),
        nullable=False,
    )

    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    progress_percent = db.Column(db.Float, nullable=False)
    created_date = db.Column(db.Date, nullable=False)

    employee = db.relationship("Employee", back_populates="goals")
    cycle = db.relationship("ReviewCycle", back_populates="goals")

    key_results = db.relationship(
        "KeyResult",
        back_populates="goal",
        cascade="all, delete-orphan",
    )


class KeyResult(db.Model):
    __tablename__ = "key_results"

    key_result_id = db.Column(db.String(80), primary_key=True)

    goal_id = db.Column(
        db.String(60),
        db.ForeignKey("goals.goal_id"),
        nullable=False,
    )

    description = db.Column(db.String(255), nullable=False)
    target_value = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)

    goal = db.relationship("Goal", back_populates="key_results")


class CheckIn(db.Model):
    __tablename__ = "check_ins"

    check_in_id = db.Column(db.String(30), primary_key=True)

    employee_id = db.Column(
        db.String(20),
        db.ForeignKey("employees.employee_id"),
        nullable=False,
    )

    cycle_id = db.Column(
        db.String(30),
        db.ForeignKey("review_cycles.cycle_id"),
        nullable=False,
    )

    check_in_date = db.Column(db.Date, nullable=False)
    progress_percent = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    rationale = db.Column(db.Text, nullable=True)


class Review(db.Model):
    __tablename__ = "reviews"

    review_id = db.Column(db.String(30), primary_key=True)

    employee_id = db.Column(
        db.String(20),
        db.ForeignKey("employees.employee_id"),
        nullable=False,
    )

    cycle_id = db.Column(
        db.String(30),
        db.ForeignKey("review_cycles.cycle_id"),
        nullable=False,
    )

    reviewer_id = db.Column(
        db.String(20),
        db.ForeignKey("managers.manager_id"),
        nullable=False,
    )

    score = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), nullable=False)
    review_date = db.Column(db.Date, nullable=False)


class Feedback(db.Model):
    __tablename__ = "feedback"

    feedback_id = db.Column(db.String(30), primary_key=True)

    employee_id = db.Column(
        db.String(20),
        db.ForeignKey("employees.employee_id"),
        nullable=False,
    )

    competency_id = db.Column(
        db.String(30),
        db.ForeignKey("competencies.competency_id"),
        nullable=True,
    )

    cycle_id = db.Column(
        db.String(30),
        db.ForeignKey("review_cycles.cycle_id"),
        nullable=False,
    )

    # Nullable so the required untraceable-feedback anomaly can be represented.
    author_id = db.Column(db.String(20), nullable=True)

    # Allowed values will be validated in the workflow/API layer.
    feedback_type = db.Column(
        db.String(20),
        nullable=False,
        default="manager",
    )

    evidence_reference = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Float, nullable=False)
    comments = db.Column(db.Text, nullable=False)
    feedback_date = db.Column(db.Date, nullable=False)


class DevelopmentPlan(db.Model):
    __tablename__ = "development_plans"

    development_plan_id = db.Column(db.String(30), primary_key=True)

    employee_id = db.Column(
        db.String(20),
        db.ForeignKey("employees.employee_id"),
        nullable=False,
    )

    review_id = db.Column(
        db.String(30),
        db.ForeignKey("reviews.review_id"),
        nullable=False,
    )

    objective = db.Column(db.String(255), nullable=False)
    action = db.Column(db.Text, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), nullable=False)

    # Approval workflow.
    approval_status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
    )

    approved_by = db.Column(
        db.String(20),
        db.ForeignKey("managers.manager_id"),
        nullable=True,
    )

    approved_at = db.Column(
        db.DateTime,
        nullable=True,
    )


class EventHistory(db.Model):
    __tablename__ = "event_history"

    event_id = db.Column(db.String(30), primary_key=True)

    cycle_id = db.Column(
        db.String(30),
        db.ForeignKey("review_cycles.cycle_id"),
        nullable=False,
    )

    entity_type = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.String(80), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    actor_id = db.Column(db.String(20), nullable=True)

    event_time = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    reason = db.Column(db.Text, nullable=True)


class ManagerAssignmentHistory(db.Model):
    __tablename__ = "manager_assignment_history"

    assignment_id = db.Column(db.String(30), primary_key=True)

    employee_id = db.Column(
        db.String(20),
        db.ForeignKey("employees.employee_id"),
        nullable=False,
    )

    manager_id = db.Column(
        db.String(20),
        db.ForeignKey("managers.manager_id"),
        nullable=False,
    )

    effective_from = db.Column(db.Date, nullable=False)
    effective_to = db.Column(db.Date, nullable=True)
    reason = db.Column(db.Text, nullable=True)

    recorded_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
