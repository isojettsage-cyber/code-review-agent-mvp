import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { AlertTriangle, Bot, CheckCircle2, Clock, FileText, Play } from "lucide-react";
import { api } from "./api";
import "./styles.css";

function StatusBadge({ status }) {
  const className = `badge badge-${status}`;
  return <span className={className}>{status}</span>;
}

function TaskForm({ onCreated }) {
  const [title, setTitle] = useState("Code Review / Tech Debt Scan");
  const [repoPath, setRepoPath] = useState("./app/sample_repo");
  const [branch, setBranch] = useState("main");
  const [loading, setLoading] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    try {
      const task = await api.createTask({
        title,
        repo_path: repoPath,
        branch,
      });
      await api.runTask(task.id);
      onCreated();
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card form" onSubmit={submit}>
      <div className="card-title">
        <Bot size={20} />
        <h2>Create Review Task</h2>
      </div>

      <label>
        Task title
        <input value={title} onChange={(e) => setTitle(e.target.value)} />
      </label>

      <label>
        Repository path
        <input value={repoPath} onChange={(e) => setRepoPath(e.target.value)} />
      </label>

      <label>
        Branch
        <input value={branch} onChange={(e) => setBranch(e.target.value)} />
      </label>

      <button disabled={loading}>
        <Play size={16} />
        {loading ? "Creating..." : "Create and Run"}
      </button>

      <p className="hint">
        Local demo path is <code>./app/sample_repo</code>. To scan your own code, use an absolute path or a path relative to the backend directory.
      </p>
    </form>
  );
}

function ReportPanel({ task }) {
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function load() {
      setError("");
      setReport(null);
      if (!task || task.status !== "completed") return;

      try {
        const data = await api.getReport(task.id);
        if (active) setReport(data);
      } catch (err) {
        if (active) setError(err.message);
      }
    }

    load();
    return () => {
      active = false;
    };
  }, [task]);

  if (!task) {
    return (
      <div className="card empty">
        <FileText />
        <p>Select a completed task to view the report.</p>
      </div>
    );
  }

  if (task.status !== "completed") {
    return (
      <div className="card empty">
        <Clock />
        <p>Task is {task.status}. Report will appear after completion.</p>
      </div>
    );
  }

  if (error) {
    return <div className="card error">{error}</div>;
  }

  if (!report) {
    return <div className="card">Loading report...</div>;
  }

  const highCount = report.findings.filter((item) => item.severity === "high").length;

  return (
    <div className="card report">
      <div className="report-header">
        <div>
          <h2>Review Report</h2>
          <p>{report.summary}</p>
        </div>
        <div className="risk-score">
          <span>{report.risk_score}</span>
          <small>Risk Score</small>
        </div>
      </div>

      {highCount > 0 && (
        <div className="warning">
          <AlertTriangle size={18} />
          {highCount} high severity issue(s) need immediate review.
        </div>
      )}

      <h3>Recommendations</h3>
      <div className="recommendations">
        {report.recommendations.map((item, index) => (
          <div className="recommendation" key={index}>
            <strong>{item.priority} · {item.title}</strong>
            <p>{item.action}</p>
          </div>
        ))}
      </div>

      <h3>Findings</h3>
      <div className="findings">
        {report.findings.map((item, index) => (
          <div className={`finding severity-${item.severity}`} key={index}>
            <div>
              <strong>{item.severity.toUpperCase()} · {item.type}</strong>
              <p>{item.message}</p>
            </div>
            <code>{item.file}:{item.line}</code>
          </div>
        ))}
      </div>
    </div>
  );
}

function App() {
  const [tasks, setTasks] = useState([]);
  const [selectedTaskId, setSelectedTaskId] = useState(null);
  const [loading, setLoading] = useState(false);

  const selectedTask = useMemo(
    () => tasks.find((task) => task.id === selectedTaskId) || tasks[0],
    [tasks, selectedTaskId]
  );

  async function loadTasks() {
    setLoading(true);
    try {
      const data = await api.listTasks();
      setTasks(data);
      if (!selectedTaskId && data.length > 0) {
        setSelectedTaskId(data[0].id);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  async function rerun(taskId) {
    await api.runTask(taskId);
    await loadTasks();
  }

  useEffect(() => {
    loadTasks();
    const timer = setInterval(loadTasks, 3000);
    return () => clearInterval(timer);
  }, []);

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">MVP Console</p>
          <h1>Code Review / Tech Debt Governance Agent</h1>
          <p>
            Multi-agent code scanning workflow with FastAPI, React, SQLite, task queue,
            and Feishu notification placeholder.
          </p>
        </div>
        <div className="hero-card">
          <CheckCircle2 />
          <span>Runnable local MVP</span>
        </div>
      </header>

      <section className="grid">
        <div>
          <TaskForm onCreated={loadTasks} />

          <div className="card task-list">
            <div className="card-title">
              <FileText size={20} />
              <h2>Tasks</h2>
              {loading && <small>Refreshing...</small>}
            </div>

            {tasks.length === 0 && <p className="hint">No tasks yet.</p>}

            {tasks.map((task) => (
              <div
                className={`task-item ${selectedTask?.id === task.id ? "active" : ""}`}
                key={task.id}
                onClick={() => setSelectedTaskId(task.id)}
              >
                <div>
                  <strong>#{task.id} {task.title}</strong>
                  <p>{task.repo_path} · {task.branch}</p>
                </div>
                <div className="task-actions">
                  <StatusBadge status={task.status} />
                  <button className="secondary" onClick={(e) => {
                    e.stopPropagation();
                    rerun(task.id);
                  }}>
                    Run
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <ReportPanel task={selectedTask} />
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
