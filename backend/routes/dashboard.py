
from flask import Blueprint, jsonify
from sqlalchemy import case, func

from extensions import db
from models import (
    Employee,
    Manager,
    Goal,
    KeyResult,
    CheckIn,
    Review,
)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/summary")
def dashboard_summary():
    total_employees = Employee.query.count()
    total_managers = Manager.query.count()
    total_goals = Goal.query.count()
    total_check_ins = CheckIn.query.count()
    total_reviews = Review.query.count()

    completed_goals = Goal.query.filter_by(
        status="completed"
    ).count()

    in_progress_goals = Goal.query.filter_by(
        status="in_progress"
    ).count()

    not_started_goals = Goal.query.filter_by(
        status="not_started"
    ).count()

    # Calculate each goal's progress from its key results.
    # Key results with non-positive targets are excluded,
    # matching the goal API's calculation rule.
    progress_by_goal = (
        db.session.query(
            KeyResult.goal_id.label("goal_id"),
            func.avg(
                case(
                    (
                        KeyResult.target_value > 0,
                        (
                            KeyResult.current_value
                            / KeyResult.target_value
                        ) * 100,
                    ),
                    else_=None,
                )
            ).label("progress"),
        )
        .group_by(KeyResult.goal_id)
        .subquery()
    )

    # Include goals without key results as 0 progress.
    average_progress = (
        db.session.query(
            func.avg(
                func.coalesce(progress_by_goal.c.progress, 0.0)
            )
        )
        .select_from(Goal)
        .outerjoin(
            progress_by_goal,
            Goal.goal_id == progress_by_goal.c.goal_id,
        )
        .scalar()
    )

    department_counts = (
        db.session.query(
            Employee.department,
            func.count(Employee.employee_id),
        )
        .group_by(Employee.department)
        .order_by(Employee.department)
        .all()
    )

    return jsonify({
        "totals": {
            "employees": total_employees,
            "managers": total_managers,
            "goals": total_goals,
            "check_ins": total_check_ins,
            "reviews": total_reviews,
        },
        "goals": {
            "completed": completed_goals,
            "in_progress": in_progress_goals,
            "not_started": not_started_goals,
        },
        "average_goal_progress": round(
            float(average_progress or 0), 2
        ),
        "employees_by_department": [
            {
                "department": department,
                "count": count,
            }
            for department, count in department_counts
        ],
    })
