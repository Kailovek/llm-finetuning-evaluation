from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message


def install_handlers(app: FastAPI) -> None:
    def content(request: Request, code: str, message: str, details: list | None = None) -> dict:
        return {
            "code": code,
            "message": message,
            "request_id": request.headers.get("X-Request-ID", str(uuid4())),
            "details": details or [],
        }

    @app.exception_handler(AppError)
    async def app_error(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=content(request, exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {"field": ".".join(map(str, item["loc"])), "reason": item["msg"]}
            for item in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=content(request, "validation_error", "Invalid request", details),
        )
