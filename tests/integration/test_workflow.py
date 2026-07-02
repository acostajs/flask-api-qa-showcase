import pytest
from flask.testing import FlaskClient
from sqlalchemy.orm import scoped_session
from sqlalchemy.exc import IntegrityError
from backend.models.models import Employee, Shift


def test_employee_shift_workflow(
    client: FlaskClient, db_session: scoped_session
) -> None:
    """Test the complete end-to-end integration workflow of employees and shifts."""
    # 1. Create a new employee
    payload_employee = {
        "name": "Jane Miller",
        "role": "Lead Architect",
        "availability": {"monday": "9am-5pm"},
    }
    resp_emp = client.post("/employees", json=payload_employee)
    assert resp_emp.status_code == 201
    emp_data = resp_emp.get_json()
    assert emp_data is not None
    emp_id = emp_data["id"]

    # 2. Verify employee is in the database and list endpoint
    resp_list = client.get("/employees")
    assert resp_list.status_code == 200
    list_data = resp_list.get_json()
    assert list_data is not None
    assert any(e["id"] == emp_id for e in list_data)

    # 3. Create a shift assigned to this employee
    payload_shift = {
        "start_time": "09:00",
        "end_time": "17:00",
        "day": "Monday",
        "employee_id": emp_id,
    }
    resp_shift = client.post("/shifts", json=payload_shift)
    assert resp_shift.status_code == 201
    shift_data = resp_shift.get_json()
    assert shift_data is not None
    shift_id = shift_data["id"]

    # 4. Verify shift is in the database and list endpoint
    resp_shift_list = client.get("/shifts")
    assert resp_shift_list.status_code == 200
    shift_list_data = resp_shift_list.get_json()
    assert shift_list_data is not None
    assert any(s["id"] == shift_id for s in shift_list_data)

    # 5. Retrieve both details individually
    resp_emp_detail = client.get(f"/employees/{emp_id}")
    assert resp_emp_detail.status_code == 200
    assert resp_emp_detail.get_json()["name"] == "Jane Miller"

    resp_shift_detail = client.get(f"/shifts/{shift_id}")
    assert resp_shift_detail.status_code == 200
    assert resp_shift_detail.get_json()["day"] == "Monday"

    # 6. Update employee and shift
    payload_emp_update = {
        "name": "Jane Miller Updated",
        "role": "Principal Architect",
        "availability": {"monday": "8am-4pm", "tuesday": "8am-4pm"},
    }
    resp_emp_update = client.put(f"/employees/{emp_id}", json=payload_emp_update)
    assert resp_emp_update.status_code == 200
    assert resp_emp_update.get_json()["name"] == "Jane Miller Updated"

    payload_shift_update = {
        "start_time": "08:00",
        "end_time": "16:00",
        "day": "Tuesday",
        "employee_id": emp_id,
    }
    resp_shift_update = client.put(f"/shifts/{shift_id}", json=payload_shift_update)
    assert resp_shift_update.status_code == 200
    assert resp_shift_update.get_json()["day"] == "Tuesday"

    # 7. Delete the shift
    resp_shift_delete = client.delete(f"/shifts/{shift_id}")
    assert resp_shift_delete.status_code == 200

    # Verify shift is deleted, employee still exists
    resp_shift_check = client.get(f"/shifts/{shift_id}")
    assert resp_shift_check.status_code == 404

    resp_emp_check = client.get(f"/employees/{emp_id}")
    assert resp_emp_check.status_code == 200

    # 8. Delete the employee
    resp_emp_delete = client.delete(f"/employees/{emp_id}")
    assert resp_emp_delete.status_code == 200

    resp_emp_check_again = client.get(f"/employees/{emp_id}")
    assert resp_emp_check_again.status_code == 404


def test_delete_employee_with_shifts_fails(
    client: FlaskClient, db_session: scoped_session
) -> None:
    """Test that deleting an employee that has active shifts raises IntegrityError due to SQL constraint."""
    # Create employee
    emp = Employee(name="Test Employee", role="Staff", availability={})
    db_session.add(emp)
    db_session.commit()

    # Create shift
    shift = Shift(
        start_time="09:00", end_time="17:00", day="Monday", employee_id=emp.id
    )
    db_session.add(shift)
    db_session.commit()

    # Deleting the employee should raise IntegrityError because shifts have nullable=False for employee_id
    with pytest.raises(IntegrityError):
        client.delete(f"/employees/{emp.id}")


def test_integration_scheduling_constraints(client: FlaskClient) -> None:
    """Test scheduling constraints integration workflow (availability & overlap validations)."""
    # 1. Create a new employee with Monday availability
    emp_payload = {
        "name": "Jane Scheduler",
        "role": "Coordinator",
        "availability": {"monday": "8am-4pm"},
    }
    resp_emp = client.post("/employees", json=emp_payload)
    assert resp_emp.status_code == 201
    emp_id = resp_emp.get_json()["id"]

    # 2. Try scheduling outside availability day (Tuesday)
    payload_tue = {
        "start_time": "09:00",
        "end_time": "17:00",
        "day": "Tuesday",
        "employee_id": emp_id,
    }
    resp_tue = client.post("/shifts", json=payload_tue)
    assert resp_tue.status_code == 400
    assert "not available on Tuesday" in resp_tue.get_json()["error"]

    # 3. Try scheduling outside availability hours on Monday (too early)
    payload_early = {
        "start_time": "07:00",
        "end_time": "15:00",
        "day": "Monday",
        "employee_id": emp_id,
    }
    resp_early = client.post("/shifts", json=payload_early)
    assert resp_early.status_code == 400
    assert "falls outside availability" in resp_early.get_json()["error"]

    # 4. Create first valid shift on Monday (8am - 12pm)
    payload_s1 = {
        "start_time": "08:00",
        "end_time": "12:00",
        "day": "Monday",
        "employee_id": emp_id,
    }
    resp_s1 = client.post("/shifts", json=payload_s1)
    assert resp_s1.status_code == 201
    s1_id = resp_s1.get_json()["id"]

    # 5. Create second valid shift on Monday (12pm - 4pm)
    payload_s2 = {
        "start_time": "12:00",
        "end_time": "16:00",
        "day": "Monday",
        "employee_id": emp_id,
    }
    resp_s2 = client.post("/shifts", json=payload_s2)
    assert resp_s2.status_code == 201
    s2_id = resp_s2.get_json()["id"]

    # 6. Try creating an overlapping shift on Monday (10am - 2pm)
    payload_overlap = {
        "start_time": "10:00",
        "end_time": "14:00",
        "day": "Monday",
        "employee_id": emp_id,
    }
    resp_overlap = client.post("/shifts", json=payload_overlap)
    assert resp_overlap.status_code == 400
    assert "overlaps with existing shift" in resp_overlap.get_json()["error"]

    # 7. Try updating first shift to overlap with second shift (8am - 2pm overlaps with 12pm - 4pm)
    payload_s1_update = {
        "start_time": "08:00",
        "end_time": "14:00",
        "day": "Monday",
        "employee_id": emp_id,
    }
    resp_update = client.put(f"/shifts/{s1_id}", json=payload_s1_update)
    assert resp_update.status_code == 400
    assert "overlaps with existing shift" in resp_update.get_json()["error"]

    # 8. Clean up
    client.delete(f"/shifts/{s1_id}")
    client.delete(f"/shifts/{s2_id}")
    client.delete(f"/employees/{emp_id}")
