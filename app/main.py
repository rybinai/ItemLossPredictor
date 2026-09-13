from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.ml import load_predictor
from app.routers.predictions import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    app.state.predictor = load_predictor()
    yield


app = FastAPI(title="item loss predictor", lifespan=lifespan)
app.include_router(router)
