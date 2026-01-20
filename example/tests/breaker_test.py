import time

import pytest

from breaker import Breaker, BreakerCircuitOpenException
from example.api.api import ServiceBehaviour

ENDPOINT_URL = "/flaky-service"


def test_breaker_trips_after_failing_more_than_threshold(client):
    attempts = 0
    failure_amount = 2
    breaker_instance = Breaker(failure_amount=failure_amount)

    for _ in range(failure_amount + 1):
        try:
            with breaker_instance:
                make_request(client, ServiceBehaviour.ERROR)
        except BreakerCircuitOpenException:
            continue
        except Exception:
            attempts += 1

    assert attempts == 2


def test_breaker_allows_requests_after_retry_timeout(client, time_machine):
    time_machine.move_to(time.time())

    retry_after = 60
    failure_amount = 2
    breaker_instance = Breaker(failure_amount=failure_amount, retry_after=retry_after)

    for _ in range(failure_amount):
        with pytest.raises(Exception):
            with breaker_instance:
                make_request(client, ServiceBehaviour.ERROR)

    with pytest.raises(BreakerCircuitOpenException):
        with breaker_instance:
            make_request(client, ServiceBehaviour.ERROR)

    time_machine.shift(retry_after + 1)

    with breaker_instance:
        response = make_request(client, ServiceBehaviour.OK)
        assert response.json()["status"] == 200


def make_request(client, mode: ServiceBehaviour | None = None):
    response = client.get(f"{ENDPOINT_URL}/{mode.value}")
    if response.json()["status"] not in [200, 201]:
        raise Exception
    return response
