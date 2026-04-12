"""
Custom CORS middleware that supports wildcard patterns for Vercel deployments
"""
import re
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send


class CustomCORSMiddleware:
    """
    Custom CORS middleware that supports pattern matching for origins.
    Allows all Vercel preview deployments and specific production URLs.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        allow_origins: list = None,
        allow_origin_regex: str = None,
        allow_methods: list = None,
        allow_headers: list = None,
        expose_headers: list = None,
        allow_credentials: bool = False,
        max_age: int = 600,
    ):
        self.app = app
        self.allow_origins = allow_origins or []
        self.allow_origin_regex = allow_origin_regex
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or ["*"]
        self.expose_headers = expose_headers or ["*"]
        self.allow_credentials = allow_credentials
        self.max_age = max_age
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin matches allowed origins or regex pattern"""
        # Check exact matches
        if origin in self.allow_origins:
            return True
        
        # Check regex pattern
        if self.allow_origin_regex:
            try:
                if re.match(self.allow_origin_regex, origin):
                    return True
            except Exception:
                pass
        
        return False
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope)
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            if origin and self._is_origin_allowed(origin):
                await self._send_cors_response(send, origin)
            else:
                await self.app(scope, receive, send)
            return
        
        # Handle regular requests
        async def send_with_cors(message: dict) -> None:
            if message["type"] == "http.response.start":
                if origin and self._is_origin_allowed(origin):
                    headers = list(message.get("headers", []))
                    headers.append((b"access-control-allow-origin", origin.encode()))
                    if self.allow_credentials:
                        headers.append((b"access-control-allow-credentials", b"true"))
                    if self.expose_headers:
                        headers.append(
                            (b"access-control-expose-headers", ", ".join(self.expose_headers).encode())
                        )
                    message["headers"] = headers
            await send(message)
        
        await self.app(scope, receive, send_with_cors)
    
    async def _send_cors_response(self, send: Send, origin: str) -> None:
        """Send CORS preflight response"""
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"access-control-allow-origin", origin.encode()),
                (b"access-control-allow-methods", ", ".join(self.allow_methods).encode()),
                (b"access-control-allow-headers", ", ".join(self.allow_headers).encode()),
                (b"access-control-max-age", str(self.max_age).encode()),
                (b"access-control-allow-credentials", b"true" if self.allow_credentials else b"false"),
                (b"content-length", b"0"),
            ],
        })
        await send({"type": "http.response.body", "body": b""})
