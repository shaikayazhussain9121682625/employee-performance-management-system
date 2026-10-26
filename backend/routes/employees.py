
from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from extensions import db
from models import Employee

employees_bp = Blueprint("employees", __name__)


@employees_bp.get("/")
def list_employees():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("search", "").strip()

    if page < 1:
        return jsonify({"error": "Page must be at least 1"}), 400

    if per_page < 1 or per_page > 100:
        return jsonify({
            "error": "per_page must be between 1 and 100"
        }), 400

    query = Employee.query

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Employee.employee_id.ilike(term),
                Employee.full_name.ilike(term),
                Employee.department.ilike(term),
                Employee.job_title.ilike(term),
            )
        )

    pagination = query.order_by(
        Employee.employee_id
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return jsonify({
        "items": [
            {
                "employee_id": employee.employee_id,
                "full_name": employee.full_name,
                "email": employee.email,
                "department": employee.department,
                "job_title": employee.job_title,
                "hire_date": employee.hire_date.isoformat(),
                "employment_status": employee.employment_status,
                "manager_id": employee.manager_id,
            }
            for employee in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        },
    })


@employees_bp.get("/<string:employee_id>")
def get_employee(employee_id):
    employee = db.session.get(Employee, employee_id)

    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify({
        "employee_id": employee.employee_id,
        "full_name": employee.full_name,
        "email": employee.email,
        "department": employee.department,
        "job_title": employee.job_title,
        "hire_date": employee.hire_date.isoformat(),
        "employment_status": employee.employment_status,
        "manager_id": employee.manager_id,
    })
