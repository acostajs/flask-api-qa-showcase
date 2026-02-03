from backend.database import db
from sqlalchemy.dialects.sqlite import JSON


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    availability = db.Column(JSON)

    shifts = db.relationship("Shift", backref="employee", lazy=True)

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}', role='{self.role}')>"


class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=False)

    def __repr__(self):
        return f"<Shift(id={self.id}, day='{self.day}', start_time='{self.start_time}', end_time='{self.end_time}', employee_id={self.employee_id})>"
