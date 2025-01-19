from fastapi import FastAPI

from api.router import base

app = FastAPI()

app.include_router(base.router)
