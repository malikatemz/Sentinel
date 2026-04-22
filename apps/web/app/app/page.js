import { SiteShell } from "../../components/site-shell";

const alerts = [
  {
    severity: "critical",
    title: "Open Redis port detected",
    detail: "34.120.18.8 - Port 6379 is reachable from the public internet.",
    when: "2m ago",
  },
  {
    severity: "high",
    title: "Credential leak candidate in GitHub Actions",
    detail: "Build logs matched a high-confidence API key pattern.",
    when: "8m ago",
  },
  {
    severity: "medium",
    title: "Traffic spike on /auth/token",
    detail: "3.8x above rolling baseline from a new ASN cluster.",
    when: "21m ago",
  },
];

const checklist = [
  {
    title: "Create org token",
    detail: "Generate a scoped ingest token for your first API environment.",
    state: "Ready",
  },
  {
    title: "Install SDK",
    detail: "Use the Node or Python package and wrap the API app with one line.",
    state: "Ready",
  },
  {
    title: "Route alerts",
    detail: "Connect Slack and email delivery before the first live scan.",
    state: "Blocked by backend",
  },
  {
    title: "Enable scans",
    detail: "Restore the legacy scanner adapter to schedule exposed-port checks.",
    state: "Needs legacy code",
  },
];

const endpoints = [
  {
    name: "auth-service",
    framework: "FastAPI",
    status: "Watching",
    baseline: "Learned",
    lastAlert: "Traffic spike 21m ago",
  },
  {
    name: "billing-api",
    framework: "Express",
    status: "Watching",
    baseline: "Learning",
    lastAlert: "Latency drift 42m ago",
  },
  {
    name: "admin-panel",
    framework: "Flask",
    status: "Pending scan",
    baseline: "Not started",
    lastAlert: "No incidents",
  },
];

const reports = [
  {
    title: "SOC 2 weekly evidence pack",
    status: "Draft ready",
    updatedAt: "9m ago",
  },
  {
    title: "GDPR incident summary",
    status: "Awaiting data source",
    updatedAt: "1h ago",
  },
  {
    title: "ISO 27001 control mapping",
    status: "Queued",
    updatedAt: "2h ago",
  },
];

export const metadata = {
  title: "Dashboard | SentinelAPI",
};

export default function DashboardPage() {
  return (
    <SiteShell>
      <section className="section">
        <div className="section-heading">
          <p className="eyebrow">Dashboard shell</p>
          <h1 className="page-title">A private-beta dashboard ready to be wired to live data.</h1>
          <p className="page-copy">
            This route is the UI shell for authenticated orgs. It currently uses placeholder data while the
            API, worker, and Supabase integration are being wired.
          </p>
        </div>

        <div className="dashboard-overview">
          <article className="feature-card">
            <span className="feature-icon">12</span>
            <h3>Alerts today</h3>
            <p>12 incidents across anomaly, port, and credential-leak categories.</p>
          </article>
          <article className="feature-card">
            <span className="feature-icon">03</span>
            <h3>Critical issues</h3>
            <p>3 critical events requiring immediate remediation.</p>
          </article>
          <article className="feature-card">
            <span className="feature-icon">07</span>
            <h3>Endpoints watched</h3>
            <p>7 monitored endpoints enrolled in the runtime baseline model.</p>
          </article>
          <article className="feature-card">
            <span className="feature-icon">01</span>
            <h3>Beta cohort</h3>
            <p>Invite-only onboarding with local waitlist persistence and routing-ready hooks.</p>
          </article>
        </div>
      </section>

      <section className="section">
        <div className="panel-grid">
          <div className="dashboard-card">
            <div className="dashboard-topline">
              <div>
                <p className="dashboard-label">Beta onboarding</p>
                <h3>Setup checklist</h3>
              </div>
              <span className="pill pill-muted">Operator view</span>
            </div>

            <div className="checklist">
              {checklist.map((item) => (
                <article className="check-item" key={item.title}>
                  <div>
                    <strong>{item.title}</strong>
                    <p>{item.detail}</p>
                  </div>
                  <span className="badge">{item.state}</span>
                </article>
              ))}
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-topline">
              <div>
                <p className="dashboard-label">Endpoint inventory</p>
                <h3>Monitored services</h3>
              </div>
              <span className="pill pill-muted">Mock org data</span>
            </div>

            <div className="table-card">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Service</th>
                    <th>Framework</th>
                    <th>Baseline</th>
                    <th>Last alert</th>
                  </tr>
                </thead>
                <tbody>
                  {endpoints.map((endpoint) => (
                    <tr key={endpoint.name}>
                      <td>
                        <strong>{endpoint.name}</strong>
                        <span>{endpoint.status}</span>
                      </td>
                      <td>{endpoint.framework}</td>
                      <td>{endpoint.baseline}</td>
                      <td>{endpoint.lastAlert}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="panel-grid panel-grid-wide">
          <div className="dashboard-card">
            <div className="dashboard-topline">
              <div>
                <p className="dashboard-label">Live feed</p>
                <h3>Recent activity</h3>
              </div>
              <span className="pill pill-muted">Placeholder data</span>
            </div>

            <div className="timeline">
              {alerts.map((alert) => (
                <div className="timeline-row" key={alert.title}>
                  <span className={`severity severity-${alert.severity}`}></span>
                  <div>
                    <strong>{alert.title}</strong>
                    <p>{alert.detail}</p>
                  </div>
                  <time>{alert.when}</time>
                </div>
              ))}
            </div>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-topline">
              <div>
                <p className="dashboard-label">Reports</p>
                <h3>Compliance drafts</h3>
              </div>
              <span className="pill pill-muted">Queue state</span>
            </div>

            <div className="report-list">
              {reports.map((report) => (
                <article className="report-item" key={report.title}>
                  <div>
                    <strong>{report.title}</strong>
                    <p>{report.status}</p>
                  </div>
                  <time>{report.updatedAt}</time>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>
    </SiteShell>
  );
}
