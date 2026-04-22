import { saveWaitlistEntry } from "../../../lib/waitlist-store";

export async function POST(request) {
  const payload = await request.json().catch(() => null);
  const email = payload?.email?.trim?.();

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return Response.json(
      {
        message: "Enter a valid email address.",
      },
      { status: 400 }
    );
  }

  const submission = await saveWaitlistEntry({
    email,
    source: "sentinelapi-beta",
    submittedAt: new Date().toISOString(),
    userAgent: request.headers.get("user-agent"),
    ip:
      request.headers.get("x-forwarded-for") ||
      request.headers.get("x-real-ip") ||
      "unknown",
  });

  const webhook = process.env.WAITLIST_WEBHOOK_URL;

  if (!webhook) {
    return Response.json(
      {
        message: submission.isNew
          ? "You are on the beta list. Your request has been saved locally for now."
          : "This email is already on the beta list.",
        persisted: "local",
        total: submission.total,
      }
    );
  }

  const response = await fetch(webhook, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      source: "sentinelapi-beta",
      submittedAt: new Date().toISOString(),
    }),
  });

  if (!response.ok) {
    return Response.json(
      {
        message:
          "Your request was saved locally, but the configured waitlist webhook did not accept the submission.",
        persisted: "local",
        total: submission.total,
      }
    );
  }

  return Response.json({
    message: submission.isNew
      ? "You are on the beta list. We will send the next steps soon."
      : "This email is already on the beta list.",
    persisted: "local+webhook",
    total: submission.total,
  });
}
