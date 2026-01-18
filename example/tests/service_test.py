import pytest

ENDPOINT_URL = "/flaky-service"


def test_normal_gateway_response_is_flaky(client):
    response = client.get(ENDPOINT_URL)
    assert response.status_code in [200, 400, 404, 429, 500, 504]


@pytest.mark.parametrize(
    "path_param, code",
    [
        ("ok", 200),
        ("bad_request", 400),
        ("not_found", 404),
        ("error", 500),
        ("high_latency", 504),
        ("rate_limited", 429),
    ],
)
def test_service_returns_appropriate_response_based_on_path_parameter(
    client, path_param, code
):
    response = client.get(f"{ENDPOINT_URL}/{path_param}")
    json = response.json()

    assert json["status"] == code
