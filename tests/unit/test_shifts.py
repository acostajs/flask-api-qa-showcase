from flask.testing import FlaskClient
from sqlalchemy.orm import scoped_session
from backend.models.models import Employee, Shift


def test_create_shift_success(client: FlaskClient, db_session: scoped_session) -> None:
    """Test successful shift creation."""
    # First create an employee to associate with the shift
    emp = Employee(name="John Doe", role="Developer", availability={})
    db_session.add(emp)
    db_session.commit()

    payload = {
        "start_time": "09:00",
        "end_time": "17:00",
        "day": "Monday",
        "employee_id": emp.id,
    }
    response = client.post("/shifts", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert data is not None
    assert "id" in data
    assert data["start_time"] == "09:00"
    assert data["end_time"] == "17:00"
    assert data["day"] == "Monday"
    assert data["employee_id"] == emp.id


def test_create_shift_missing_fields(
    client: FlaskClient, db_session: scoped_session
) -> None:
    """Test shift creation fails when required fields are missing."""
    # First create an employee
    emp = Employee(name="John Doe", role="Developer", availability={})
    db_session.add(emp)
    db_session.commit()

    payload = {
        "start_time": "09:00",
        # Missing end_time, day, employee_id
    }
    response = client.post("/shifts", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data is not None
    assert "error" in data
    assert data["error"] == "Missing required shift fields"


def test_get_shifts_empty(client: FlaskClient) -> None:
    """Test get shifts returns an empty list when no shifts exist."""
    response = client.get("/shifts")
    assert response.status_code == 200
    data = response.get_json()
    assert data == []


def test_get_shifts_populated(client: FlaskClient, db_session: scoped_session) -> None:
    """Test get shifts returns all shifts."""
    # Seed database
    emp = Employee(name="Alice", role="Manager", availability={})
    db_session.add(emp)
    db_session.commit()

    shift1 = Shift(
        start_time="08:00", end_time="16:00", day="Wednesday", employee_id=emp.id
    )
    shift2 = Shift(
        start_time="12:00", end_time="20:00", day="Thursday", employee_id=emp.id
    )
    db_session.add(shift1)
    db_session.add(shift2)
    db_session.commit()

    response = client.get("/shifts")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert len(data) == 2
    assert {s["day"] for s in data} == {"Wednesday", "Thursday"}


def test_get_shift_success(client: FlaskClient, db_session: scoped_session) -> None:
    """Test get a single shift by ID."""
    emp = Employee(name="Charlie", role="Intern", availability={})
    db_session.add(emp)
    db_session.commit()

    shift = Shift(
        start_time="09:00", end_time="13:00", day="Friday", employee_id=emp.id
    )
    db_session.add(shift)
    db_session.commit()

    response = client.get(f"/shifts/{shift.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data["id"] == shift.id
    assert data["day"] == "Friday"


def test_get_shift_not_found(client: FlaskClient) -> None:
    """Test get shift returns 404 if shift does not exist."""
    response = client.get("/shifts/999")
    assert response.status_code == 404
    data = response.get_json()
    assert data is not None
    assert "error" in data
    assert data["error"] == "Shift not found"


def test_update_shift_success(client: FlaskClient, db_session: scoped_session) -> None:
    """Test successfully updating a shift."""
    emp1 = Employee(name="Dave", role="Staff", availability={})
    emp2 = Employee(name="Eve", role="Staff", availability={})
    db_session.add_all([emp1, emp2])
    db_session.commit()

    shift = Shift(
        start_time="09:00", end_time="17:00", day="Monday", employee_id=emp1.id
    )
    db_session.add(shift)
    db_session.commit()

    payload = {
        "start_time": "08:00",
        "end_time": "16:00",
        "day": "Tuesday",
        "employee_id": emp2.id,
    }
    response = client.put(f"/shifts/{shift.id}", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data["id"] == shift.id
    assert data["start_time"] == "08:00"
    assert data["end_time"] == "16:00"
    assert data["day"] == "Tuesday"
    assert data["employee_id"] == emp2.id


def test_update_shift_missing_fields(
    client: FlaskClient, db_session: scoped_session
) -> None:
    """Test updating a shift fails with missing fields."""
    emp = Employee(name="Eve", role="Staff", availability={})
    db_session.add(emp)
    db_session.commit()

    shift = Shift(
        start_time="09:00", end_time="17:00", day="Monday", employee_id=emp.id
    )
    db_session.add(shift)
    db_session.commit()

    payload = {
        "start_time": "08:00",
        # Missing end_time, day, employee_id
    }
    response = client.put(f"/shifts/{shift.id}", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data is not None
    assert "error" in data
    assert data["error"] == "Missing required shift fields"


def test_update_shift_not_found(
    client: FlaskClient, db_session: scoped_session
) -> None:
    """Test updating a non-existent shift returns 404."""
    emp = Employee(name="Ghost", role="Intern", availability={})
    db_session.add(emp)
    db_session.commit()

    payload = {
        "start_time": "09:00",
        "end_time": "17:00",
        "day": "Monday",
        "employee_id": emp.id,
    }
    response = client.put("/shifts/999", json=payload)
    assert response.status_code == 404
    data = response.get_json()
    assert data is not None
    assert "error" in data
    assert data["error"] == "Shift not found"


def test_delete_shift_success(client: FlaskClient, db_session: scoped_session) -> None:
    """Test successfully deleting a shift."""
    emp = Employee(name="Frank", role="Staff", availability={})
    db_session.add(emp)
    db_session.commit()

    shift = Shift(
        start_time="09:00", end_time="17:00", day="Monday", employee_id=emp.id
    )
    db_session.add(shift)
    db_session.commit()

    response = client.delete(f"/shifts/{shift.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert "message" in data
    assert data["message"] == "Shift deleted successfully"

    # Verify deleted from DB
    deleted_shift = db_session.get(Shift, shift.id)
    assert deleted_shift is None


def test_delete_shift_not_found(client: FlaskClient) -> None:
    """Test deleting a non-existent shift returns 404."""
    response = client.delete("/shifts/999")
    assert response.status_code == 404
    data = response.get_json()
    assert data is not None
    assert "error" in data
    assert data["error"] == "Shift not found"
