export type SentinelEvent = {
  method: string;
  path: string;
  statusCode: number;
  latencyMs: number;
  ip?: string;
  userAgent?: string;
  occurredAt?: string;
};

export type WatchOptions = {
  token: string;
  ingestUrl?: string;
  endpointName?: string;
  environment?: string;
};

type RequestLike = {
  method?: string;
  path?: string;
  ip?: string;
  headers?: Record<string, string | string[] | undefined>;
  originalUrl?: string;
};

type ResponseLike = {
  statusCode?: number;
  on: (event: "finish", callback: () => void) => void;
};

type NextLike = () => void;

class SentinelClient {
  private readonly token: string;
  private readonly ingestUrl: string;
  private readonly endpointName: string;
  private readonly environment: string;

  constructor(options: WatchOptions) {
    this.token = options.token;
    this.ingestUrl = options.ingestUrl || "http://localhost:8000/v1/ingest/events";
    this.endpointName = options.endpointName || "default";
    this.environment = options.environment || "prod";
  }

  async send(events: SentinelEvent[]): Promise<Response> {
    return fetch(this.ingestUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        org_token: this.token,
        endpoint_name: this.endpointName,
        events: events.map((event) => ({
          method: event.method,
          path: event.path,
          status_code: event.statusCode,
          latency_ms: event.latencyMs,
          ip: event.ip,
          user_agent: event.userAgent,
          environment: this.environment,
          occurred_at: event.occurredAt || new Date().toISOString(),
        })),
      }),
    });
  }

  middleware() {
    return (req: RequestLike, res: ResponseLike, next: NextLike) => {
      const startedAt = Date.now();

      res.on("finish", async () => {
        void this.send([
          {
            method: req.method || "GET",
            path: req.originalUrl || req.path || "/",
            statusCode: res.statusCode || 200,
            latencyMs: Date.now() - startedAt,
            ip: req.ip,
            userAgent: headerValue(req.headers?.["user-agent"]),
          },
        ]).catch(() => undefined);
      });

      next();
    };
  }

  watch() {
    return this.middleware();
  }

  async scan(target: string): Promise<{ status: string; target: string }> {
    return {
      status: "queued",
      target,
    };
  }

  async report(input: {
    type: "soc2" | "gdpr" | "iso27001";
    startAt?: string;
    endAt?: string;
  }): Promise<{ status: string; type: string }> {
    return {
      status: "queued",
      type: input.type,
    };
  }
}

function headerValue(value: string | string[] | undefined): string | undefined {
  if (!value) {
    return undefined;
  }

  return Array.isArray(value) ? value.join(", ") : value;
}

export const sentinel = {
  createClient(options: WatchOptions) {
    return new SentinelClient(options);
  },
  watch(options: WatchOptions) {
    return new SentinelClient(options).middleware();
  },
};

export { SentinelClient };
