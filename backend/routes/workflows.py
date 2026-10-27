from datetime import date, datetime, timezone
import re
import math

from flask import Blueprint, jsonify, request

from extensions import db
from models import (
    Employee, Manager, ReviewCycle, CheckIn, Feedback, Review,
    DevelopmentPlan, EventHistory, Competency,
)

workflows_bp = Blueprint("workflows", __name__)

ALLOWED_FEEDBACK_TYPES = {"manager", "peer", "self", "direct_report"}
ALLOWED_REVIEW_STATUSES = {"draft", "submitted", "completed"}
ALLOWED_PLAN_STATUSES = {"not_started", "in_progress", "completed"}
ALLOWED_APPROVAL_STATUSES = {"approved", "rejected"}


def next_id(model, field_name, prefix):
    values = db.session.query(getattr(model, field_name)).all()
    highest = 0
    for (value,) in values:
        match = re.fullmatch(re.escape(prefix) + r"-(\d+)", value or "")
        if match:
            highest = max(highest, int(match.group(1)))
    return f"{prefix}-{highest + 1:06d}"


def parse_date(value, field_name):
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a date in YYYY-MM-DD format")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{field_name} must be a valid YYYY-MM-DD date")


def get_payload():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, (jsonify({"error": "Request body must be a JSON object"}), 400)
    return payload, None


def require_active_cycle(cycle_id):
    cycle = db.session.get(ReviewCycle, cycle_id)
    if cycle is None:
        return None, (jsonify({"error": "Review cycle not found"}), 404)
    if (cycle.status or "").strip().lower() != "active":
        return None, (jsonify({
            "error": "This operation requires an active review cycle",
            "cycle_status": cycle.status,
        }), 409)
    return cycle, None


def record_event(cycle_id, entity_type, record_id, event_type, actor_id, reason):
    event = EventHistory(
        event_id=next_id(EventHistory, "event_id", "EVT"),
        cycle_id=cycle_id,
        entity_type=entity_type,
        record_id=record_id,
        event_type=event_type,
        actor_id=actor_id,
        event_time=datetime.now(timezone.utc),
        reason=reason,
    )
    db.session.add(event)
    return event


def commit_or_rollback():
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


@workflows_bp.get("/check-ins")
def list_check_ins():
    employee_id = request.args.get("employee_id", "").strip()
    cycle_id = request.args.get("cycle_id", "").strip()
    query = CheckIn.query
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if cycle_id:
        query = query.filter_by(cycle_id=cycle_id)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    if page < 1 or not 1 <= per_page <= 100:
        return jsonify({"error": "page must be positive and per_page must be 1–100"}), 400

    result = query.order_by(CheckIn.check_in_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "items": [{
            "check_in_id": item.check_in_id,
            "employee_id": item.employee_id,
            "cycle_id": item.cycle_id,
            "check_in_date": item.check_in_date.isoformat(),
            "progress_percent": item.progress_percent,
            "notes": item.notes,
            "rationale": item.rationale,
        } for item in result.items],
        "pagination": {
            "page": result.page, "per_page": result.per_page,
            "total": result.total, "pages": result.pages,
        },
    })


@workflows_bp.post("/check-ins")
def create_check_in():
    payload, error = get_payload()
    if error:
        return error

    required = {"employee_id", "cycle_id", "progress_percent"}
    missing = required - payload.keys()
    if missing:
        return jsonify({"error": "Missing required fields", "fields": sorted(missing)}), 400

    employee = db.session.get(Employee, payload["employee_id"])
    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    cycle, error = require_active_cycle(payload["cycle_id"])
    if error:
        return error

    progress = payload["progress_percent"]
    if isinstance(progress, bool) or not isinstance(progress, (int, float)) or not math.isfinite(progress):
        return jsonify({"error": "progress_percent must be a finite number"}), 400

    rationale = payload.get("rationale")
    if progress < 0 or progress > 100:
        if not isinstance(rationale, str) or not rationale.strip():
            return jsonify({"error": "A rationale is required when progress is outside 0–100"}), 400

    try:
        check_in_date = parse_date(payload.get("check_in_date", date.today().isoformat()), "check_in_date")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if check_in_date < cycle.start_date or check_in_date > cycle.end_date:
        return jsonify({"error": "Check-in date must fall within the review cycle"}), 400

    actor_id = payload.get("actor_id")
    if actor_id is not None and (not isinstance(actor_id, str) or not actor_id.strip()):
        return jsonify({"error": "actor_id must be a non-empty string"}), 400

    item = CheckIn(
        check_in_id=next_id(CheckIn, "check_in_id", "CHK"),
        employee_id=employee.employee_id,
        cycle_id=cycle.cycle_id,
        check_in_date=check_in_date,
        progress_percent=float(progress),
        notes=payload.get("notes"),
        rationale=rationale,
    )

    try:
        db.session.add(item)
        record_event(cycle.cycle_id, "check_in", item.check_in_id, "created",
                     actor_id.strip() if actor_id else None, "Check-in created")
        commit_or_rollback()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "message": "Check-in created",
        "check_in_id": item.check_in_id,
        "employee_id": item.employee_id,
        "cycle_id": item.cycle_id,
        "progress_percent": item.progress_percent,
    }), 201

