"""
FastAPI application entry point.

This module initializes and configures the FastAPI application, including
CORS middleware, rate limiting, and routing for all API endpoints.

:author: Artur
:version: 1.0.0
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from src.api import contact, utils, auth, users
from src.conf.limiter import limiter
from src.database.redis import redis_client
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Sets up the rate limiter and initialises the Redis client
    on application startup. Closes the Redis connection on shutdown.

    :param app: The FastAPI application instance
    :type app: FastAPI
    """
    app.state.limiter = limiter
    app.state._rate_limit_exceeded_handler = _rate_limit_exceeded_handler
    # Initialise Redis
    await redis_client.init()
    yield
    # Close Redis on shutdown
    await redis_client.close()


app = FastAPI(lifespan=lifespan)
origins = ["http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom rate limit exceeded exception handler.

    :param request: The incoming request
    :type request: Request
    :param exc: The rate limit exceeded exception
    :type exc: RateLimitExceeded
    :return: JSON response with error message
    :rtype: JSONResponse
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )


app.include_router(utils.router, prefix="/api")
app.include_router(contact.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
