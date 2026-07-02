import os
from typing import Any, Dict, List, Optional, Tuple
from flask import Flask, request, jsonify
from backend.database import db
from backend.models.models import Employee, Shift
from backend.schemas import EmployeeSchema, ShiftSchema

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///../instance/site.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()


employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)
shift_schema = ShiftSchema()
shifts_schema = ShiftSchema(many=True)


def validate_availability(availability: Any) -> bool:
    """Validate that availability is a dictionary with string keys and string/dict values."""
    if not isinstance(availability, dict):
        return False
    for key, val in availability.items():
        if not isinstance(key, str):
            return False
        if not isinstance(val, (str, dict)):
            return False
        if isinstance(val, dict):
            if "start" not in val or "end" not in val:
                return False
    return True


def parse_time_to_minutes(time_str: str) -> int:
    """Parse time string (e.g., '09:30', '9', '17:00') into minutes since midnight."""
    time_str = time_str.strip().lower()

    is_pm = False
    is_am = False
    if time_str.endswith("pm"):
        is_pm = True
        time_str = time_str[:-2].strip()
    elif time_str.endswith("am"):
        is_am = True
        time_str = time_str[:-2].strip()

    if ":" in time_str:
        parts = time_str.split(":")
        try:
            h = int(parts[0])
            m = int(parts[1])
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}")
    else:
        try:
            h = int(time_str)
            m = 0
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}")

    if is_pm and h < 12:
        h += 12
    elif is_am and h == 12:
        h = 0

    if not (0 <= h <= 24 and 0 <= m < 60):
        raise ValueError(f"Time out of bounds: {h}:{m}")

    return h * 60 + m


def is_shift_in_availability(
    shift_day: str,
    shift_start_str: str,
    shift_end_str: str,
    availability: Dict[str, Any],
) -> Tuple[bool, str]:
    """Check if shift times fall entirely within the employee's availability for that day."""
    avail_val = None
    for k, v in availability.items():
        if k.lower() == shift_day.lower():
            avail_val = v
            break

    if not avail_val:
        return False, f"Employee is not available on {shift_day}"

    try:
        s_minutes = parse_time_to_minutes(shift_start_str)
        e_minutes = parse_time_to_minutes(shift_end_str)
    except ValueError as e:
        return False, f"Invalid shift time: {e}"

    if s_minutes >= e_minutes:
        return False, "Shift start time must be before end time"

    try:
        if isinstance(avail_val, dict):
            a_start_str = avail_val.get("start", "")
            a_end_str = avail_val.get("end", "")
        elif isinstance(avail_val, str):
            if "-" in avail_val:
                parts = avail_val.split("-")
                a_start_str, a_end_str = parts[0].strip(), parts[1].strip()
            else:
                a_start_str, a_end_str = avail_val, ""
        else:
            return False, f"Invalid availability format for {shift_day}"

        if not a_start_str or not a_end_str:
            return False, f"Employee is not available on {shift_day}"

        a_start_minutes = parse_time_to_minutes(a_start_str)
        a_end_minutes = parse_time_to_minutes(a_end_str)
    except ValueError as e:
        return False, f"Invalid availability time for {shift_day}: {e}"

    if s_minutes < a_start_minutes or e_minutes > a_end_minutes:
        return (
            False,
            f"Shift ({shift_start_str} - {shift_end_str}) falls outside availability ({a_start_str} - {a_end_str}) for {shift_day}",
        )

    return True, ""


def check_shift_overlap(
    shift_id: Optional[int],
    employee_id: int,
    day: str,
    start_str: str,
    end_str: str,
    existing_shifts: List[Shift],
) -> Tuple[bool, str]:
    """Check if the proposed shift overlaps with any existing scheduled shifts for the employee."""
    try:
        s_minutes = parse_time_to_minutes(start_str)
        e_minutes = parse_time_to_minutes(end_str)
    except ValueError as e:
        return False, f"Invalid shift time: {e}"

    for shift in existing_shifts:
        if shift.employee_id != employee_id or shift.day.lower() != day.lower():
            continue

        if shift_id is not None and shift.id == shift_id:
            continue

        try:
            ex_start = parse_time_to_minutes(shift.start_time)
            ex_end = parse_time_to_minutes(shift.end_time)
        except ValueError:
            continue

        # Overlap logic: s1 < e2 and s2 < e1
        if s_minutes < ex_end and ex_start < e_minutes:
            return (
                False,
                f"Shift overlaps with existing shift #{shift.id} ({shift.start_time} - {shift.end_time}) on {day}",
            )

    return True, ""


@app.post("/employees")
def create_employee():
    data = request.get_json()
    if (
        not data
        or "name" not in data
        or "role" not in data
        or "availability" not in data
    ):
        return jsonify({"error": "Missing required fields"}), 400

    if not validate_availability(data["availability"]):
        return jsonify({"error": "Invalid availability format"}), 400

    new_employee = Employee(
        name=data["name"], role=data["role"], availability=data["availability"]
    )
    db.session.add(new_employee)
    db.session.commit()
    result = employee_schema.dump(new_employee)
    return jsonify(result), 201


