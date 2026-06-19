from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp
from app.auth.auth import verificar_token
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction

EXCLUDE_PATHS = ["/api/login", "/login", "/docs", "/openapi.json"]

class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, database_service:str, dispatch: DispatchFunction | None = None):
        super().__init__(app)
        self.database_service = database_service

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in EXCLUDE_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"error": "Token requerido"})

        token = auth_header.split(" ")[1]
        payload = verificar_token(token)

        if not payload:
            return JSONResponse(status_code=401, content={"error": "Token inválido"})

        request.state.user = payload
        return await call_next(request)
