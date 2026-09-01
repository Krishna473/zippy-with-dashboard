import { useEffect, useMemo, useState } from "react";
import { fetchList, createRecord, updateRecord } from "../api.js";
import logo from "../assets/zenve-zippy-logo.png";
import "./SalesCRM.css";

const ROLE_META = {
  regionalManager: {
    title: "Regional Manager",
    subtitle: "Regional sales planning, manager assignment and team progress",
  },
  manager: {
    title: "Sales Manager",
    subtitle: "Team planning, executive assignment and task monitoring",
  },
  executive: {
    title: "Sales Executive",
    subtitle: "Daily execution, doctor visits and assigned task progress",
  },
};

const PLAN_TABS = ["standard", "monthly", "daily"];
const VIP_LEVELS = ["VIP 1", "VIP 2", "VIP 3"];
const ALL_REGIONS = "ALL";

function formatINR(n) {
  return "₹" + Math.round(n || 0).toLocaleString("en-IN");
}

// "Standard plan" shows everything; "Monthly plan" narrows to tasks due this
// calendar month; "Daily plan" narrows to tasks due today. Tied to the real
// due_date field on executive_tasks — not decorative.
function isWithinPlan(dueDate, plan) {
  if (plan === "standard") return true;
  if (!dueDate) return false;
  const due = new Date(dueDate);
  const today = new Date();
  if (plan === "daily") {
    return due.toDateString() === today.toDateString();
  }
  if (plan === "monthly") {
    return due.getFullYear() === today.getFullYear() && due.getMonth() === today.getMonth();
  }
  return true;
}

