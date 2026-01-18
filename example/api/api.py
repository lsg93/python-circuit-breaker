import random
from enum import Enum

from fastapi import APIRouter, status

router = APIRouter()


# Use an enum for the different path parameters
class ServiceBehaviour(Enum):
    OK = "ok"
    BAD_REQUEST = "bad_request"
    NOT_FOUND = "not_found"
    ERROR = "error"
    HIGH_LATENCY = "high_latency"  # ??
    RATE_LIMITED = "rate_limited"


@router.get("/flaky-service")
@router.get("/flaky-service/{behaviour}")
def flaky_service(behaviour: ServiceBehaviour | None = None):
    if behaviour is None:
        behaviour = random.choice(list(ServiceBehaviour))

    match behaviour:
        case ServiceBehaviour.OK:
            return {"status": status.HTTP_200_OK}
        case ServiceBehaviour.BAD_REQUEST:
            return {"status": status.HTTP_400_BAD_REQUEST}
        case ServiceBehaviour.NOT_FOUND:
            return {"status": status.HTTP_404_NOT_FOUND}
        case ServiceBehaviour.ERROR:
            return {"status": status.HTTP_500_INTERNAL_SERVER_ERROR}
        case ServiceBehaviour.HIGH_LATENCY:
            return {"status": status.HTTP_504_GATEWAY_TIMEOUT}
        case ServiceBehaviour.RATE_LIMITED:
            return {"status": status.HTTP_429_TOO_MANY_REQUESTS}
