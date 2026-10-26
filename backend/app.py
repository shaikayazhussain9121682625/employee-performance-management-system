
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db
import models 
from routes.employees import employees_bp 
from routes.goals import goals_bp 
from routes.dashboard import dashboard_bp 
from routes.exceptions import exceptions_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    app.register_blueprint(employees_bp, url_prefix="/api/employees") 
    app.register_blueprint(goals_bp, url_prefix="/api/goals") 
    app.register_blueprint(
    dashboard_bp,
    url_prefix="/api/dashboard",
)
    
    app.register_blueprint(
    exceptions_bp,
    url_prefix="/api/exceptions",
)

    @app.get("/")
    def home():
        return jsonify({
            "message": "Employee Performance Management System API",
            "status": "running"
        })

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "healthy",
            "service": "employee-performance-backend"
        })

    return app


app = create_app()

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
