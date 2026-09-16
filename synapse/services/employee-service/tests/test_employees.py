import pytest


@pytest.fixture()
def foundation_objects(client):
    client.post("/departments", json={"external_code": "DEP-100", "name": "Tecnologia"})
    client.post("/cost-centers", json={"external_code": "CC-100", "name": "CeCo Tecnologia"})
    client.post(
        "/locations",
        json={"external_code": "LOC-100", "name": "Oficina CDMX", "city": "CDMX", "country": "MX"},
    )
    return {"department_id": "DEP-100", "cost_center_id": "CC-100", "location_id": "LOC-100"}


def _employee_payload(foundation_objects, person_id="E1000001", manager_person_id=None):
    return {
        "person_id_external": person_id,
        "date_of_birth": "1990-05-10",
        "gender": "F",
        "personal": {
            "first_name": "Ana",
            "last_name": "Garcia",
            "marital_status": "single",
            "nationality": "MX",
        },
        "emails": [
            {"email_type": "business", "email_address": f"{person_id.lower()}@synapse-demo.com", "is_primary": True}
        ],
        "phones": [{"phone_type": "mobile", "phone_number": "5512345678", "is_primary": True}],
        "employment": {"start_date": "2022-01-10"},
        "job": {
            "job_start_date": "2022-01-10",
            "job_title": "Desarrolladora de Software",
            "department_id": foundation_objects["department_id"],
            "cost_center_id": foundation_objects["cost_center_id"],
            "location_id": foundation_objects["location_id"],
            "manager_person_id": manager_person_id,
            "employment_type": "full_time",
            "standard_hours": 40,
        },
    }


def test_create_and_get_employee(client, foundation_objects):
    payload = _employee_payload(foundation_objects)
    resp = client.post("/employees", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["person_id_external"] == "E1000001"
    assert body["job"]["department"]["external_code"] == "DEP-100"
    assert body["employment_status"] == "active"

    resp = client.get("/employees/E1000001")
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Ana"


def test_get_missing_employee_returns_404(client):
    resp = client.get("/employees/DOES-NOT-EXIST")
    assert resp.status_code == 404


def test_create_duplicate_employee_fails(client, foundation_objects):
    payload = _employee_payload(foundation_objects)
    client.post("/employees", json=payload)
    resp = client.post("/employees", json=payload)
    assert resp.status_code == 409


def test_create_employee_with_unknown_manager_fails(client, foundation_objects):
    payload = _employee_payload(foundation_objects, manager_person_id="E-NO-EXISTE")
    resp = client.post("/employees", json=payload)
    assert resp.status_code == 400


def test_update_employee_job(client, foundation_objects):
    payload = _employee_payload(foundation_objects)
    client.post("/employees", json=payload)

    resp = client.patch("/employees/E1000001", json={"job": {"job_title": "Tech Lead"}})
    assert resp.status_code == 200
    assert resp.json()["job"]["job_title"] == "Tech Lead"


def test_terminate_employee(client, foundation_objects):
    payload = _employee_payload(foundation_objects)
    client.post("/employees", json=payload)

    resp = client.post(
        "/employees/E1000001/terminate",
        json={"end_date": "2024-01-01", "termination_reason": "Renuncia voluntaria"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["employment_status"] == "terminated"
    assert body["termination_date"] == "2024-01-01"


def test_direct_reports(client, foundation_objects):
    manager_payload = _employee_payload(foundation_objects, person_id="E2000001")
    client.post("/employees", json=manager_payload)

    report_payload = _employee_payload(foundation_objects, person_id="E2000002", manager_person_id="E2000001")
    client.post("/employees", json=report_payload)

    resp = client.get("/employees/E2000001/direct-reports")
    assert resp.status_code == 200
    reports = resp.json()
    assert len(reports) == 1
    assert reports[0]["person_id_external"] == "E2000002"


def test_list_employees_filter_by_department(client, foundation_objects):
    payload = _employee_payload(foundation_objects, person_id="E3000001")
    client.post("/employees", json=payload)

    resp = client.get("/employees", params={"department_id": "DEP-100"})
    assert resp.status_code == 200
    assert any(e["person_id_external"] == "E3000001" for e in resp.json())

    resp = client.get("/employees", params={"department_id": "DEP-999"})
    assert resp.json() == []
