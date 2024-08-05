from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis
import uvicorn
from src.contacts.routers import router as router_contacts
from src.auth.routers import router as router_auth
from config.general import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(router_contacts, prefix="/contacts", tags=["contacts"])
app.include_router(router_auth, prefix="/auth", tags=["auth"])

origins = settings.origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    redis = Redis(host=settings.redis_host, port=settings.redis_port)
    await FastAPILimiter.init(redis)


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def index():
    return {"msg": "Hello World"}


def root():
    return {"message": "Welcome to FastApi"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
