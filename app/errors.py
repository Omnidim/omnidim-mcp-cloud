"""RFC 7591/6749 error responses for the OAuth provider surface."""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

OAUTH_ROUTES = frozenset({"/register"})


def _classify(field_path: tuple[str | int, ...]) -> str:
    if "redirect_uris" in field_path:
        return "invalid_redirect_uri"
    if "software_statement" in field_path:
        return "invalid_software_statement"
    return "invalid_client_metadata"


def install_oauth_error_handler(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        if request.url.path in OAUTH_ROUTES:
            errors = exc.errors()
            first = errors[0] if errors else {}
            loc = tuple(p for p in first.get("loc", ()) if p != "body")
            error = _classify(loc)
            description = first.get("msg", "request did not validate")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": error, "error_description": description},
            )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )
