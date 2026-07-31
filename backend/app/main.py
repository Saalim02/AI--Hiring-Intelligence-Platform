from fastapi import FastAPI , Depends
from app.core.dependencies import get_current_user
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth,
    health,
    resume
)

from app.core.database import (
    Base,
    engine
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Resume Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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

app.include_router(
    resume.router,
    prefix="/resume",
    tags=["Resume"],
    dependencies=[Depends(get_current_user)]
)
