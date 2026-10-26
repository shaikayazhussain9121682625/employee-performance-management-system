
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

sys.path.insert(0, BACKEND_DIR)

from app import app


class EmployeePerformanceAPITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_home_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["status"],
            "running"
        )

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["status"],
            "healthy"
        )

    def test_dashboard_summary(self):
        response = self.client.get("/api/dashboard/summary")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["totals"]["employees"], 3000)
        self.assertEqual(data["totals"]["goals"], 10000)
        self.assertEqual(data["totals"]["check_ins"], 20000)

    def test_employee_list(self):
        response = self.client.get(
            "/api/employees/?page=1&per_page=10"
        )
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data["items"]), 10)

    def test_goals_endpoint(self):
        response = self.client.get(
            "/api/goals/?page=1&per_page=10"
        )
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data["items"]), 10)

    def test_exceptions_endpoint(self):
        response = self.client.get("/api/exceptions/")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["total_exceptions"], 5)
        self.assertEqual(data["severity_counts"]["high"], 4)
        self.assertEqual(data["severity_counts"]["medium"], 1)

    def test_exception_rules(self):
        response = self.client.get("/api/exceptions/")
        data = response.get_json()

        rules = {item["rule"] for item in data["items"]}

        expected_rules = {
            "GOAL_OWNER_MISMATCH",
            "INVALID_PROGRESS_WITHOUT_RATIONALE",
            "REVIEWER_NOT_ASSIGNED_MANAGER",
            "FEEDBACK_TRACEABILITY_INCOMPLETE",
            "CLOSED_CYCLE_CHANGE_WITHOUT_REASON",
        }

        self.assertTrue(expected_rules.issubset(rules))


if __name__ == "__main__":
    unittest.main(verbosity=2)
