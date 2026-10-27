import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:5000";

const inputStyle = {
  width: "100%",
  boxSizing: "border-box",
  padding: "11px 12px",
  border: "1px solid #cbd5e1",
  borderRadius: "8px",
  background: "#fff",
  color: "#172033",
  fontSize: "14px",
};

const buttonStyle = {
  padding: "10px 15px",
  border: "none",
  borderRadius: "8px",
  background: "#2563eb",
  color: "#fff",
  fontWeight: 600,
  cursor: "pointer",
};

const secondaryButtonStyle = {
  ...buttonStyle,
  background: "#e2e8f0",
  color: "#334155",
};

function WorkflowPanel() {
  const [employees, setEmployees] = useState([]);
  const [employeeSearch, setEmployeeSearch] = useState("");
  const [selectedEmployeeId, setSelectedEmployeeId] = useState("");
  const [employeeDetails, setEmployeeDetails] = useState(null);

  const [reviews, setReviews] = useState([]);
  const [plans, setPlans] = useState([]);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const [activeModal, setActiveModal] = useState(null);
  const [modalData, setModalData] = useState({
    status: "submitted",
    approval_status: "approved",
    reason: "",
    actor_id: "",
    manager_id: "",
  });

  const [checkin, setCheckin] = useState({
    employee_id: "",
    cycle_id: "CYCLE-2026-H2",
    progress_percent: "",
    notes: "",
    rationale: "",
  });

  const [feedback, setFeedback] = useState({
    employee_id: "",
    cycle_id: "CYCLE-2026-H2",
    author_id: "",
    feedback_type: "peer",
    rating: "",
    comments: "",
    competency_id: "",
    evidence_reference: "",
  });

  const [review, setReview] = useState({
    employee_id: "",
    cycle_id: "CYCLE-2026-H2",
    reviewer_id: "",
    score: "",
  });

  const [plan, setPlan] = useState({
    employee_id: "",
    review_id: "",
    objective: "",
    action: "",
    target_date: "",
  });

  function showMessage(text) {
    setError("");
    setMessage(text);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function showError(text) {
    setMessage("");
    setError(text);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function request(url, options = {}) {
    const response = await fetch(`${API}${url}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(
        data.error || data.message || `Request failed (${response.status})`
      );
    }

    return data;
  }

  async function loadEmployees(search = "") {
    try {
      const params = new URLSearchParams({
        page: "1",
        per_page: "100",
      });

      if (search.trim()) params.set("search", search.trim());

      const data = await request(`/api/employees/?${params.toString()}`);
      setEmployees(data.items || []);
    } catch (err) {
      showError(`Could not load employees: ${err.message}`);
    }
  }

  async function loadWorkflowData() {
    try {
      const [reviewData, planData] = await Promise.all([
        request("/api/reviews?per_page=20"),
        request("/api/development-plans?per_page=20"),
      ]);

      setReviews(reviewData.items || []);
      setPlans(planData.items || []);
    } catch (err) {
      showError(`Could not load workflow records: ${err.message}`);
    }
  }

  useEffect(() => {
    loadEmployees();
    loadWorkflowData();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      loadEmployees(employeeSearch);
    }, 300);

    return () => clearTimeout(timer);
  }, [employeeSearch]);

  async function selectEmployee(employeeId) {
    setSelectedEmployeeId(employeeId);

    if (!employeeId) {
      setEmployeeDetails(null);
      return;
    }

    const employee =
      employees.find((item) => item.employee_id === employeeId) || null;

    setEmployeeDetails(employee);

    setCheckin((old) => ({ ...old, employee_id: employeeId }));
    setFeedback((old) => ({
      ...old,
      employee_id: employeeId,
      author_id: employee?.manager_id || old.author_id,
    }));
    setReview((old) => ({
      ...old,
      employee_id: employeeId,
      reviewer_id: employee?.manager_id || old.reviewer_id,
    }));
    setPlan((old) => ({ ...old, employee_id: employeeId }));

    try {
      const data = await request(
        `/api/employees/${encodeURIComponent(employeeId)}`
      );
      setEmployeeDetails(data.employee || data);
    } catch {
      // Keep the employee information already available in the search list.
    }
  }

  async function submitForm(event, endpoint, formData, successMessage, reset) {
    event.preventDefault();
    setMessage("");
    setError("");
    setBusy(true);

    try {
      await request(endpoint, {
        method: "POST",
        body: JSON.stringify(formData),
      });

      if (reset) reset();
      await loadWorkflowData();
      showMessage(successMessage);
    } catch (err) {
      showError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function openReviewModal(item) {
    setModalData({
      status: item.status || "submitted",
      approval_status: "approved",
      reason: "",
      actor_id: item.reviewer_id || "",
      manager_id: "",
    });

    setActiveModal({ type: "review", item });
  }

  async function openPlanModal(item) {
    let managerId = "";

    try {
      const data = await request(
        `/api/employees/${encodeURIComponent(item.employee_id)}`
      );
      const employee = data.employee || data;
      managerId = employee.manager_id || "";
    } catch {
      // The manager ID can also be entered manually in the dialog.
    }

    setModalData({
      status: "submitted",
      approval_status: "approved",
      reason: "",
      actor_id: "",
      manager_id: managerId,
    });

    setActiveModal({ type: "plan", item });
  }

  async function submitModal(event) {
    event.preventDefault();
    if (!activeModal) return;

    setBusy(true);
    setMessage("");
    setError("");

    try {
      const modal = activeModal;

      if (modal.type === "review") {
        const { item } = modal;
        await request(`/api/reviews/${encodeURIComponent(item.review_id)}`, {
          method: "PATCH",
          body: JSON.stringify({
            status: modalData.status,
            reason: modalData.reason.trim(),
            actor_id: modalData.actor_id.trim(),
          }),
        });

        setActiveModal(null);
        showMessage(`Review ${item.review_id} updated successfully.`);
      } else {
        const { item } = modal;
        await request(`/api/development-plans/${encodeURIComponent(item.plan_id)}/approval`, {
          method: "PATCH",
          body: JSON.stringify({
            approval_status: modalData.approval_status,
            manager_id: modalData.manager_id.trim(),
            reason: modalData.reason.trim(),
          }),
        });

        setActiveModal(null);
        showMessage(`Development plan ${item.plan_id} updated successfully.`);
      }

      await loadWorkflowData();
    } catch (err) {
      showError(err.message);
    } finally {
      setBusy(false);
    }
  }
  const selectedEmployeeReviews = reviews.filter(
    (item) => item.employee_id === selectedEmployeeId
  );

  const selectedEmployeePlans = plans.filter(
    (item) => item.employee_id === selectedEmployeeId
  );

  return (
    <section className="workflow-section">
      <div className="workflow-heading">
        <div>
          <h2>Employee Performance Workflows</h2>
          <p>Manage check-ins, feedback, reviews, and development plans.</p>
        </div>
      </div>

      {(message || error) && (
        <div
          className={`workflow-notice ${error ? "error-notice" : ""}`}
          role={error ? "alert" : "status"}
          aria-live="polite"
        >
          <span>{error ? "Ã¢Å¡Â Ã¯Â¸Â" : "Ã¢Å“â€œ"}</span>
          <div>{error || message}</div>
          <button
            type="button"
            onClick={() => {
              setMessage("");
              setError("");
            }}
            aria-label="Dismiss notification"
            style={{
              marginLeft: "auto",
              border: 0,
              background: "transparent",
              cursor: "pointer",
              fontSize: "18px",
            }}
          >
            Ãƒâ€”
          </button>
        </div>
      )}

      <div className="employee-picker">
        <h3>Find an Employee</h3>

        <label>
          Search by employee name or ID
          <input
            style={inputStyle}
            value={employeeSearch}
            onChange={(event) => setEmployeeSearch(event.target.value)}
            placeholder="Search employees..."
          />
        </label>

        <label>
          Select employee
          <select
            style={inputStyle}
            value={selectedEmployeeId}
            onChange={(event) => selectEmployee(event.target.value)}
          >
            <option value="">Choose an employee</option>
            {employees.map((employee) => (
              <option
                key={employee.employee_id}
                value={employee.employee_id}
              >
                {employee.full_name} Ã¢â‚¬â€ {employee.employee_id}
              </option>
            ))}
          </select>
        </label>

        {employeeDetails && (
          <div className="employee-profile">
            <strong>{employeeDetails.full_name}</strong>
            <div>Employee ID: {employeeDetails.employee_id}</div>
            <div>Email: {employeeDetails.email || "Not available"}</div>
            <div>Department: {employeeDetails.department || "Not available"}</div>
            <div>Job title: {employeeDetails.job_title || "Not available"}</div>
            <div>
              Assigned manager ID:{" "}
              {employeeDetails.manager_id || "Not assigned"}
            </div>
            <div>
              Employment status:{" "}
              {employeeDetails.employment_status || "Not available"}
            </div>
          </div>
        )}
      </div>

      <div className="workflow-grid">
        <form
          className="workflow-card"
          onSubmit={(event) =>
            submitForm(
              event,
              "/api/check-ins",
              {
                ...checkin,
                progress_percent: Number(checkin.progress_percent),
              },
              "Check-in submitted successfully.",
              () =>
                setCheckin((old) => ({
                  ...old,
                  progress_percent: "",
                  notes: "",
                  rationale: "",
                }))
            )
          }
        >
          <h3>Submit Check-in</h3>

          <label>
            Employee ID
            <input
              style={inputStyle}
              value={checkin.employee_id}
              onChange={(e) =>
                setCheckin({ ...checkin, employee_id: e.target.value })
              }
              required
            />
          </label>

          <label>
            Review cycle ID
            <input
              style={inputStyle}
              value={checkin.cycle_id}
              onChange={(e) =>
                setCheckin({ ...checkin, cycle_id: e.target.value })
              }
              required
            />
          </label>

          <label>
            Progress percentage
            <input
              style={inputStyle}
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={checkin.progress_percent}
              onChange={(e) =>
                setCheckin({ ...checkin, progress_percent: e.target.value })
              }
              required
            />
          </label>

          <label>
            Notes
            <textarea
              style={inputStyle}
              value={checkin.notes}
              onChange={(e) =>
                setCheckin({ ...checkin, notes: e.target.value })
              }
            />
          </label>

          <label>
            Rationale (required for out-of-range progress)
            <textarea
              style={inputStyle}
              value={checkin.rationale}
              onChange={(e) =>
                setCheckin({ ...checkin, rationale: e.target.value })
              }
            />
          </label>

          <button style={buttonStyle} disabled={busy}>
            {busy ? "Submitting..." : "Submit Check-in"}
          </button>
        </form>

        <form
          className="workflow-card"
          onSubmit={(event) =>
            submitForm(
              event,
              "/api/feedback",
              {
                ...feedback,
                rating: feedback.rating === "" ? null : Number(feedback.rating),
                competency_id: feedback.competency_id || null,
                evidence_reference: feedback.evidence_reference || null,
              },
              "Feedback submitted successfully.",
              () =>
                setFeedback((old) => ({
                  ...old,
                  rating: "",
                  comments: "",
                  competency_id: "",
                  evidence_reference: "",
                }))
            )
          }
        >
          <h3>Give Feedback</h3>

          <label>
            Employee ID
            <input
              style={inputStyle}
              value={feedback.employee_id}
              onChange={(e) =>
                setFeedback({ ...feedback, employee_id: e.target.value })
              }
              required
            />
          </label>

          <label>
            Review cycle ID
            <input
              style={inputStyle}
              value={feedback.cycle_id}
              onChange={(e) =>
                setFeedback({ ...feedback, cycle_id: e.target.value })
              }
              required
            />
          </label>

          <label>
            Author ID
            <input
              style={inputStyle}
              value={feedback.author_id}
              onChange={(e) =>
                setFeedback({ ...feedback, author_id: e.target.value })
              }
              required
            />
          </label>

          <label>
            Feedback type
            <select
              style={inputStyle}
              value={feedback.feedback_type}
              onChange={(e) =>
                setFeedback({ ...feedback, feedback_type: e.target.value })
              }
            >
              <option value="peer">Peer</option>
              <option value="manager">Manager</option>
              <option value="self">Self</option>
              <option value="upward">Upward</option>
            </select>
          </label>

          <label>
            Rating (optional)
            <input
              style={inputStyle}
              type="number"
              min="1"
              max="5"
              value={feedback.rating}
              onChange={(e) =>
                setFeedback({ ...feedback, rating: e.target.value })
              }
            />
          </label>

          <label>
            Comments
            <textarea
              style={inputStyle}
              value={feedback.comments}
              onChange={(e) =>
                setFeedback({ ...feedback, comments: e.target.value })
              }
              required
            />
          </label>

          <label>
            Competency ID (optional)
            <input
              style={inputStyle}
              value={feedback.competency_id}
              onChange={(e) =>
                setFeedback({ ...feedback, competency_id: e.target.value })
              }
            />
          </label>

          <label>
            Evidence reference (optional)
            <input
              style={inputStyle}
              value={feedback.evidence_reference}
              onChange={(e) =>
                setFeedback({
                  ...feedback,
                  evidence_reference: e.target.value,
                })
              }
            />
          </label>

          <button style={buttonStyle} disabled={busy}>
            {busy ? "Submitting..." : "Submit Feedback"}
          </button>
        </form>

        <form
          className="workflow-card"
          onSubmit={(event) =>
            submitForm(
              event,
              "/api/reviews",
              { ...review, score: Number(review.score) },
              "Performance review created successfully.",
              () =>
                setReview((old) => ({
                  ...old,
                  score: "",
                }))
            )
          }
        >
          <h3>Create Performance Review</h3>

          <label>
            Employee ID
            <input
              style={inputStyle}
              value={review.employee_id}
              onChange={(e) =>
                setReview({ ...review, employee_id: e.target.value })
              }
              required
            />
          </label>

          <label>
            Review cycle ID
            <input
              style={inputStyle}
              value={review.cycle_id}
              onChange={(e) =>
                setReview({ ...review, cycle_id: e.target.value })
              }
              required
            />
          </label>

          <label>
            Reviewer / manager ID
            <input
              style={inputStyle}
              value={review.reviewer_id}
              onChange={(e) =>
                setReview({ ...review, reviewer_id: e.target.value })
              }
              required
            />
          </label>

          <label>
            Review score
            <input
              style={inputStyle}
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={review.score}
              onChange={(e) =>
                setReview({ ...review, score: e.target.value })
              }
              required
            />
          </label>

          <button style={buttonStyle} disabled={busy}>
            {busy ? "Creating..." : "Create Review"}
          </button>
        </form>

        <form
          className="workflow-card"
          onSubmit={(event) =>
            submitForm(
              event,
              "/api/development-plans",
              plan,
              "Development plan created successfully.",
              () =>
                setPlan((old) => ({
                  ...old,
                  review_id: "",
                  objective: "",
                  action: "",
                  target_date: "",
                }))
            )
          }
        >
          <h3>Create Development Plan</h3>

          <label>
            Employee ID
            <input
              style={inputStyle}
              value={plan.employee_id}
              onChange={(e) =>
                setPlan({ ...plan, employee_id: e.target.value })
              }
              required
            />
          </label>

          <label>
            Review ID (if applicable)
            <input
              style={inputStyle}
              value={plan.review_id}
              onChange={(e) =>
                setPlan({ ...plan, review_id: e.target.value })
              }
            />
          </label>

          <label>
            Objective
            <textarea
              style={inputStyle}
              value={plan.objective}
              onChange={(e) =>
                setPlan({ ...plan, objective: e.target.value })
              }
              required
            />
          </label>

          <label>
            Action
            <textarea
              style={inputStyle}
              value={plan.action}
              onChange={(e) => setPlan({ ...plan, action: e.target.value })}
              required
            />
          </label>

          <label>
            Target date
            <input
              style={inputStyle}
              type="date"
              value={plan.target_date}
              onChange={(e) =>
                setPlan({ ...plan, target_date: e.target.value })
              }
              required
            />
          </label>

          <button style={buttonStyle} disabled={busy}>
            {busy ? "Creating..." : "Create Development Plan"}
          </button>
        </form>
      </div>

      {selectedEmployeeId ? (
        <section className="records-section">
          <div className="records-heading">
            <div>
              <h2>Performance Records</h2>
              <p>Review history and employee development progress</p>
            </div>
            {employeeDetails && (
              <span className="records-employee">
                {employeeDetails.full_name}
              </span>
            )}
          </div>

          <div className="records-columns">
            <section className="records-panel">
              <div className="records-panel-heading">
                <div>
                  <h3>Performance Reviews</h3>
                  <p>Review status and scores</p>
                </div>
                <span className="records-count">{selectedEmployeeReviews.length}</span>
              </div>

              {selectedEmployeeReviews.length ? (
                <div className="records-grid">
                  {selectedEmployeeReviews.map((item) => (
                    <article className="record-card" key={item.review_id}>
                      <div className="record-topline">
                        <span className="record-type">PERFORMANCE REVIEW</span>
                        <span className={`status-badge status-${String(item.status || "unknown").toLowerCase()}`}>
                          {item.status || "Unknown"}
                        </span>
                      </div>
                      <h4>{item.review_id}</h4>
                      <p className="record-description">Employee: {item.employee_id}</p>
                      <div className="record-score">
                        <span>Review score</span>
                        <strong>{item.score ?? "â€”"}</strong>
                      </div>
                      <button type="button" className="record-action" onClick={() => openReviewModal(item)}>
                        Update status <span aria-hidden="true">â†’</span>
                      </button>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="records-empty">
                  <strong>No reviews yet</strong>
                  <p>Performance reviews will appear here.</p>
                </div>
              )}
            </section>

            <section className="records-panel">
              <div className="records-panel-heading">
                <div>
                  <h3>Development Plans</h3>
                  <p>Objectives and approval decisions</p>
                </div>
                <span className="records-count">{selectedEmployeePlans.length}</span>
              </div>

              {selectedEmployeePlans.length ? (
                <div className="records-grid">
                  {selectedEmployeePlans.map((item) => {
                    const status = item.approval_status || item.status || "Pending";
                    return (
                      <article className="record-card" key={item.plan_id}>
                        <div className="record-topline">
                          <span className="record-type">DEVELOPMENT PLAN</span>
                          <span className={`status-badge status-${String(status).toLowerCase().replace(/\s+/g, "-")}`}>
                            {status}
                          </span>
                        </div>
                        <h4>{item.plan_id}</h4>
                        <p className="record-description">{item.objective || "Development objective"}</p>
                        {item.target_date && (
                          <div className="record-meta">
                            <span>Target date</span>
                            <strong>{item.target_date}</strong>
                          </div>
                        )}
                        <button type="button" className="record-action" onClick={() => openPlanModal(item)}>
                          Make decision <span aria-hidden="true">â†’</span>
                        </button>
                      </article>
                    );
                  })}
                </div>
              ) : (
                <div className="records-empty">
                  <strong>No development plans yet</strong>
                  <p>Development plans will appear here.</p>
                </div>
              )}
            </section>
          </div>
        </section>
      ) : (
        <section className="records-section">
          <div className="records-heading">
            <div>
              <h2>Recent Activity</h2>
              <p>Latest performance reviews and development plans</p>
            </div>
          </div>

          <div className="records-columns">
            <section className="records-panel">
              <div className="records-panel-heading">
                <div>
                  <h3>Performance Reviews</h3>
                  <p>Recent review activity</p>
                </div>
                <span className="records-count">{reviews.length}</span>
              </div>

              {reviews.length ? (
                <div className="records-grid">
                  {reviews.map((item) => (
                    <article className="record-card" key={item.review_id}>
                      <div className="record-topline">
                        <span className="record-type">REVIEW</span>
                        <span className={`status-badge status-${String(item.status || "unknown").toLowerCase()}`}>
                          {item.status || "Unknown"}
                        </span>
                      </div>
                      <h4>{item.review_id}</h4>
                      <p className="record-description">Employee: {item.employee_id}</p>
                      <div className="record-score">
                        <span>Review score</span>
                        <strong>{item.score ?? "â€”"}</strong>
                      </div>
                      <button type="button" className="record-action" onClick={() => openReviewModal(item)}>
                        Update status <span aria-hidden="true">â†’</span>
                      </button>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="records-empty">
                  <strong>No reviews available</strong>
                  <p>New reviews will appear here.</p>
                </div>
              )}
            </section>

            <section className="records-panel">
              <div className="records-panel-heading">
                <div>
                  <h3>Development Plans</h3>
                  <p>Recent plans and approval decisions</p>
                </div>
                <span className="records-count">{plans.length}</span>
              </div>

              {plans.length ? (
                <div className="records-grid">
                  {plans.map((item) => {
                    const status = item.approval_status || item.status || "Pending";
                    return (
                      <article className="record-card" key={item.plan_id}>
                        <div className="record-topline">
                          <span className="record-type">DEVELOPMENT PLAN</span>
                          <span className={`status-badge status-${String(status).toLowerCase().replace(/\s+/g, "-")}`}>
                            {status}
                          </span>
                        </div>
                        <h4>{item.plan_id}</h4>
                        <p className="record-description">Employee: {item.employee_id}</p>
                        <p className="record-objective">{item.objective || "Development objective"}</p>
                        <button type="button" className="record-action" onClick={() => openPlanModal(item)}>
                          Make decision <span aria-hidden="true">â†’</span>
                        </button>
                      </article>
                    );
                  })}
                </div>
              ) : (
                <div className="records-empty">
                  <strong>No development plans available</strong>
                  <p>New plans will appear here.</p>
                </div>
              )}
            </section>
          </div>
        </section>
      )}
      {activeModal && (
        <div
          className="workflow-modal-backdrop"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget && !busy) {
              setActiveModal(null);
            }
          }}
        >
          <form className="workflow-modal" onSubmit={submitModal}>
            {activeModal.type === "review" ? (
              <>
                <h3>Update Review Status</h3>
                <p>
                  Review: <strong>{activeModal.item.review_id}</strong>
                </p>

                <label>
                  New status
                  <select
                    style={inputStyle}
                    value={modalData.status}
                    onChange={(e) =>
                      setModalData({ ...modalData, status: e.target.value })
                    }
                    required
                  >
                    <option value="draft">Draft</option>
                    <option value="submitted">Submitted</option>
                    <option value="completed">Completed</option>
                  </select>
                </label>

                <label>
                  Assigned reviewer ID
                  <input
                    style={inputStyle}
                    value={modalData.actor_id}
                    onChange={(e) =>
                      setModalData({ ...modalData, actor_id: e.target.value })
                    }
                    required
                  />
                </label>

                <label>
                  Reason for status change
                  <textarea
                    style={inputStyle}
                    value={modalData.reason}
                    onChange={(e) =>
                      setModalData({ ...modalData, reason: e.target.value })
                    }
                    required
                  />
                </label>
              </>
            ) : (
              <>
                <h3>Development Plan Decision</h3>
                <p>
                  Plan: <strong>{activeModal.item.plan_id}</strong>
                </p>

                <label>
                  Decision
                  <select
                    style={inputStyle}
                    value={modalData.approval_status}
                    onChange={(e) =>
                      setModalData({
                        ...modalData,
                        approval_status: e.target.value,
                      })
                    }
                    required
                  >
                    <option value="approved">Approve</option>
                    <option value="rejected">Reject</option>
                  </select>
                </label>

                <label>
                  Manager ID
                  <input
                    style={inputStyle}
                    value={modalData.manager_id}
                    onChange={(e) =>
                      setModalData({
                        ...modalData,
                        manager_id: e.target.value,
                      })
                    }
                    required
                  />
                </label>

                <label>
                  Reason for decision
                  <textarea
                    style={inputStyle}
                    value={modalData.reason}
                    onChange={(e) =>
                      setModalData({ ...modalData, reason: e.target.value })
                    }
                    required
                  />
                </label>
              </>
            )}

            <div className="workflow-modal-actions">
              <button
                type="button"
                style={secondaryButtonStyle}
                onClick={() => setActiveModal(null)}
                disabled={busy}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="primary-action"
                style={buttonStyle}
                disabled={busy}
              >
                {busy ? "Saving..." : "Save Changes"}
              </button>
            </div>
          </form>
        </div>
      )}
    </section>
  );
}

export default WorkflowPanel;

