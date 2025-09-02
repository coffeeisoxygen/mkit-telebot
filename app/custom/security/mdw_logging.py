import time

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        # Untuk audit, jika sudah ada auth, bisa ambil user_id dari request.state atau token
        user_id = getattr(
            request.state, "user_id", None
        )  # contoh, sesuaikan dengan auth
        log = logger.bind(
            client_ip=client_ip,
            user_agent=user_agent,
            method=request.method,
            url=str(request.url),
            user_id=user_id,
        )
        log.info(f"Incoming Request: {request.method} {request.url.path}")

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        # Untuk trace lebih detail, bisa log response body (hati-hati data sensitif)
        # response_body = b""
        # async for chunk in response.body_iterator:
        #     response_body += chunk
        # log.debug(f"Response Body: {response_body}")
        log.info(
            f"Outgoing Response: {request.method} {request.url.path} - Status: {response.status_code} - Process Time: {process_time:.4f}s"
        )
        return response
