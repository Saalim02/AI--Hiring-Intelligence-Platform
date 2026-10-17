from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from app.core.dependencies import get_current_user
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth,
    candidate,
    health,
    resume,
    invitations
)

from app.core.config import settings
from app.core.ai_errors import AIServiceError

app = FastAPI(
    title="AI Resume Platform"
)


@app.exception_handler(AIServiceError)
async def ai_service_error_handler(request: Request, exc: AIServiceError):
    return JSONResponse(status_code=503, content={"detail": exc.message})

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health.router,
    tags=["Health"]
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(candidate.router, prefix="/candidate", tags=["Candidate"])
app.include_router(invitations.router, prefix="/invitations", tags=["Invitations"])

app.include_router(
    resume.router,
    prefix="/resume",
    tags=["Resume"],
    dependencies=[Depends(get_current_user)]
)
