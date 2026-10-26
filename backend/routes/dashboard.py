
from flask import Blueprint, jsonify
from sqlalchemy import func

from extensions import db
from models import (
    Employee,
    Manager,
    Goal,
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

    average_progress = db.session.query(
        func.avg(Goal.progress_percent)
    ).scalar()

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
