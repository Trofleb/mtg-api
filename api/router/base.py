from fastapi.routing import APIRouter
from starlette.responses import PlainTextResponse

router = APIRouter()


@router.get("/ping", response_class=PlainTextResponse)
def read_root():
    return "pong"
