def test_flaky_service_endpoint(client):
    response = client.get("/flaky-service")
    assert response.status_code in [200, 500]
