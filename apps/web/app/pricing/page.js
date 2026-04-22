import Link from "next/link";
import { SiteShell } from "../../components/site-shell";

const tiers = [
  {
    name: "Starter",
    price: "$49",
    summary: "For solo developers and side projects.",
    items: ["3 monitored endpoints", "100K requests per month", "Security alerts and starter reports"],
  },
  {
    name: "Pro",
    price: "$149",
    summary: "For startup teams shipping production APIs.",
    items: ["20 monitored endpoints", "5M requests per month", "Slack alerts, richer reports, and faster triage"],
  },
  {
    name: "Enterprise",
    price: "$299",
    summary: "For growing companies that need wider coverage and support.",
    items: ["Unlimited endpoints", "SLA and priority support", "Custom audit exports and onboarding"],
  },
];

export const metadata = {
  title: "Pricing | SentinelAPI",
};

export default function PricingPage() {
  return (
    <SiteShell>
      <section className="section">
        <div className="section-heading">
          <p className="eyebrow">Pricing</p>
          <h1 className="page-title">Security monitoring that fits startup tool budgets.</h1>
          <p className="page-copy">
            SentinelAPI is designed for the teams that need runtime coverage and audit evidence without
            buying an enterprise platform.
          </p>
        </div>

        <div className="pricing-grid">
          {tiers.map((tier) => (
            <article className={`price-card${tier.name === "Pro" ? " featured" : ""}`} key={tier.name}>
              <p className="price-tier">{tier.name}</p>
              <h3>
                {tier.price}
                <span>/mo</span>
              </h3>
              <p className="price-copy">{tier.summary}</p>
              <ul>
                {tier.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="value-card">
          <p className="value-label">Beta billing</p>
          <h2>Private beta access starts with invites, not open self-serve checkout.</h2>
          <p>
            The first release is optimizing for fast onboarding and product feedback. Stripe integration is
            scaffolded in the platform plan and will be added once the core detection loop is live.
          </p>
          <div className="hero-actions">
            <Link className="button button-primary" href="/beta">
              Request beta access
            </Link>
            <Link className="button button-secondary" href="/docs">
              Read the docs
            </Link>
          </div>
        </div>
      </section>
    </SiteShell>
  );
}

