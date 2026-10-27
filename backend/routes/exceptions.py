
import re

from flask import Blueprint, jsonify

from models import (
    Employee,
    Goal,
    CheckIn,
    Review,
    Feedback,
    EventHistory,
    ReviewCycle,
)

exceptions_bp = Blueprint("exceptions", __name__)


def detect_exceptions():
    findings = []

    # Rule 1: The employee ID encoded in a goal ID must match its owner.
    goal_pattern = re.compile(r"^GOAL-(EMP-\d+)-\d+$")

    for goal in Goal.query.yield_per(500):
        match = goal_pattern.match(goal.goal_id)

        if match and match.group(1) != goal.employee_id:
            findings.append({
                "exception_id": f"GOAL-OWNER-{goal.goal_id}",
                "entity_type": "goal",
                "record_id": goal.goal_id,
                "severity": "high",
                "rule": "GOAL_OWNER_MISMATCH",
                "message": (
                    f"Goal ID identifies {match.group(1)}, "
                    f"but the recorded owner is {goal.employee_id}."
                ),
                "recommended_action": (
                    "Verify the intended goal owner before correcting "
                    "the record. Preserve the original evidence."
                ),
            })

    # Rule 2: Check-in progress must be within 0-100 unless rationale exists.
    for checkin in CheckIn.query.yield_per(500):
        if (
            not 0 <= checkin.progress_percent <= 100
            and not (checkin.rationale or "").strip()
        ):
            findings.append({
                "exception_id": f"CHECKIN-PROGRESS-{checkin.check_in_id}",
                "entity_type": "check_in",
                "record_id": checkin.check_in_id,
                "severity": "high",
                "rule": "INVALID_PROGRESS_WITHOUT_RATIONALE",
                "message": (
                    f"Progress is {checkin.progress_percent}, "
                    "outside the permitted 0-100 range, with no rationale."
                ),
                "recommended_action": (
                    "Review the source update and request an explanation."
                ),
            })

    # Rule 3: A review's reviewer should match the employee's assigned manager.
    # Load employees once to avoid querying separately for every review.
    employees_by_id = {
        employee.employee_id: employee
        for employee in Employee.query.yield_per(500)
    }

    for review in Review.query.yield_per(500):
        employee = employees_by_id.get(review.employee_id)

        if employee and review.reviewer_id != employee.manager_id:
            findings.append({
                "exception_id": f"REVIEWER-MISMATCH-{review.review_id}",
                "entity_type": "review",
                "record_id": review.review_id,
                "severity": "high",
                "rule": "REVIEWER_NOT_ASSIGNED_MANAGER",
                "message": (
                    f"Reviewer {review.reviewer_id} does not match "
                    f"employee {employee.employee_id}'s assigned manager "
                    f"({employee.manager_id})."
                ),
                "recommended_action": (
                    "Verify the authorized reviewer and review policy."
                ),
            })

    # Rule 4: Feedback needs an author and an evidence reference.
    for feedback in Feedback.query.yield_per(500):
        missing = []

        if not (feedback.author_id or "").strip():
            missing.append("author")

        if not (feedback.evidence_reference or "").strip():
            missing.append("evidence reference")

        if missing:
            findings.append({
                "exception_id": f"FEEDBACK-EVIDENCE-{feedback.feedback_id}",
                "entity_type": "feedback",
                "record_id": feedback.feedback_id,
                "severity": "medium",
                "rule": "FEEDBACK_TRACEABILITY_INCOMPLETE",
                "message": "Missing " + " and ".join(missing) + ".",
                "recommended_action": (
                    "Request the missing attribution or evidence. "
                    "Do not invent missing information."
                ),
            })

    # Rule 5: Changes to goals in a closed cycle need a reason.
    closed_cycles = {
        cycle.cycle_id
        for cycle in ReviewCycle.query.filter_by(status="closed").all()
    }

    for event in EventHistory.query.yield_per(500):
        if (
            event.cycle_id in closed_cycles
            and event.entity_type == "goal"
            and event.event_type != "created"
            and not (event.reason or "").strip()
        ):
            findings.append({
                "exception_id": f"CLOSED-CYCLE-{event.event_id}",
                "entity_type": "event_history",
                "record_id": event.event_id,
                "severity": "high",
                "rule": "CLOSED_CYCLE_CHANGE_WITHOUT_REASON",
                "message": (
                    f"Goal event {event.event_id} changes a record "
                    "in a closed review cycle without a reason."
                ),
                "recommended_action": (
                    "Review the change history and request an explanation."
                ),
            })

    return findings


@exceptions_bp.get("/")
def list_exceptions():
    findings = detect_exceptions()

    severity_counts = {
        severity: sum(
            item["severity"] == severity for item in findings
        )
        for severity in ("high", "medium", "low")
    }

    return jsonify({
        "total_exceptions": len(findings),
        "severity_counts": severity_counts,
        "items": findings,
        "note": (
            "These are rule-based findings, not automatic corrections. "
            "Review each finding before taking action."
        ),
    })
