from breaker import Breaker, BreakerCircuitOpenException
from example.api.api import ServiceBehaviour

ENDPOINT_URL = "/flaky-service"


def make_request(client, mode: ServiceBehaviour | None = None):
    response = client.get(f"{ENDPOINT_URL}/{mode.value}")
    if response.json()["status"] not in [200, 201]:
        raise Exception
    return response


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


# def test_gateway_resumes_service_after_retry_timeout

# def test_gateway_ignores_client_errors_and_stays_closed
