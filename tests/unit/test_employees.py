from flask.testing import FlaskClient
from sqlalchemy.orm import scoped_session
from backend.models.models import Employee


def test_create_employee_success(client: FlaskClient) -> None:
    """Test successful employee creation."""
    payload = {
        "name": "John Doe",
        "role": "Developer",
        "availability": {"monday": "9am-5pm", "tuesday": "9am-5pm"},
    }
    response = client.post("/employees", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert data is not None
    assert "id" in data
    assert data["name"] == "John Doe"
    assert data["role"] == "Developer"
    assert data["availability"] == {"monday": "9am-5pm", "tuesday": "9am-5pm"}


def test_create_employee_missing_fields(client: FlaskClient) -> None:
    """Test employee creation fails when required fields are missing."""
    payload = {
        "name": "John Doe",
        # Missing role and availability
    }
    response = client.post("/employees", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data is not None
    assert "error" in data
    assert data["error"] == "Missing required fields"


def test_get_employees_empty(client: FlaskClient) -> None:
    """Test get employees returns an empty list when no employees exist."""
    response = client.get("/employees")
    assert response.status_code == 200
    data = response.get_json()
    assert data == []


def test_get_employees_populated(
    client: FlaskClient, db_session: scoped_session
) -> None:
    """Test get employees returns all employees."""
    # Seed database
    emp1 = Employee(name="Alice", role="Manager", availability={"wednesday": "8am-4pm"})
    emp2 = Employee(name="Bob", role="Cashier", availability={"thursday": "12pm-8pm"})
    db_session.add(emp1)
    db_session.add(emp2)
    db_session.commit()

    response = client.get("/employees")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert len(data) == 2
    assert {e["name"] for e in data} == {"Alice", "Bob"}


def test_get_employee_success(client: FlaskClient, db_session: scoped_session) -> None:
    """Test get a single employee by ID."""
    emp = Employee(name="Charlie", role="Intern", availability={"friday": "9am-1pm"})
    db_session.add(emp)
    db_session.commit()

    response = client.get(f"/employees/{emp.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data["id"] == emp.id
    assert data["name"] == "Charlie"


def test_get_employee_not_found(client: FlaskClient) -> None:
    """Test get employee returns 404 if employee does not exist."""
    response = client.get("/employees/999")
    assert response.status_code == 404
    data = response.get_json()
    assert data is not None
    assert "error" in data
    assert data["error"] == "Employee not found"


def test_update_employee_success(
    client: FlaskClient, db_session: scoped_session
) -> None:
    """Test successfully updating an employee."""
    emp = Employee(name="Dave", role="Staff", availability={"monday": "9am-5pm"})
    db_session.add(emp)
    db_session.commit()

    payload = {
        "name": "Dave Updated",
        "role": "Supervisor",
        "availability": {"monday": "8am-6pm"},
    }
    response = client.put(f"/employees/{emp.id}", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data["id"] == emp.id
    assert data["name"] == "Dave Updated"
    assert data["role"] == "Supervisor"
    assert data["availability"] == {"monday": "8am-6pm"}


def test_update_employee_missing_fields(
    client: FlaskClient, db_session: scoped_session
) -> None:
    """Test updating an employee fails with missing fields."""
    emp = Employee(name="Eve", role="Staff", availability={"monday": "9am-5pm"})
    db_session.add(emp)
    db_session.commit()

    payload = {
        "name": "Eve Updated",
        # Missing role and availability
    }
    response = client.put(f"/employees/{emp.id}", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data is not None
    assert "error" in data
    assert data["error"] == "Missing required fields"


def test_update_employee_not_found(client: FlaskClient) -> None:
    """Test updating a non-existent employee returns 404."""
    payload = {
        "name": "Nobody",
        "role": "Ghost",
        "availability": {},
    }
    response = client.put("/employees/999", json=payload)
    assert response.status_code == 404
    data = response.get_json()
    assert data is not None
    assert "error" in data
    assert data["error"] == "Employee not found"


def test_delete_employee_success(
    client: FlaskClient, db_session: scoped_session
) -> None:
    """Test successfully deleting an employee."""
    emp = Employee(name="Frank", role="Staff", availability={"monday": "9am-5pm"})
    db_session.add(emp)
    db_session.commit()

    response = client.delete(f"/employees/{emp.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert "message" in data
    assert data["message"] == "Employee deleted successfully"

    # Verify deleted from DB
    deleted_emp = db_session.get(Employee, emp.id)
    assert deleted_emp is None


def test_delete_employee_not_found(client: FlaskClient) -> None:
    """Test deleting a non-existent employee returns 404."""
    response = client.delete("/employees/999")
    assert response.status_code == 404
    data = response.get_json()
    assert data is not None
    assert "error" in data
    assert data["error"] == "Employee not found"
