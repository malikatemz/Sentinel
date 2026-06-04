from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .exceptions import generic_exception_handler, http_exception_handler
from .middleware import RateLimitMiddleware, RequestIdMiddleware, SecurityHeadersMiddleware
from .routers import alerts, auth, checks, dashboard, endpoints, health, users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="API monitoring platform — monitor your endpoints in under 5 minutes.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware (order matters — outermost first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(endpoints.router)
app.include_router(checks.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)
