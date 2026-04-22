import express from "express";
import { sentinel } from "@sentinel/sdk-node";

const app = express();
const port = Number(process.env.PORT || 3001);
const client = sentinel.createClient({
  token: process.env.SENTINEL_TOKEN || "sentinel_demo_token",
  ingestUrl: process.env.SENTINEL_INGEST_URL || "http://localhost:8000/v1/ingest/events",
  endpointName: "express-demo",
  environment: process.env.SENTINEL_ENVIRONMENT || "local",
});

app.use(client.watch());

app.get("/", (_req, res) => {
  res.json({
    service: "express-demo",
    status: "ok",
    message: "SentinelAPI middleware is active for this route.",
  });
});

app.get("/auth/token", (_req, res) => {
  res.status(401).json({
    error: "Unauthorized",
    hint: "This endpoint is useful for generating anomaly-shaped traffic during local testing.",
  });
});

app.get("/health", (_req, res) => {
  res.json({
    status: "healthy",
    monitored: true,
  });
});

app.listen(port, () => {
  console.log(`Express demo listening on http://localhost:${port}`);
});
