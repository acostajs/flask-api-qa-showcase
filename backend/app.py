import os
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
