import random
from locust import HttpUser, between, task


class EmployeeUser(HttpUser):
    wait_time = between(1, 2)
    created_employee_ids: list[int] = []

    def on_start(self) -> None:
        """Runs when a user starts simulated traffic."""
        self.created_employee_ids = []

    @task(3)
    def view_employees(self) -> None:
        """Simulates viewing the list of all employees."""
        self.client.get("/employees")

    @task(3)
    def view_shifts(self) -> None:
        """Simulates viewing the list of all shifts."""
        self.client.get("/shifts")

    @task(1)
    def employee_lifecycle(self) -> None:
        """Simulates creating an employee, viewing details, and deleting them."""
        payload = {
            "name": f"Perf User {random.randint(1000, 9999)}",
            "role": "Consultant",
            "availability": {"monday": "12pm-4pm"},
        }
        with self.client.post(
            "/employees", json=payload, catch_response=True
        ) as response:
            if response.status_code == 201:
                data = response.json()
                emp_id = data.get("id")
                if emp_id:
                    # View details
                    self.client.get(f"/employees/{emp_id}")
                    # Clean up / Delete
                    self.client.delete(f"/employees/{emp_id}")
            else:
                response.failure(
                    f"Failed to create employee during lifecycle simulation (status: {response.status_code})"
                )