export default function SalesCRM({ role = "executive", onRoleChange, onExit }) {
  const meta = ROLE_META[role] || ROLE_META.executive;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [executives, setExecutives] = useState([]);
  const [coverage, setCoverage] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [products, setProducts] = useState([]);
  const [inventory, setInventory] = useState([]);

  // executive role: scope is an executive id (number).
  // manager / regionalManager role: scope is a region string, or ALL_REGIONS.
  const [scope, setScope] = useState(null);
  const [subTab, setSubTab] = useState("tasks"); // tasks | alerts | coverage
  const [activePlan, setActivePlan] = useState("standard");
  const [activeVip, setActiveVip] = useState("VIP 1");

  const [taskTitle, setTaskTitle] = useState("");
  const [taskPincode, setTaskPincode] = useState("");
  const [taskPriority, setTaskPriority] = useState("medium");
  const [taskDue, setTaskDue] = useState("");
  const [assignee, setAssignee] = useState("");
  const [busy, setBusy] = useState(false);

  function loadAll() {
    setLoading(true);
    setError("");
    Promise.all([
      fetchList("sales_executives"),
      fetchList("pincode_coverage"),
      fetchList("executive_tasks"),
      fetchList("executive_alerts"),
      fetchList("doctors"),
      fetchList("products"),
      fetchList("inventory"),
    ])
      .then(([execs, cov, tsk, alr, docs, prods, inv]) => {
        setExecutives(Array.isArray(execs) ? execs : []);
        setCoverage(Array.isArray(cov) ? cov : []);
        setTasks(Array.isArray(tsk) ? tsk : []);
        setAlerts(Array.isArray(alr) ? alr : []);
        setDoctors(Array.isArray(docs) ? docs : []);
        setProducts(Array.isArray(prods) ? prods : []);
        setInventory(Array.isArray(inv) ? inv : []);
      })
      .catch((err) => setError(err?.message || "Failed to load Sales CRM data"))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadAll();
  }, []);

  const regions = useMemo(() => [...new Set(executives.map((e) => e.region).filter(Boolean))], [executives]);

  // Keep `scope` valid whenever the role changes or data finishes loading —
  // switching to Sales Executive needs a numeric executive id; switching to
  // a manager tier needs a region (or "All regions").
  useEffect(() => {
    if (role !== "executive") return;
    if (!executives.length) return;
    if (typeof scope === "number" && executives.some((e) => e.id === scope)) return;
    setScope(executives[0].id);
  }, [role, executives, scope]);

  useEffect(() => {
    if (role === "executive") return;
    if (scope === ALL_REGIONS || (typeof scope === "string" && regions.includes(scope))) return;
    setScope(regions[0] || ALL_REGIONS);
  }, [role, regions, scope]);

  const execsInScope = useMemo(() => {
    if (role === "executive") {
      const one = executives.find((e) => e.id === scope);
      return one ? [one] : [];
    }
    if (scope === ALL_REGIONS || !scope) return executives;
    return executives.filter((e) => e.region === scope);
  }, [role, scope, executives]);

  const coveredPincodes = useMemo(() => {
    const ids = new Set(execsInScope.map((e) => e.id));
    return new Set(coverage.filter((c) => ids.has(c.executive_id)).map((c) => c.pincode));
  }, [execsInScope, coverage]);

  const myCoverage = useMemo(
    () => coverage.filter((c) => execsInScope.some((e) => e.id === c.executive_id)),
    [coverage, execsInScope]
  );

  // Tasks/alerts have no direct executive-id field in the schema — only a
  // pincode. A task/alert is "in scope" if it's tagged with one of the
  // covered pin codes, or has no pincode at all (a general item visible to
  // everyone in scope).
  const myTasksAll = useMemo(
    () => tasks.filter((t) => !t.pincode || coveredPincodes.has(t.pincode)),
    [tasks, coveredPincodes]
  );
  const myTasks = useMemo(() => myTasksAll.filter((t) => isWithinPlan(t.due_date, activePlan)), [myTasksAll, activePlan]);
  const myAlerts = useMemo(
    () => alerts.filter((a) => !a.pincode || coveredPincodes.has(a.pincode)),
    [alerts, coveredPincodes]
  );

  const areaDoctors = useMemo(() => doctors.filter((d) => coveredPincodes.has(d.pincode)), [doctors, coveredPincodes]);
  const areaProducts = useMemo(() => products.filter((p) => coveredPincodes.has(p.pincode)), [products, coveredPincodes]);

  const openTasksCount = myTasksAll.filter((t) => t.status !== "done").length;
  const unreadAlertsCount = myAlerts.filter((a) => !a.is_read).length;
  const doctorsInArea = areaDoctors.length;
  const skusInArea = areaProducts.length;
  const lowStockRows = inventory.filter(
    (i) => coveredPincodes.has(i.pincode) && (Number(i.available_quantity) || 0) <= (Number(i.reorder_level) || 0)
  ).length;

  const vipDoctors = useMemo(() => {
    const sorted = [...doctors].sort((a, b) => Number(b.rating || 0) - Number(a.rating || 0));
    const groupSize = Math.max(1, Math.ceil(sorted.length / 3));
    const start = VIP_LEVELS.indexOf(activeVip) * groupSize;
    return sorted.slice(start, start + groupSize);
  }, [doctors, activeVip]);

  const assignPincodeOptions = [...coveredPincodes];
  const assigneeOptions = role === "regionalManager" ? regions : execsInScope.map((e) => e.name).filter(Boolean);

  function addTask() {
    if (!taskTitle.trim()) return;
    setBusy(true);
    createRecord("executive_tasks", {
      title: taskTitle.trim(),
      task_type: role === "regionalManager" ? "regional_assigned" : role === "manager" ? "manager_assigned" : "field_task",
      entity_type: "general",
      pincode: taskPincode.trim() || null,
      priority: taskPriority,
      status: "open",
      due_date: taskDue || null,
    })
      .then((created) => {
        setTasks((prev) => [...prev, created]);
        setTaskTitle("");
        setTaskPincode("");
        setTaskDue("");
        setTaskPriority("medium");
        setAssignee("");
      })
      .catch((err) => setError(err?.message || "Failed to add task"))
      .finally(() => setBusy(false));
  }

  function setTaskStatus(task, status) {
    updateRecord("executive_tasks", task.id, { status })
      .then((updated) => setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t))))
      .catch((err) => setError(err?.message || "Failed to update task"));
  }

  function markAlertRead(alert) {
    updateRecord("executive_alerts", alert.id, { is_read: true })
      .then((updated) => setAlerts((prev) => prev.map((a) => (a.id === updated.id ? updated : a))))
      .catch((err) => setError(err?.message || "Failed to update alert"));
  }

  if (loading) {
    return (
      <div className="sales-crm-page">
        <p className="zzc-muted">Loading Sales CRM…</p>
      </div>
    );
  }

  return (
    <div className="sales-crm-page">
      <header className="sales-crm-header">
        <div className="sales-crm-brand">
          <div className="sales-crm-logo">
            <img src={logo} alt="Zenve Zippy" />
          </div>
          <div>
            <h1>{meta.title} · Sales CRM</h1>
            <p className="zzc-muted zzc-small">{meta.subtitle}</p>
          </div>
        </div>
        <div className="sales-crm-actions">
          <button className={`sales-role-switch ${role === "regionalManager" ? "active" : ""}`} onClick={() => onRoleChange?.("regionalManager")}>
            Regional Manager
          </button>
          <button className={`sales-role-switch ${role === "manager" ? "active" : ""}`} onClick={() => onRoleChange?.("manager")}>
            Sales Manager
          </button>
          <button className={`sales-role-switch ${role === "executive" ? "active" : ""}`} onClick={() => onRoleChange?.("executive")}>
            Sales Executive
          </button>

          {role === "executive" ? (
            <select className="sales-crm-select" value={scope ?? ""} onChange={(e) => setScope(Number(e.target.value))}>
              {executives.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name} — {e.region || e.city || "—"}
                </option>
              ))}
            </select>
          ) : (
            <select className="sales-crm-select" value={scope ?? ""} onChange={(e) => setScope(e.target.value)}>
              <option value={ALL_REGIONS}>All regions</option>
              {regions.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          )}

          <button className="zzc-btn zzc-btn-outline" onClick={loadAll} disabled={busy}>
            Reload
          </button>
          <button className="zzc-btn zzc-btn-outline" onClick={onExit}>
            Admin CRM
          </button>
        </div>
      </header>

      {error && <div className="dash-error sales-crm-error">{error}</div>}

      <section className="sales-crm-stats">
        <div className="sales-stat-card">
          <p className="sales-stat-label">Open tasks</p>
          <p className="sales-stat-value">{openTasksCount}</p>
        </div>
        <div className="sales-stat-card">
          <p className="sales-stat-label">Unread alerts</p>
          <p className="sales-stat-value">{unreadAlertsCount}</p>
        </div>
        <div className="sales-stat-card">
          <p className="sales-stat-label">Doctors in area</p>
          <p className="sales-stat-value">{doctorsInArea}</p>
        </div>
        <div className="sales-stat-card">
          <p className="sales-stat-label">SKUs in area</p>
          <p className="sales-stat-value">{skusInArea}</p>
        </div>
        <div className="sales-stat-card">
          <p className="sales-stat-label">Low stock rows</p>
          <p className="sales-stat-value">{lowStockRows}</p>
        </div>
      </section>

      <div className="sales-crm-tabs-row">
        <div className="sales-crm-tabs">
          {["tasks", "alerts", "coverage"].map((t) => (
            <button key={t} className={"sales-crm-tab" + (subTab === t ? " active" : "")} onClick={() => setSubTab(t)}>
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>
        <div className="sales-plan-tabs">
          {PLAN_TABS.map((plan) => (
            <button key={plan} className={activePlan === plan ? "active" : ""} onClick={() => setActivePlan(plan)}>
              {plan.charAt(0).toUpperCase() + plan.slice(1)} plan
            </button>
          ))}
        </div>
      </div>

      {subTab === "tasks" && (
        <>
          {role !== "executive" && (
            <div className="sales-crm-card">
              <h3>{role === "regionalManager" ? "Assign task to Sales Manager" : "Assign task to Sales Executive"}</h3>
              <div className="sales-task-form">
                <input
                  className="sales-task-title-input"
                  placeholder="Task title"
                  value={taskTitle}
                  onChange={(e) => setTaskTitle(e.target.value)}
                />
                <select value={assignee} onChange={(e) => setAssignee(e.target.value)}>
                  <option value="">Select {role === "regionalManager" ? "manager" : "executive"}</option>
                  {assigneeOptions.map((name) => (
                    <option key={name} value={name}>
                      {name}
                    </option>
                  ))}
                </select>
                <select value={taskPincode} onChange={(e) => setTaskPincode(e.target.value)}>
                  <option value="">Pin code</option>
                  {assignPincodeOptions.map((pc) => (
                    <option key={pc} value={pc}>
                      {pc}
                    </option>
                  ))}
                </select>
                <select value={taskPriority} onChange={(e) => setTaskPriority(e.target.value)}>
                  <option value="low">low</option>
                  <option value="medium">medium</option>
                  <option value="high">high</option>
                </select>
                <input type="date" value={taskDue} onChange={(e) => setTaskDue(e.target.value)} />
                <button className="zzc-btn zzc-btn-primary" onClick={addTask} disabled={busy || !taskTitle.trim()}>
                  Add task
                </button>
              </div>
              <p className="zzc-muted zzc-small" style={{ marginTop: 10 }}>
                Tasks are matched to executives by pin code — there's no direct assignee field on tasks in the current schema,
                and no Sales Manager records exist yet, so the {role === "regionalManager" ? "manager" : "executive"} picker
                above is for your reference; the pin code you choose is what actually determines who sees this task.
              </p>
            </div>
          )}

          {role === "executive" && (
            <div className="sales-crm-card">
              <h3>Add a field task</h3>
              <div className="sales-task-form">
                <input
                  className="sales-task-title-input"
                  placeholder="Task title"
                  value={taskTitle}
                  onChange={(e) => setTaskTitle(e.target.value)}
                />
                <select value={taskPincode} onChange={(e) => setTaskPincode(e.target.value)}>
                  <option value="">Pin code</option>
                  {assignPincodeOptions.map((pc) => (
                    <option key={pc} value={pc}>
                      {pc}
                    </option>
                  ))}
                </select>
                <select value={taskPriority} onChange={(e) => setTaskPriority(e.target.value)}>
                  <option value="low">low</option>
                  <option value="medium">medium</option>
                  <option value="high">high</option>
                </select>
                <input type="date" value={taskDue} onChange={(e) => setTaskDue(e.target.value)} />
                <button className="zzc-btn zzc-btn-primary" onClick={addTask} disabled={busy || !taskTitle.trim()}>
                  Add task
                </button>
              </div>
            </div>
          )}

          <div className="sales-crm-card">
            <h3>
              {role === "executive" ? "My tasks" : "Team tasks"} <span className="zzc-muted zzc-small">({activePlan} plan)</span>
            </h3>
            <div className="sales-task-list">
              {myTasks.length === 0 ? (
                <p className="zzc-muted zzc-small">No tasks in this view.</p>
              ) : (
                myTasks.map((t) => (
                  <div className="sales-task-row" key={t.id}>
                    <div>
                      <p className="sales-task-title">{t.title}</p>
                      <p className="zzc-muted zzc-small">
                        {t.task_type} · {t.entity_type} · pin {t.pincode || "—"} · due {t.due_date || "—"} ·{" "}
                        {String(t.priority || "").toUpperCase()}
                      </p>
                    </div>
                    <div className="sales-task-status-pills">
                      {[
                        ["open", "open"],
                        ["in_progress", "in progress"],
                        ["done", "done"],
                      ].map(([value, label]) => (
                        <button
                          key={value}
                          className={"sales-status-pill" + (t.status === value ? " active" : "")}
                          onClick={() => setTaskStatus(t, value)}
                        >
                          {label}
                        </button>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}

      {subTab === "alerts" && (
        <div className="sales-crm-card">
          <h3>Alerts</h3>
          <div className="sales-task-list">
            {myAlerts.length === 0 ? (
              <p className="zzc-muted zzc-small">No alerts.</p>
            ) : (
              myAlerts.map((a) => (
                <div className="sales-task-row" key={a.id}>
                  <div>
                    <p className="sales-task-title">{a.title}</p>
                    <p className="zzc-muted zzc-small">
                      {a.severity} · {a.entity_type} · pin {a.pincode || "—"}
                    </p>
                  </div>
                  {a.is_read ? (
                    <span className="sales-status-pill active">read</span>
                  ) : (
                    <button className="sales-status-pill" onClick={() => markAlertRead(a)}>
                      mark read
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {subTab === "coverage" && (
        <>
          <div className="sales-coverage-grid">
            <div className="sales-crm-card">
              <h3>Pin codes covered</h3>
              <div className="sales-pincode-pills">
                {myCoverage.length === 0 ? (
                  <p className="zzc-muted zzc-small">No pin codes assigned yet.</p>
                ) : (
                  myCoverage.map((c) => (
                    <span className="sales-status-pill" key={c.id}>
                      {c.pincode}
                    </span>
                  ))
                )}
              </div>
            </div>
            <div className="sales-crm-card">
              <h3>Doctors in area</h3>
              <div className="sales-task-list">
                {areaDoctors.length === 0 ? (
                  <p className="zzc-muted zzc-small">No doctors in this scope yet.</p>
                ) : (
                  areaDoctors.map((d) => (
                    <div className="sales-task-row" key={d.id}>
                      <div>
                        <p className="sales-task-title">{d.name}</p>
                        <p className="zzc-muted zzc-small">
                          {d.specializations || "—"} · pin {d.pincode}
                        </p>
                      </div>
                      <span className="zzc-muted zzc-small">★ {d.rating ?? "—"}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="sales-crm-card">
            <h3>Medicines, pet food &amp; accessories in area</h3>
            <table className="zzc-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Pin</th>
                  <th>Price</th>
                  <th>Stock</th>
                  <th>Rx</th>
                </tr>
              </thead>
              <tbody>
                {areaProducts.length === 0 ? (
                  <tr className="zzc-empty-row">
                    <td colSpan={5}>No products in this scope yet</td>
                  </tr>
                ) : (
                  areaProducts.map((p) => (
                    <tr key={p.id}>
                      <td>{p.name}</td>
                      <td>{p.pincode}</td>
                      <td>{formatINR(p.price)}</td>
                      <td>{p.stock_quantity}</td>
                      <td>{p.is_prescription_required === true || p.is_prescription_required === "Yes" ? "Yes" : "No"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      <section className="sales-workspace">
        <div className="sales-section-heading sales-doctor-heading">
          <div>
            <h2>Doctor Segments</h2>
            <p>Top-rated doctors grouped into VIP 1, VIP 2 and VIP 3.</p>
          </div>
          <div className="sales-plan-tabs">
            {VIP_LEVELS.map((vip) => (
              <button key={vip} className={activeVip === vip ? "active" : ""} onClick={() => setActiveVip(vip)}>
                {vip}
              </button>
            ))}
          </div>
        </div>
        <div className="sales-doctor-grid">
          {vipDoctors.length === 0 ? (
            <div className="sales-empty-panel">No doctors available for {activeVip}.</div>
          ) : (
            vipDoctors.slice(0, 6).map((doctor) => (
              <article className="sales-doctor-card" key={doctor.id}>
                <span className="sales-vip-badge">{activeVip}</span>
                <h3>{doctor.name || "Doctor"}</h3>
                <p>{doctor.specializations || doctor.specialization || "Specialization not set"}</p>
                <div>
                  <span>Rating</span>
                  <strong>{doctor.rating ?? "—"}</strong>
                </div>
                <div>
                  <span>Pin code</span>
                  <strong>{doctor.pincode || "—"}</strong>
                </div>
              </article>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
