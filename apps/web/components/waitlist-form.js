"use client";

import { useState } from "react";

export function WaitlistForm({
  compact = false,
  title = "Join the beta list to get early access pricing, onboarding updates, and the first working SDK drop.",
}) {
  const [status, setStatus] = useState({
    type: "idle",
    message: title,
  });
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email") || "").trim();

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setStatus({
        type: "error",
        message: "Enter a valid email address to request beta access.",
      });
      return;
    }

    setLoading(true);
    setStatus({
      type: "idle",
      message: "Submitting your beta request...",
    });

    try {
      const response = await fetch("/api/waitlist", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const payload = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(payload.message || "Waitlist request failed.");
      }

      event.currentTarget.reset();
      setStatus({
        type: "success",
        message:
          payload.message ||
          "You are on the beta list. We will reach out with access details soon.",
      });
    } catch (error) {
      setStatus({
        type: "error",
        message:
          error.message ||
          "The waitlist endpoint is not configured yet. Set WAITLIST_WEBHOOK_URL to enable submissions.",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className={`waitlist-form${compact ? " compact" : ""}`} onSubmit={handleSubmit} noValidate>
      <label className="sr-only" htmlFor={compact ? "beta-email-compact" : "beta-email"}>
        Email address
      </label>
      <input
        id={compact ? "beta-email-compact" : "beta-email"}
        name="email"
        type="email"
        autoComplete="email"
        placeholder="you@company.com"
        required
      />
      <button className="button button-primary" type="submit" disabled={loading}>
        {loading ? "Submitting..." : "Request access"}
      </button>
      <p
        className={`form-note${status.type === "success" ? " is-success" : ""}${
          status.type === "error" ? " is-error" : ""
        }`}
      >
        {status.message}
      </p>
    </form>
  );
}

