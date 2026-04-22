import { SiteShell } from "../../components/site-shell";
import { WaitlistForm } from "../../components/waitlist-form";

export const metadata = {
  title: "Beta | SentinelAPI",
};

export default function BetaPage() {
  return (
    <SiteShell>
      <section className="section">
        <div className="waitlist-card">
          <div>
            <p className="eyebrow">Private beta</p>
            <h1 className="page-title">Request access to the first SentinelAPI customer cohort.</h1>
            <p className="page-copy">
              The beta will focus on startup backend teams running production APIs on FastAPI, Flask, or
              Express. Early customers will shape alert quality, onboarding, and reporting workflows.
            </p>
          </div>
          <WaitlistForm title="Tell us where to send your beta invite." />
        </div>
      </section>

      <section className="section">
        <div className="feature-grid">
          <article className="feature-card">
            <span className="feature-icon">01</span>
            <h3>Fast integration</h3>
            <p>Install the SDK, create an org token, and start shipping runtime events quickly.</p>
          </article>
          <article className="feature-card">
            <span className="feature-icon">02</span>
            <h3>Human feedback loop</h3>
            <p>Beta participants help tune anomaly thresholds and alert quality before broad release.</p>
          </article>
          <article className="feature-card">
            <span className="feature-icon">03</span>
            <h3>Invite-only rollout</h3>
            <p>Support stays personal while the scanning and reporting loops mature.</p>
          </article>
        </div>
      </section>
    </SiteShell>
  );
}