@app.get("/employees")
def get_employees():
    all_employees = db.session.query(Employee).all()
    result = employees_schema.dump(all_employees)
    return jsonify(result)


@app.get("/employees/<int:employee_id>")
def get_employee(employee_id):
    employee = db.session.get(Employee, employee_id)
    if employee:
        result = employee_schema.dump(employee)
        return jsonify(result)
    return jsonify({"error": "Employee not found"}), 404


@app.put("/employees/<int:employee_id>")
def update_employee(employee_id):
    employee = db.session.get(Employee, employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    data = request.get_json()
    if (
        not data
        or "name" not in data
        or "role" not in data
        or "availability" not in data
    ):
        return jsonify({"error": "Missing required fields"}), 400

    if not validate_availability(data["availability"]):
        return jsonify({"error": "Invalid availability format"}), 400

    employee.name = data["name"]
    employee.role = data["role"]
    employee.availability = data["availability"]
    db.session.commit()
    result = employee_schema.dump(employee)
    return jsonify(result)


@app.delete("/employees/<int:employee_id>")
def delete_employee(employee_id):
    employee = db.session.get(Employee, employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    db.session.delete(employee)
    db.session.commit()
    return jsonify({"message": "Employee deleted successfully"}), 200


@app.post("/shifts")
def create_shift():
    data = request.get_json()
    if (
        not data
        or "start_time" not in data
        or "end_time" not in data
        or "day" not in data
        or "employee_id" not in data
    ):
        return jsonify({"error": "Missing required shift fields"}), 400

    employee = db.session.get(Employee, data["employee_id"])
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    # Validate availability if defined
    if employee.availability:
        ok, err_msg = is_shift_in_availability(
            data["day"], data["start_time"], data["end_time"], employee.availability
        )
        if not ok:
            return jsonify({"error": err_msg}), 400

    # Check for overlaps
    existing_shifts = (
        db.session.query(Shift).filter(Shift.employee_id == employee.id).all()
    )
    ok, err_msg = check_shift_overlap(
        None,
        employee.id,
        data["day"],
        data["start_time"],
        data["end_time"],
        existing_shifts,
    )
    if not ok:
        return jsonify({"error": err_msg}), 400

    new_shift = Shift(
        start_time=data["start_time"],
        end_time=data["end_time"],
        day=data["day"],
        employee_id=data["employee_id"],
    )
    db.session.add(new_shift)
    db.session.commit()
    result = shift_schema.dump(new_shift)
    return jsonify(result), 201


@app.get("/shifts")
def get_shifts():
    all_shifts = db.session.query(Shift).all()
    result = shifts_schema.dump(all_shifts)
    return jsonify(result)


@app.get("/shifts/<int:shift_id>")
def get_shift(shift_id):
    shift = db.session.get(Shift, shift_id)
    if shift:
        result = shift_schema.dump(shift)
        return jsonify(result)
    return jsonify({"error": "Shift not found"}), 404


@app.put("/shifts/<int:shift_id>")
def update_shift(shift_id):
    shift = db.session.get(Shift, shift_id)
    if not shift:
        return jsonify({"error": "Shift not found"}), 404

    data = request.get_json()
    if (
        not data
        or "start_time" not in data
        or "end_time" not in data
        or "day" not in data
        or "employee_id" not in data
    ):
        return jsonify({"error": "Missing required shift fields"}), 400

    employee = db.session.get(Employee, data["employee_id"])
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    # Validate availability if defined
    if employee.availability:
        ok, err_msg = is_shift_in_availability(
            data["day"], data["start_time"], data["end_time"], employee.availability
        )
        if not ok:
            return jsonify({"error": err_msg}), 400

    # Check for overlaps
    existing_shifts = (
        db.session.query(Shift).filter(Shift.employee_id == employee.id).all()
    )
    ok, err_msg = check_shift_overlap(
        shift_id,
        employee.id,
        data["day"],
        data["start_time"],
        data["end_time"],
        existing_shifts,
    )
    if not ok:
        return jsonify({"error": err_msg}), 400

    shift.start_time = data["start_time"]
    shift.end_time = data["end_time"]
    shift.day = data["day"]
    shift.employee_id = data["employee_id"]
    db.session.commit()
    result = shift_schema.dump(shift)
    return jsonify(result)


@app.delete("/shifts/<int:shift_id>")
def delete_shift(shift_id):
    shift = db.session.get(Shift, shift_id)
    if not shift:
        return jsonify({"error": "Shift not found"}), 404

    db.session.delete(shift)
    db.session.commit()
    return jsonify({"message": "Shift deleted successfully"}), 200