@workflows_bp.get("/feedback")
def list_feedback():
    employee_id = request.args.get("employee_id", "").strip()
    cycle_id = request.args.get("cycle_id", "").strip()

    query = Feedback.query

    if employee_id:
        query = query.filter_by(employee_id=employee_id)

    if cycle_id:
        query = query.filter_by(cycle_id=cycle_id)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    if page < 1 or not 1 <= per_page <= 100:
        return jsonify({
            "error": "page must be positive and per_page must be 1–100"
        }), 400

    result = query.order_by(Feedback.feedback_date.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return jsonify({
        "items": [
            {
                "feedback_id": item.feedback_id,
                "employee_id": item.employee_id,
                "cycle_id": item.cycle_id,
                "author_id": item.author_id,
                "feedback_type": item.feedback_type,
                "competency_id": item.competency_id,
                "rating": item.rating,
                "comments": item.comments,
                "evidence_reference": item.evidence_reference,
                "feedback_date": item.feedback_date.isoformat(),
            }
            for item in result.items
        ],
        "pagination": {
            "page": result.page,
            "per_page": result.per_page,
            "total": result.total,
            "pages": result.pages,
        },
    })



@workflows_bp.post("/feedback")
def create_feedback():
    payload, error = get_payload()
    if error:
        return error

    required = {"employee_id", "cycle_id", "rating", "comments", "author_id", "feedback_type"}
    missing = required - payload.keys()
    if missing:
        return jsonify({"error": "Missing required fields", "fields": sorted(missing)}), 400

    employee = db.session.get(Employee, payload["employee_id"])
    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    cycle, error = require_active_cycle(payload["cycle_id"])
    if error:
        return error

    author_id = payload["author_id"]
    if not isinstance(author_id, str) or not author_id.strip():
        return jsonify({"error": "Feedback must have a traceable author_id"}), 400

    # An author must correspond to a known employee or manager.
    if not (
        db.session.get(Employee, author_id)
        or db.session.get(Manager, author_id)
    ):
        return jsonify({"error": "author_id must identify an existing employee or manager"}), 400

    feedback_type = payload["feedback_type"]
    if feedback_type not in ALLOWED_FEEDBACK_TYPES:
        return jsonify({
            "error": "Invalid feedback_type",
            "allowed_values": sorted(ALLOWED_FEEDBACK_TYPES),
        }), 400

    rating = payload["rating"]
    if isinstance(rating, bool) or not isinstance(rating, (int, float)) or not math.isfinite(rating) or not 1 <= rating <= 5:
        return jsonify({"error": "rating must be a number from 1 to 5"}), 400

    comments = payload["comments"]
    if not isinstance(comments, str) or not comments.strip():
        return jsonify({"error": "comments must not be empty"}), 400

    competency_id = payload.get("competency_id")
    if competency_id and db.session.get(Competency, competency_id) is None:
        return jsonify({"error": "Competency not found"}), 404

    try:
        feedback_date = parse_date(payload.get("feedback_date", date.today().isoformat()), "feedback_date")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not cycle.start_date <= feedback_date <= cycle.end_date:
        return jsonify({"error": "Feedback date must fall within the review cycle"}), 400

    item = Feedback(
        feedback_id=next_id(Feedback, "feedback_id", "FB"),
        employee_id=employee.employee_id,
        competency_id=competency_id,
        cycle_id=cycle.cycle_id,
        author_id=author_id.strip(),
        feedback_type=feedback_type,
        evidence_reference=payload.get("evidence_reference"),
        rating=float(rating),
        comments=comments.strip(),
        feedback_date=feedback_date,
    )

    try:
        db.session.add(item)
        record_event(cycle.cycle_id, "feedback", item.feedback_id, "created",
                     author_id.strip(), "Feedback created")
        commit_or_rollback()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({"message": "Feedback created", "feedback_id": item.feedback_id}), 201


@workflows_bp.get("/reviews")
def list_reviews():
    employee_id = request.args.get("employee_id", "").strip()
    cycle_id = request.args.get("cycle_id", "").strip()
    query = Review.query
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if cycle_id:
        query = query.filter_by(cycle_id=cycle_id)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    if page < 1 or not 1 <= per_page <= 100:
        return jsonify({"error": "page must be positive and per_page must be 1–100"}), 400

    result = query.order_by(Review.review_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "items": [{
            "review_id": item.review_id,
            "employee_id": item.employee_id,
            "cycle_id": item.cycle_id,
            "reviewer_id": item.reviewer_id,
            "score": item.score,
            "status": item.status,
            "review_date": item.review_date.isoformat(),
        } for item in result.items],
        "pagination": {
            "page": result.page, "per_page": result.per_page,
            "total": result.total, "pages": result.pages,
        },
    })


