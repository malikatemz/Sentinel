import { SiteShell } from "../../components/site-shell";

export const metadata = {
  title: "Docs | SentinelAPI",
};

export default function DocsPage() {
  return (
    <SiteShell>
      <section className="section">
        <div className="section-heading">
          <p className="eyebrow">Docs</p>
          <h1 className="page-title">The product surface is here, and the backend contracts are ready to fill.</h1>
          <p className="page-copy">
            This documentation route is the starting point for onboarding developers during the private beta.
          </p>
        </div>

        <div className="docs-grid">
          <article className="feature-card">
            <span className="feature-icon">PY</span>
            <h3>Python SDK</h3>
            <p>Planned entry points for FastAPI and Flask:</p>
            <pre className="code-block">
              <code>{`from sentinelapi import sentinel

client = sentinel.client(token="...")
client.watch(app)
client.scan("api.example.com")
client.report("soc2", start_at, end_at)`}</code>
            </pre>
          </article>

          <article className="feature-card">
            <span className="feature-icon">JS</span>
            <h3>Node SDK</h3>
            <p>Planned entry points for Express and Node services:</p>
            <pre className="code-block">
              <code>{`import { sentinel } from "@sentinel/sdk-node";

const client = sentinel.createClient({ token: "..." });
app.use(client.watch());
await client.scan("api.example.com");
await client.report({ type: "soc2" });`}</code>
            </pre>
          </article>

          <article className="feature-card">
            <span className="feature-icon">API</span>
            <h3>Ingestion contract</h3>
            <p>Primary backend endpoints for the beta:</p>
            <pre className="code-block">
              <code>{`POST /v1/ingest/events
POST /v1/scans/trigger
GET  /v1/alerts
POST /v1/reports
POST /v1/webhooks/github
POST /v1/webhooks/stripe`}</code>
            </pre>
          </article>
        </div>
      </section>
    </SiteShell>
  );
}
