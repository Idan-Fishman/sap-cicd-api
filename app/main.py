from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import branch, change_request


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

app.include_router(router=branch.router, tags=["branches"])
app.include_router(router=change_request.router, tags=["change-requests"])


@app.get("/")
async def root():
    return {"greetings": "Hey you! move to /docs to find out how to use the api"}


@app.get("/ping")
async def ping():
    return {"ping": "pong!"}
