from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router
from app.api.analyze import router as analyze_router
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.langsmith import router as langsmith_router


app = FastAPI(
    title="Resume AI",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

app.include_router(auth_router)

app.include_router(upload_router)

app.include_router(analyze_router)

app.include_router(health_router)

app.include_router(langsmith_router)

# Dashboard router
from app.api.dashboard import router as dashboard_router
app.include_router(dashboard_router)


@app.get("/")
def home():

    return {
        "message": "Resume AI API Running"
    }
