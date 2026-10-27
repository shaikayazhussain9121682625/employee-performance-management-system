
import { useEffect, useState } from "react";
import "./App.css";
import WorkflowPanel from "./WorkflowPanel";

const API = "http://127.0.0.1:5000";

function App() {
  const [summary, setSummary] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [exceptions, setExceptions] = useState([]);
  const [exceptionCounts, setExceptionCounts] = useState({
    high: 0,
    medium: 0,
    low: 0,
  });
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const [summaryResponse, employeeResponse, exceptionResponse] =
          await Promise.all([
            fetch(`${API}/api/dashboard/summary`),
            fetch(`${API}/api/employees/?page=1&per_page=10`),
            fetch(`${API}/api/exceptions/`),
          ]);

        if (
          !summaryResponse.ok ||
          !employeeResponse.ok ||
          !exceptionResponse.ok
        ) {
          throw new Error("Unable to load dashboard data.");
        }

        const summaryData = await summaryResponse.json();
        const employeeData = await employeeResponse.json();
        const exceptionData = await exceptionResponse.json();

        setSummary(summaryData);
        setEmployees(employeeData.items);
        setExceptions(exceptionData.items);
        setExceptionCounts(exceptionData.severity_counts);
      } catch {
        setError(
          "Could not load dashboard data. Make sure Flask is running on port 5000 and all API routes are registered."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  async function searchEmployees(event) {
    event.preventDefault();

    try {
      setError("");

      const params = new URLSearchParams({
        page: "1",
        per_page: "10",
        search,
      });

      const response = await fetch(
        `${API}/api/employees/?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error("Employee search failed.");
      }

      const data = await response.json();
      setEmployees(data.items);
    } catch {
      setError("Unable to search employees. Please try again.");
    }
  }

  if (loading) {
    return <div className="loading">Loading performance dashboard...</div>;
  }

  if (!summary) {
    return (
      <main className="page">
        <h1>Employee Performance</h1>
        <p className="error">{error || "Dashboard data is unavailable."}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </main>
    );
  }

  const cards = [
    { label: "Total Employees", value: summary.totals.employees },
    { label: "Managers", value: summary.totals.managers },
    { label: "Performance Goals", value: summary.totals.goals },
    { label: "Check-ins", value: summary.totals.check_ins },
  ];

  return (
    <main className="page">
      <header className="header">
        <div>
          <p className="eyebrow">PEOPLE ANALYTICS</p>
          <h1>Employee Performance</h1>
          <p className="subtitle">
            Track goals, review progress, and support employee development.
          </p>
        </div>
        <div className="status">
          <span className="status-dot" />
          Backend connected
        </div>
      </header>

      {error && <p className="error">{error}</p>}

      <section className="metrics">
        {cards.map((card) => (
          <article className="metric-card" key={card.label}>
            <p>{card.label}</p>
            <h2>{card.value.toLocaleString()}</h2>
          </article>
        ))}
      </section>

      <section className="content-grid">
        <article className="panel progress-panel">
          <h2>Goal Progress</h2>
          <p className="muted">Average progress across all recorded goals</p>

          <div className="progress-value">
            {summary.average_goal_progress}%
          </div>

          <div
            className="progress-track"
            role="progressbar"
            aria-label="Average goal progress"
            aria-valuenow={summary.average_goal_progress}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div
              className="progress-fill"
              style={{
                width: `${Math.max(
                  0,
                  Math.min(100, summary.average_goal_progress)
                )}%`,
              }}
            />
          </div>

          <div className="goal-statuses">
            <div>
              <span className="status-dot green" />
              Completed
              <strong>{summary.goals.completed.toLocaleString()}</strong>
            </div>
            <div>
              <span className="status-dot blue" />
              In progress
              <strong>{summary.goals.in_progress.toLocaleString()}</strong>
            </div>
            <div>
              <span className="status-dot gray" />
              Not started
              <strong>{summary.goals.not_started.toLocaleString()}</strong>
            </div>
          </div>
        </article>

        <article className="panel department-panel">
          <h2>Employees by Department</h2>
          <p className="muted">Employee distribution across departments</p>

          {summary.employees_by_department.map((item) => (
            <div className="department-row" key={item.department}>
              <div className="department-label">
                <span>{item.department}</span>
                <strong>{item.count.toLocaleString()}</strong>
              </div>
              <div className="department-track">
                <div
                  className="department-fill"
                  style={{
                    width: `${
                      (item.count /
                        Math.max(
                          ...summary.employees_by_department.map(
                            (department) => department.count
                          ),
                          1
                        )) *
                      100
                    }%`,
                  }}
                />
              </div>
            </div>
          ))}
        </article>
      </section>
      <WorkflowPanel />

      <section className="panel exceptions-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">DATA QUALITY</p>
            <h2>Exceptions &amp; Review Queue</h2>
            <p className="muted">
              Records that need verification before any correction.
            </p>
          </div>
          <div className="exception-total">
            <strong>{exceptions.length}</strong>
            <span>Detected</span>
          </div>
        </div>

        <div className="exception-summary">
          <div className="severity-card high-severity">
            <span>High severity</span>
            <strong>{exceptionCounts.high}</strong>
          </div>
          <div className="severity-card medium-severity">
            <span>Medium severity</span>
            <strong>{exceptionCounts.medium}</strong>
          </div>
          <div className="severity-card low-severity">
            <span>Low severity</span>
            <strong>{exceptionCounts.low}</strong>
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Severity</th>
                <th>Rule</th>
                <th>Record ID</th>
                <th>Issue</th>
                <th>Recommended action</th>
              </tr>
            </thead>
            <tbody>
              {exceptions.map((item) => (
                <tr key={item.exception_id}>
                  <td>
                    <span
                      className={`severity-badge ${item.severity.toLowerCase()}`}
                    >
                      {item.severity}
                    </span>
                  </td>
                  <td>{item.rule}</td>
                  <td>{item.record_id}</td>
                  <td>{item.message}</td>
                  <td>{item.recommended_action}</td>
                </tr>
              ))}
              {exceptions.length === 0 && (
                <tr>
                  <td colSpan="5" className="empty-state">
                    No exceptions detected.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <p className="exception-note">
          These findings are rule-based. The system does not automatically
          change records; authorized people should review the evidence first.
        </p>
      </section>

      <section className="panel employees-panel">
        <div className="section-heading">
          <div>
            <h2>Employees</h2>
            <p className="muted">Browse employee records from the database</p>
          </div>
          <form className="search-form" onSubmit={searchEmployees}>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search name, ID, department..."
              aria-label="Search employees"
            />
            <button type="submit">Search</button>
          </form>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Employee</th>
                <th>Employee ID</th>
                <th>Department</th>
                <th>Job Title</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((employee) => (
                <tr key={employee.employee_id}>
                  <td>
                    <div className="employee-name">
                      <span className="avatar">
                        {employee.full_name.charAt(0)}
                      </span>
                      <span>{employee.full_name}</span>
                    </div>
                  </td>
                  <td>{employee.employee_id}</td>
                  <td>{employee.department}</td>
                  <td>{employee.job_title}</td>
                  <td>
                    <span className="employee-status">
                      {employee.employment_status}
                    </span>
                  </td>
                </tr>
              ))}
              {employees.length === 0 && (
                <tr>
                  <td colSpan="5" className="empty-state">
                    No employees found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <footer>
        Employee Performance Management System
        <span>Built with React, Flask, and SQLite</span>
      </footer>
    </main>
  );
}

export default App;
