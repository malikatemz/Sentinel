import Link from "next/link";
import { SiteShell } from "../components/site-shell";
import { WaitlistForm } from "../components/waitlist-form";

const features = [
  {
    id: "01",
    title: "Real-time anomaly detection",
    copy:
      "Learn a baseline from live API traffic and surface suspicious spikes, unusual response patterns, and risky IP clusters.",
  },
  {
    id: "02",
    title: "Exposed port scanning",
    copy:
      "Continuously scan public infrastructure for services that should not be visible to the internet.",
  },
  {
    id: "03",
    title: "Credential leak alerts",
    copy:
      "Watch repos, CI logs, and deployment workflows for exposed tokens before they become incidents.",
  },
  {
    id: "04",
    title: "AI alert triage",
    copy:
      "Turn noisy signals into prioritized, readable incidents with remediation guidance your team can act on quickly.",
  },
  {
    id: "05",
    title: "Compliance report generation",
    copy:
      "Produce audit-ready summaries and evidence trails for SOC 2, GDPR, and ISO 27001 preparation.",
  },
  {
    id: "06",
    title: "Slack and email routing",
    copy:
      "Pipe incidents straight to the people responsible so issues are seen while they still matter.",
  },
];

const steps = [
  {
    step: "Step 1",
    title: "Wrap your app",
    copy: "Add one middleware line to FastAPI, Flask, or Express.",
  },
  {
    step: "Step 2",
    title: "Stream security events",
    copy: "Requests, ports, and suspicious changes feed the monitor continuously.",
  },
  {
    step: "Step 3",
    title: "Respond faster",
    copy: "Get prioritized alerts and export audit-ready evidence when needed.",
  },
];

const pricing = [
  {
    tier: "Starter",
    price: "$49",
    copy: "For solo developers and side projects.",
    items: ["3 monitored endpoints", "100K requests per month", "Basic alerts and reports"],
  },
  {
    tier: "Pro",
    price: "$149",
    featured: true,
    copy: "For startup teams shipping production APIs.",
    items: ["20 monitored endpoints", "5M requests per month", "Slack alerts and richer reporting"],
  },
  {
    tier: "Enterprise",
    price: "$299",
    copy: "For growing teams that need full coverage.",
    items: ["Unlimited endpoints", "Priority support and SLA", "Custom audit exports"],
  },
];

