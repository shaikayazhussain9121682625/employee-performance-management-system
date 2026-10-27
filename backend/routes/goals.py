
from datetime import datetime, timezone
import re

from flask import Blueprint, jsonify, request

from extensions import db
from models import Goal, KeyResult, EventHistory

goals_bp = Blueprint("goals", __name__)

ALLOWED_GOAL_STATUSES = {
    "not_started",
    "in_progress",
    "completed",
}


def calculate_goal_progress(goal):
    """Calculate average progress from the goal's key results."""
    results = goal.key_results

    if not results:
        return 0

    progress_values = []

    for result in results:
        if result.target_value <= 0:
            continue

        percentage = (
            result.current_value / result.target_value
        ) * 100
        progress_values.append(percentage)

    if not progress_values:
        return 0

    return round(sum(progress_values) / len(progress_values))


def serialize_goal(goal, include_key_results=False):
    """Serialize a goal using calculated progress."""
    data = {
        "goal_id": goal.goal_id,
        "employee_id": goal.employee_id,
        "cycle_id": goal.cycle_id,
        "title": goal.title,
        "status": goal.status,
        "progress_percent": calculate_goal_progress(goal),
        "created_date": goal.created_date.isoformat(),
    }

    if include_key_results:
        data["key_results"] = [
            {
                "key_result_id": result.key_result_id,
                "description": result.description,
                "target_value": result.target_value,
                "current_value": result.current_value,
                "unit": result.unit,
            }
            for result in goal.key_results
        ]

    return data


def next_event_id():
    """Generate the next zero-padded event ID."""
    existing_ids = EventHistory.query.with_entities(
        EventHistory.event_id
    ).all()

    highest_number = 0

    for (event_id,) in existing_ids:
        match = re.fullmatch(r"EVT-(\d+)", event_id)

        if match:
            highest_number = max(
                highest_number,
                int(match.group(1)),
            )

    return f"EVT-{highest_number + 1:06d}"


@goals_bp.get("/")
def list_goals():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    employee_id = request.args.get("employee_id", "").strip()
    status = request.args.get("status", "").strip()

    if page < 1:
        return jsonify({"error": "Page must be at least 1"}), 400

    if per_page < 1 or per_page > 100:
        return jsonify({
            "error": "per_page must be between 1 and 100"
        }), 400

    query = Goal.query

    if employee_id:
        query = query.filter(Goal.employee_id == employee_id)

    if status:
        query = query.filter(Goal.status == status)

    pagination = query.order_by(Goal.goal_id).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return jsonify({
        "items": [
            serialize_goal(goal)
            for goal in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        },
    })


@goals_bp.get("/<string:goal_id>")
def get_goal(goal_id):
    goal = db.session.get(Goal, goal_id)

    if goal is None:
        return jsonify({"error": "Goal not found"}), 404

    return jsonify(serialize_goal(goal, include_key_results=True))


@goals_bp.put("/<string:goal_id>")
def update_goal(goal_id):
    """Update an active-cycle goal and record the change event."""
    goal = db.session.get(Goal, goal_id)

    if goal is None:
        return jsonify({"error": "Goal not found"}), 404

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    allowed_fields = {"title", "status", "reason", "actor_id"}
    unexpected_fields = set(payload) - allowed_fields

    if unexpected_fields:
        return jsonify({
            "error": "Unsupported fields",
            "fields": sorted(unexpected_fields),
        }), 400

    # Require a reason for every goal update.
    reason = payload.get("reason")

    if not isinstance(reason, str) or not reason.strip():
        return jsonify({
            "error": "A non-empty reason is required for goal updates"
        }), 400

    # Check the review-cycle lifecycle before changing anything.
    cycle_status = (goal.cycle.status or "").strip().lower()

    if cycle_status != "active":
        return jsonify({
            "error": (
                "Goals can only be updated in an active review cycle"
            ),
            "cycle_id": goal.cycle_id,
            "cycle_status": goal.cycle.status,
        }), 409

    changes = {}

    if "title" in payload:
        title = payload["title"]

        if not isinstance(title, str) or not title.strip():
            return jsonify({
                "error": "Title must be a non-empty string"
            }), 400

        title = title.strip()

        if title != goal.title:
            changes["title"] = {
                "old": goal.title,
                "new": title,
            }

    if "status" in payload:
        status = payload["status"]

        if (
            not isinstance(status, str)
            or status not in ALLOWED_GOAL_STATUSES
        ):
            return jsonify({
                "error": "Invalid goal status",
                "allowed_values": sorted(ALLOWED_GOAL_STATUSES),
            }), 400

        if status != goal.status:
            changes["status"] = {
                "old": goal.status,
                "new": status,
            }

    if not changes:
        return jsonify({
            "error": "No changes were provided"
        }), 400

    actor_id = payload.get("actor_id")

    if actor_id is not None and (
        not isinstance(actor_id, str) or not actor_id.strip()
    ):
        return jsonify({
            "error": "actor_id must be a non-empty string"
        }), 400

    event = EventHistory(
        event_id=next_event_id(),
        cycle_id=goal.cycle_id,
        entity_type="goal",
        record_id=goal.goal_id,
        event_type="updated",
        actor_id=actor_id.strip() if actor_id else None,
        event_time=datetime.now(timezone.utc),
        reason=reason.strip(),
    )

    try:
        if "title" in changes:
            goal.title = changes["title"]["new"]

        if "status" in changes:
            goal.status = changes["status"]["new"]

        db.session.add(event)
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "message": "Goal updated successfully",
        "goal": serialize_goal(goal),
        "changes": changes,
        "event": {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "reason": event.reason,
        },
    }), 200

