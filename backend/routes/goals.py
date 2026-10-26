
from flask import Blueprint, jsonify, request

from models import Goal, KeyResult

goals_bp = Blueprint("goals", __name__)


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
            {
                "goal_id": goal.goal_id,
                "employee_id": goal.employee_id,
                "cycle_id": goal.cycle_id,
                "title": goal.title,
                "status": goal.status,
                "progress_percent": goal.progress_percent,
                "created_date": goal.created_date.isoformat(),
            }
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
    goal = Goal.query.filter_by(goal_id=goal_id).first()

    if goal is None:
        return jsonify({"error": "Goal not found"}), 404

    return jsonify({
        "goal_id": goal.goal_id,
        "employee_id": goal.employee_id,
        "cycle_id": goal.cycle_id,
        "title": goal.title,
        "status": goal.status,
        "progress_percent": goal.progress_percent,
        "created_date": goal.created_date.isoformat(),
        "key_results": [
            {
                "key_result_id": result.key_result_id,
                "description": result.description,
                "target_value": result.target_value,
                "current_value": result.current_value,
                "unit": result.unit,
            }
            for result in KeyResult.query.filter_by(
                goal_id=goal.goal_id
            ).all()
        ],
    })