export default function HomePage() {
  return (
    <SiteShell>
      <section className="hero section">
        <div className="hero-copy">
          <p className="eyebrow">Security monitoring for modern APIs</p>
          <h1>Catch the breach before it becomes a postmortem.</h1>
          <p className="hero-text">
            SentinelAPI monitors your APIs and infrastructure for security threats in real time, detects
            exposed ports, credential leaks, and anomalies, and auto-generates compliance reports with a
            one-line SDK integration.
          </p>

          <div className="hero-actions">
            <Link className="button button-primary" href="/beta">
              Join the beta
            </Link>
            <Link className="button button-secondary" href="/docs">
              View the SDK
            </Link>
          </div>

          <ul className="hero-stats" aria-label="Highlights">
            <li>
              <strong>&lt; 5 minutes</strong>
              <span>to install and start watching traffic</span>
            </li>
            <li>
              <strong>FastAPI, Flask, Express</strong>
              <span>first-class developer workflow</span>
            </li>
            <li>
              <strong>Audit-ready reports</strong>
              <span>for SOC 2, GDPR, and ISO 27001 prep</span>
            </li>
          </ul>
        </div>

        <div className="hero-visual">
          <div className="signal-card">
            <div className="card-topline">
              <span className="pill">Live Monitor</span>
              <span className="status-dot" aria-hidden="true"></span>
            </div>

            <div className="terminal-block">
              <div className="terminal-tabs" aria-hidden="true">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <pre>
                <code>{`pip install sentinelapi

from fastapi import FastAPI
from sentinelapi import sentinel

app = FastAPI()
client = sentinel.client(token=os.getenv("SENTINEL_TOKEN"))
client.watch(app)`}</code>
              </pre>
            </div>

            <div className="alert-stack" aria-label="Example alerts">
              <article className="alert-card critical">
                <span className="alert-kind">Critical</span>
                <h2>Credential leak detected in CI logs</h2>
                <p>Rotated key suggested. Slack alert delivered to on-call.</p>
              </article>
              <article className="alert-card medium">
                <span className="alert-kind">Medium</span>
                <h2>Unexpected traffic spike on /auth/token</h2>
                <p>3.8x above baseline from a new IP cluster.</p>
              </article>
            </div>
          </div>
        </div>
      </section>

      <section className="value-strip section">
        <div className="value-card">
          <p className="value-label">Why teams switch</p>
          <h2>Security tools should feel like developer tooling, not enterprise procurement.</h2>
          <p>
            Install one SDK, stream runtime events, detect misconfigurations, and generate clean evidence
            for auditors without stitching together five separate products.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="section-heading">
          <p className="eyebrow">What you get</p>
          <h2>Coverage across runtime, infrastructure, and compliance.</h2>
        </div>

        <div className="feature-grid">
          {features.map((feature) => (
            <article className="feature-card" key={feature.id}>
              <span className="feature-icon">{feature.id}</span>
              <h3>{feature.title}</h3>
              <p>{feature.copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section-heading">
          <p className="eyebrow">How it works</p>
          <h2>From install to first alert in a single sprint planning slot.</h2>
        </div>

        <div className="monitor-layout">
          <div className="monitor-steps">
            {steps.map((item) => (
              <article key={item.step}>
                <span>{item.step}</span>
                <h3>{item.title}</h3>
                <p>{item.copy}</p>
              </article>
            ))}
          </div>

          <div className="dashboard-card">
            <div className="dashboard-topline">
              <div>
                <p className="dashboard-label">Threat Activity</p>
                <h3>Sentinel timeline</h3>
              </div>
              <span className="pill pill-muted">24h baseline</span>
            </div>

            <div className="timeline">
              <div className="timeline-row">
                <span className="severity severity-critical"></span>
                <div>
                  <strong>Open Redis port detected</strong>
                  <p>34.120.18.8 - Port 6379 reachable from public internet</p>
                </div>
                <time>2m ago</time>
              </div>
              <div className="timeline-row">
                <span className="severity severity-medium"></span>
                <div>
                  <strong>New token pattern in build logs</strong>
                  <p>GitHub Actions runner flagged a possible credential leak</p>
                </div>
                <time>8m ago</time>
              </div>
              <div className="timeline-row">
                <span className="severity severity-low"></span>
                <div>
                  <strong>Latency drift on billing API</strong>
                  <p>Response time rising alongside 401 burst from one ASN</p>
                </div>
                <time>21m ago</time>
              </div>
            </div>

            <div className="report-preview">
              <p>Audit report snapshot</p>
              <div className="report-bars" aria-hidden="true">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
              </div>
              <small>Evidence grouped by control, alert history, and remediation notes.</small>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-heading">
          <p className="eyebrow">Pricing</p>
          <h2>Built for teams that want coverage before they hire a security engineer.</h2>
        </div>

        <div className="pricing-grid">
          {pricing.map((tier) => (
            <article className={`price-card${tier.featured ? " featured" : ""}`} key={tier.tier}>
              <p className="price-tier">{tier.tier}</p>
              <h3>
                {tier.price}
                <span>/mo</span>
              </h3>
              <p className="price-copy">{tier.copy}</p>
              <ul>
                {tier.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <section className="waitlist section">
        <div className="waitlist-card">
          <div>
            <p className="eyebrow">Beta waitlist</p>
            <h2>Launch with a sharper security story.</h2>
            <p>
              Join the beta list to get early access pricing, onboarding updates, and the first working SDK
              drop.
            </p>
          </div>

          <WaitlistForm />
        </div>
      </section>
    </SiteShell>
  );
}