@workflows_bp.post("/reviews")
def create_review():
    payload, error = get_payload()
    if error:
        return error

    required = {"employee_id", "cycle_id", "reviewer_id", "score"}
    missing = required - payload.keys()
    if missing:
        return jsonify({"error": "Missing required fields", "fields": sorted(missing)}), 400

    employee = db.session.get(Employee, payload["employee_id"])
    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    cycle, error = require_active_cycle(payload["cycle_id"])
    if error:
        return error

    reviewer_id = payload["reviewer_id"]
    if db.session.get(Manager, reviewer_id) is None:
        return jsonify({"error": "Reviewer manager not found"}), 404
    if employee.manager_id != reviewer_id:
        return jsonify({"error": "Reviewer is not the employee's assigned manager"}), 403

    score = payload["score"]
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 5:
        return jsonify({"error": "score must be a number from 0 to 5"}), 400

    try:
        review_date = parse_date(payload.get("review_date", date.today().isoformat()), "review_date")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    if not cycle.start_date <= review_date <= cycle.end_date:
        return jsonify({"error": "Review date must fall within the review cycle"}), 400

    item = Review(
        review_id=next_id(Review, "review_id", "REV"),
        employee_id=employee.employee_id,
        cycle_id=cycle.cycle_id,
        reviewer_id=reviewer_id,
        score=float(score),
        status="draft",
        review_date=review_date,
    )
    try:
        db.session.add(item)
        record_event(cycle.cycle_id, "review", item.review_id, "created",
                     reviewer_id, "Review created")
        commit_or_rollback()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({"message": "Review created", "review_id": item.review_id, "status": item.status}), 201


@workflows_bp.patch("/reviews/<string:review_id>")
def update_review_status(review_id):
    item = db.session.get(Review, review_id)
    if item is None:
        return jsonify({"error": "Review not found"}), 404

    payload, error = get_payload()
    if error:
        return error

    allowed = {"status", "actor_id", "reason"}
    if set(payload) - allowed:
        return jsonify({"error": "Only status, actor_id, and reason are allowed"}), 400

    new_status = payload.get("status")
    if new_status not in ALLOWED_REVIEW_STATUSES:
        return jsonify({"error": "Invalid review status", "allowed_values": sorted(ALLOWED_REVIEW_STATUSES)}), 400

    actor_id = payload.get("actor_id")
    if actor_id != item.reviewer_id:
        return jsonify({"error": "Only the assigned reviewer can change this review"}), 403

    reason = payload.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        return jsonify({"error": "A non-empty reason is required"}), 400

    cycle, error = require_active_cycle(item.cycle_id)
    if error:
        return error

    old_status = item.status
    if old_status == new_status:
        return jsonify({"error": "Review already has this status"}), 400

    if old_status == "completed":
        return jsonify({"error": "Completed reviews cannot be changed"}), 409

    item.status = new_status
    try:
        record_event(item.cycle_id, "review", item.review_id, "status_changed",
                     actor_id, f"{reason.strip()} | status: {old_status} -> {new_status}")
        commit_or_rollback()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({"message": "Review status updated", "review_id": item.review_id, "status": item.status})