@goals_bp.put("/<string:goal_id>/key-results/<string:key_result_id>")
def update_key_result(goal_id, key_result_id):
    """Update a key result, recalculate goal progress, and audit the change."""
    goal = db.session.get(Goal, goal_id)

    if goal is None:
        return jsonify({"error": "Goal not found"}), 404

    key_result = db.session.get(KeyResult, key_result_id)

    if key_result is None or key_result.goal_id != goal_id:
        return jsonify({
            "error": "Key result not found for this goal"
        }), 404

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    allowed_fields = {"current_value", "reason", "actor_id"}
    unexpected = set(payload) - allowed_fields

    if unexpected:
        return jsonify({
            "error": "Unsupported fields",
            "fields": sorted(unexpected),
        }), 400

    value = payload.get("current_value")

    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not __import__("math").isfinite(value)
        or value < 0
    ):
        return jsonify({
            "error": "current_value must be a finite, non-negative number"
        }), 400

    reason = payload.get("reason")

    if not isinstance(reason, str) or not reason.strip():
        return jsonify({
            "error": "A non-empty reason is required"
        }), 400

    actor_id = payload.get("actor_id")

    if actor_id is not None and (
        not isinstance(actor_id, str) or not actor_id.strip()
    ):
        return jsonify({
            "error": "actor_id must be a non-empty string"
        }), 400

    cycle_status = (goal.cycle.status or "").strip().lower()

    if cycle_status != "active":
        return jsonify({
            "error": "Key results can only be updated in an active review cycle",
            "cycle_status": goal.cycle.status,
        }), 409

    if key_result.target_value <= 0:
        return jsonify({
            "error": "Key result target_value must be greater than zero"
        }), 409

    if value > key_result.target_value and not reason.strip():
        return jsonify({
            "error": "A rationale is required when progress exceeds the target"
        }), 400

    old_value = key_result.current_value
    new_value = float(value)

    if old_value == new_value:
        return jsonify({"error": "No change to current_value"}), 400

    # Store the before-and-after values in the audit reason.
    audit_reason = (
        f"{reason.strip()} | current_value: {old_value} -> {new_value}"
    )

    event = EventHistory(
        event_id=next_event_id(),
        cycle_id=goal.cycle_id,
        entity_type="key_result",
        record_id=key_result.key_result_id,
        event_type="updated",
        actor_id=actor_id.strip() if actor_id else None,
        event_time=datetime.now(timezone.utc),
        reason=audit_reason,
    )

    try:
        key_result.current_value = new_value
        db.session.add(event)
        db.session.flush()

        progress = calculate_goal_progress(goal)

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "message": "Key result updated successfully",
        "key_result": {
            "key_result_id": key_result.key_result_id,
            "goal_id": goal.goal_id,
            "old_current_value": old_value,
            "current_value": key_result.current_value,
            "target_value": key_result.target_value,
        },
        "goal_progress_percent": progress,
        "event": {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "reason": event.reason,
        },
    }), 200
