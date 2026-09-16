def test_create_and_list_department(client):
    resp = client.post("/departments", json={"external_code": "DEP-9000", "name": "Innovacion"})
    assert resp.status_code == 201
    assert resp.json()["external_code"] == "DEP-9000"

    resp = client.get("/departments")
    assert resp.status_code == 200
    codes = [d["external_code"] for d in resp.json()]
    assert "DEP-9000" in codes


def test_create_duplicate_department_fails(client):
    client.post("/departments", json={"external_code": "DEP-9001", "name": "Legal"})
    resp = client.post("/departments", json={"external_code": "DEP-9001", "name": "Legal 2"})
    assert resp.status_code == 409


def test_update_department(client):
    client.post("/departments", json={"external_code": "DEP-9002", "name": "Marketing"})
    resp = client.patch("/departments/DEP-9002", json={"status": "inactive"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "inactive"


def test_get_missing_department_returns_404(client):
    resp = client.get("/departments/DEP-DOES-NOT-EXIST")
    assert resp.status_code == 404


def test_create_and_list_cost_center(client):
    resp = client.post("/cost-centers", json={"external_code": "CC-9000", "name": "CeCo Innovacion"})
    assert resp.status_code == 201

    resp = client.get("/cost-centers")
    codes = [c["external_code"] for c in resp.json()]
    assert "CC-9000" in codes


def test_create_and_list_location(client):
    resp = client.post(
        "/locations",
        json={"external_code": "LOC-9000", "name": "Oficina Test", "city": "CDMX", "country": "MX"},
    )
    assert resp.status_code == 201

    resp = client.get("/locations")
    codes = [loc["external_code"] for loc in resp.json()]
    assert "LOC-9000" in codes
