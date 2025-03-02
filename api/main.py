from fastapi import FastAPI

from api.router import base, cards, sets, dnd_rules, mtg_rules

app = FastAPI()

app.include_router(base.router)
app.include_router(sets.router)
app.include_router(cards.router)
app.include_router(dnd_rules.router)
app.include_router(mtg_rules.router)
