"use client";

import Link from "next/link";
import { SiteShell } from "../../../components/site-shell";

const translations = {
  en: {
    eyebrow: "Pricing",
    title: "Security monitoring that fits startup tool budgets.",
    subtitle: "SentinelAPI is designed for the teams that need runtime coverage and audit evidence without buying an enterprise platform.",
    subscribe: "Subscribe",
    cta_label: "Subscribe now",
    cta_title: "Start protecting your APIs today with a monthly subscription.",
    cta_desc: "Choose the plan that fits your needs. All plans include core security monitoring, alerts and regular reports. Upgrade or downgrade anytime.",
    cta_view: "View pricing",
    cta_docs: "Read the docs",
    tiers: {
      Starter: { summary: "For solo developers and side projects." },
      Pro: { summary: "For startup teams shipping production APIs." },
      Enterprise: { summary: "For growing companies that need wider coverage and support." },
    },
  },
  es: {
    eyebrow: "Precios",
    title: "Monitoreo de seguridad que se ajusta a presupuestos de startups.",
    subtitle: "SentinelAPI está diseñado para equipos que necesitan cobertura de runtime.",
    subscribe: "Suscribirse",
    cta_label: "Suscríbete ahora",
    cta_title: "Comienza a proteger tus APIs hoy.",
    cta_desc: "Elige el plan que se ajuste a tus necesidades.",
    cta_view: "Ver precios",
    cta_docs: "Leer docs",
    tiers: {
      Starter: { summary: "Para desarrolladores individuales." },
      Pro: { summary: "Para equipos de startups." },
      Enterprise: { summary: "Para empresas en crecimiento." },
    },
  },
  de: {
    eyebrow: "Preise",
    title: "Sicherheitsüberwachung, die in Startup-Budgets passt.",
    subtitle: "SentinelAPI ist für Teams konzipiert, die Laufzeitabdeckung benötigen.",
    subscribe: "Abonnieren",
    cta_label: "Jetzt abonnieren",
    cta_title: "Beginnen Sie heute mit dem Schutz Ihrer APIs.",
    cta_desc: "Wählen Sie den Plan, der zu Ihnen passt.",
    cta_view: "Preise",
    cta_docs: "Doku",
    tiers: {
      Starter: { summary: "Für einzelne Entwickler." },
      Pro: { summary: "Für Startup-Teams." },
      Enterprise: { summary: "Für wachsende Unternehmen." },
    },
  },
};

const tiers = [
  { name: "Starter", price: "$24", items: ["3 endpoints", "100K solicitudes/mes", "Alertas de seguridad"] },
  { name: "Pro", price: "$75", items: ["20 endpoints", "5M solicitudes/mes", "Alertas Slack"] },
  { name: "Enterprise", price: "$150", items: ["Endpoints ilimitados", "SLA y soporte", "Exportaciones personalizadas"] },
];

// Try to get language from URL path
function getLangFromPath(pathname) {
  if (pathname.startsWith("/es")) return "es";
  if (pathname.startsWith("/de")) return "de";
  return "en";
}

export default function PricingPage() {
  // Get lang - in real app would come from params/context
  const pathname = typeof window !== "undefined" ? window.location.pathname : "/";
  const lang = getLangFromPath(pathname);
  const t = translations[lang] || translations.en;

  const handleSubscribe = async (tier) => {
    try {
      const response = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tier }),
      });
      const data = await response.json();
      if (data.url) {
        window.location.href = data.url;
      } else {
        alert(data.error || "Failed to start checkout");
      }
    } catch (err) {
      alert("Failed to start checkout");
    }
  };

  return (
    <SiteShell lang={lang}>
      <section className="section">
        <div className="section-heading">
          <p className="eyebrow">{t.eyebrow}</p>
          <h1 className="page-title">{t.title}</h1>
          <p className="page-copy">{t.subtitle}</p>
        </div>

        <div className="pricing-grid">
          {tiers.map((tier) => (
            <article className={`price-card${tier.name === "Pro" ? " featured" : ""}`} key={tier.name}>
              <p className="price-tier">{tier.name}</p>
              <h3>
                {tier.price}
                <span>/mo</span>
              </h3>
              <p className="price-copy">{t.tiers[tier.name].summary}</p>
              <ul>
                {tier.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
              <button className="button button-primary" onClick={() => handleSubscribe(tier.name)}>
                {t.subscribe}
              </button>
            </article>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="value-card">
          <p className="value-label">{t.cta_label}</p>
          <h2>{t.cta_title}</h2>
          <p>{t.cta_desc}</p>
          <div className="hero-actions">
            <Link className="button button-primary" href="/pricing">
              {t.cta_view}
            </Link>
            <Link className="button button-secondary" href="/docs">
              {t.cta_docs}
            </Link>
          </div>
        </div>
      </section>
    </SiteShell>
  );
}