@workflows_bp.get("/development-plans")
def list_development_plans():
    employee_id = request.args.get("employee_id", "").strip()
    approval_status = request.args.get("approval_status", "").strip()
    query = DevelopmentPlan.query
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if approval_status:
        query = query.filter_by(approval_status=approval_status)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    if page < 1 or not 1 <= per_page <= 100:
        return jsonify({"error": "page must be positive and per_page must be 1–100"}), 400

    result = query.order_by(DevelopmentPlan.target_date).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "items": [{
            "development_plan_id": item.development_plan_id,
            "employee_id": item.employee_id,
            "review_id": item.review_id,
            "objective": item.objective,
            "action": item.action,
            "target_date": item.target_date.isoformat(),
            "status": item.status,
            "approval_status": item.approval_status,
            "approved_by": item.approved_by,
            "approved_at": item.approved_at.isoformat() if item.approved_at else None,
        } for item in result.items],
        "pagination": {
            "page": result.page, "per_page": result.per_page,
            "total": result.total, "pages": result.pages,
        },
    })


@workflows_bp.post("/development-plans")
def create_development_plan():
    payload, error = get_payload()
    if error:
        return error

    required = {"employee_id", "review_id", "objective", "action", "target_date"}
    missing = required - payload.keys()
    if missing:
        return jsonify({"error": "Missing required fields", "fields": sorted(missing)}), 400

    employee = db.session.get(Employee, payload["employee_id"])
    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    review = db.session.get(Review, payload["review_id"])
    if review is None:
        return jsonify({"error": "Review not found"}), 404
    if review.employee_id != employee.employee_id:
        return jsonify({"error": "Development plan employee must match the review employee"}), 400

    cycle, error = require_active_cycle(review.cycle_id)
    if error:
        return error

    objective, action = payload["objective"], payload["action"]
    if not isinstance(objective, str) or not objective.strip():
        return jsonify({"error": "objective must not be empty"}), 400
    if not isinstance(action, str) or not action.strip():
        return jsonify({"error": "action must not be empty"}), 400

    try:
        target_date = parse_date(payload["target_date"], "target_date")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    if target_date < cycle.start_date:
        return jsonify({"error": "target_date cannot precede the review cycle start date"}), 400

    actor_id = payload.get("actor_id")
    item = DevelopmentPlan(
        development_plan_id=next_id(DevelopmentPlan, "development_plan_id", "DP"),
        employee_id=employee.employee_id,
        review_id=review.review_id,
        objective=objective.strip(),
        action=action.strip(),
        target_date=target_date,
        status="not_started",
        approval_status="pending",
    )
    try:
        db.session.add(item)
        record_event(cycle.cycle_id, "development_plan", item.development_plan_id,
                     "created", actor_id, "Development plan created")
        commit_or_rollback()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "message": "Development plan created",
        "development_plan_id": item.development_plan_id,
        "approval_status": item.approval_status,
    }), 201


@workflows_bp.patch("/development-plans/<string:plan_id>/approval")
def decide_development_plan(plan_id):
    item = db.session.get(DevelopmentPlan, plan_id)
    if item is None:
        return jsonify({"error": "Development plan not found"}), 404

    payload, error = get_payload()
    if error:
        return error

    if set(payload) - {"approval_status", "manager_id", "reason"}:
        return jsonify({"error": "Only approval_status, manager_id, and reason are allowed"}), 400

    decision = payload.get("approval_status")
    manager_id = payload.get("manager_id")
    reason = payload.get("reason")

    if decision not in ALLOWED_APPROVAL_STATUSES:
        return jsonify({"error": "approval_status must be approved or rejected"}), 400
    if not isinstance(reason, str) or not reason.strip():
        return jsonify({"error": "A non-empty reason is required"}), 400

    manager = db.session.get(Manager, manager_id) if isinstance(manager_id, str) else None
    if manager is None:
        return jsonify({"error": "Manager not found"}), 404

    employee = db.session.get(Employee, item.employee_id)
    if employee is None or employee.manager_id != manager.manager_id:
        return jsonify({"error": "Only the employee's assigned manager can decide this plan"}), 403

    review = db.session.get(Review, item.review_id)
    if review is None:
        return jsonify({"error": "Related review not found"}), 409

    cycle, error = require_active_cycle(review.cycle_id)
    if error:
        return error

    if item.approval_status != "pending":
        return jsonify({"error": "Only pending plans can be approved or rejected"}), 409

    old_status = item.approval_status
    item.approval_status = decision
    item.approved_by = manager.manager_id
    item.approved_at = datetime.now(timezone.utc)
    try:
        record_event(cycle.cycle_id, "development_plan", item.development_plan_id,
                     "approval_decided", manager.manager_id,
                     f"{reason.strip()} | approval_status: {old_status} -> {decision}")
        commit_or_rollback()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "message": f"Development plan {decision}",
        "development_plan_id": item.development_plan_id,
        "approval_status": item.approval_status,
        "approved_by": item.approved_by,
        "approved_at": item.approved_at.isoformat() if item.approved_at else None,
    })
