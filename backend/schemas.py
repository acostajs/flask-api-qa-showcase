from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from backend.models.models import Employee, Shift


class EmployeeSchema(SQLAlchemySchema):
    class Meta:
        model = Employee
        load_instance = True  # Optional: Create model instances when loading

    id = auto_field()
    name = auto_field()
    role = auto_field()
    availability = auto_field()


class ShiftSchema(SQLAlchemySchema):
    class Meta:
        model = Shift
        load_instance = True

    id = auto_field()
    start_time = auto_field()
    end_time = auto_field()
    day = auto_field()
    employee_id = auto_field()
