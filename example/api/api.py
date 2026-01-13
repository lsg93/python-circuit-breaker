import random
from http import HTTPStatus

from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/flaky-service")
def flaky_service():
    if random.randint(0, 1) == 1:
        return "Hello, World!"

    return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
