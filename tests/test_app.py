def test_application_starts(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Digital Banking Backend" in response.json()["message"]


def test_openapi_schema_available(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "openapi" in response.json()
    assert "paths" in response.json()
