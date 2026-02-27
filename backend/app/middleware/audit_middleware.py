"""Audit middleware that logs every API request for SIH compliance."""

import time
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config.database import AsyncSessionLocal
from app.core.security import decode_access_token
from app.models.audit_models import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that creates an audit log entry for every API request.

    This ensures full traceability of all data access and modifications
    as required by hospital information system regulations.
    """

    # Paths to exclude from audit logging
    EXCLUDED_PATHS = {
        "/api/health",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/favicon.ico",
    }

    # Map HTTP methods to audit actions
    METHOD_ACTION_MAP = {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process the request and log an audit entry."""
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Extract user info from token if present
        user_id = self._extract_user_id(request)
        action = self.METHOD_ACTION_MAP.get(request.method, "unknown")
        ip_address = request.client.host if request.client else None

        # Parse entity info from path
        entity_type, entity_id = self._parse_path(request.url.path)

        try:
            async with AsyncSessionLocal() as session:
                audit_entry = AuditLog(
                    user_id=user_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    details={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                        "query_params": dict(request.query_params),
                    },
                    ip_address=ip_address,
                )
                session.add(audit_entry)
                await session.commit()
        except Exception:
            # Audit logging should never break the request
            pass

        return response

    def _extract_user_id(self, request: Request) -> Optional[int]:
        """Extract user ID from the Authorization header."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            try:
                return int(payload["sub"])
            except (ValueError, TypeError):
                return None
        return None

    def _parse_path(self, path: str) -> tuple[str, Optional[str]]:
        """Parse the request path to extract entity type and ID."""
        parts = path.strip("/").split("/")

        # e.g., /api/v1/donors/5 -> entity_type="donors", entity_id="5"
        entity_type = "unknown"
        entity_id = None

        if len(parts) >= 3:
            entity_type = parts[2] if parts[0] == "api" else parts[0]

        if len(parts) >= 4:
            # Check if last segment is an ID
            last = parts[-1]
            if last.isdigit():
                entity_id = last
                entity_type = parts[-2]

        return entity_type, entity_id
