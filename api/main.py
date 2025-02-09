from fastapi import FastAPI

from api.router import base, cards

app = FastAPI()

app.include_router(base.router)
app.include_router(cards.router)
