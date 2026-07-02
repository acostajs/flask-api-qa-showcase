from typing import Any, Dict, Optional
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Input, Label, Static
from tui.client import APIClient, get_error_message


def format_availability(availability: Dict[str, Any]) -> str:
    """Format availability dict to a human-readable multi-line string."""
    if not availability or not isinstance(availability, dict):
        return "Not set"

    DAY_ORDER = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    parts = []

    for d in DAY_ORDER:
        # Find key case-insensitively
        val = None
        for k, v in availability.items():
            if k.lower() == d:
                val = v
                break
        if not val:
            continue

        day_label = d[:3].capitalize()

        # Parse value
        if isinstance(val, dict):
            start = val.get("start", "")
            end = val.get("end", "")
            if start and end:
                parts.append(f"{day_label}: {start} - {end}")
        elif isinstance(val, str):
            val_clean = val.strip()
            if val_clean and val_clean.lower() != "off":
                parts.append(f"{day_label}: {val_clean}")

    if not parts:
        return "Not set"

    return "\n".join(parts)


class EmployeesTab(Horizontal):
    """TUI Pane for viewing and managing employee records."""

    def __init__(self, client: APIClient, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client: APIClient = client
        self.editing_id: Optional[int] = None
        self._employees_cache: Dict[int, Dict[str, Any]] = {}

    def compose(self) -> ComposeResult:
        with Vertical(id="emp_list_pane"):
            yield Static("Employee Directory", classes="section-title")
            yield DataTable(id="emp_table")
            with Horizontal(id="emp_controls"):
                yield Button("Refresh", id="btn_emp_refresh", variant="primary")
                yield Button("Edit Selected", id="btn_emp_edit", variant="warning")
                yield Button("Delete Selected", id="btn_emp_delete", variant="error")

        with Vertical(id="emp_form_pane"):
            yield Static(
                "Add New Employee", id="emp_form_title", classes="section-title"
            )
            yield Label("Name:")
            yield Input(placeholder="e.g. Alice Smith", id="inp_emp_name")
            yield Label("Role:")
            yield Input(placeholder="e.g. Shift Manager", id="inp_emp_role")
            yield Label("Availability (Start - End):")
            with Vertical(id="emp_avail_container"):
                for day in [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]:
                    with Horizontal(classes="avail-row"):
                        yield Label(day[:3], classes="avail-day-label")
                        yield Input(
                            placeholder="Start",
                            classes="avail-input-start",
                            id=f"inp_avail_{day.lower()}_start",
                        )
                        yield Static("to", classes="avail-to")
                        yield Input(
                            placeholder="End",
                            classes="avail-input-end",
                            id=f"inp_avail_{day.lower()}_end",
                        )
            yield Label("", id="emp_form_error", classes="error-label")
            with Horizontal(id="emp_form_buttons"):
                yield Button("Save", id="btn_emp_save", variant="success")
                yield Button("Clear", id="btn_emp_clear")

    def on_mount(self) -> None:
        table = self.query_one("#emp_table", DataTable)
        table.cursor_type = "row"
        table.add_columns("ID", "Name", "Role", "Weekly Hours", "Availability")
        self.run_worker(self.refresh_employees())

    async def refresh_employees(self) -> None:
        """Fetch and populate the DataTable of employees from the REST backend."""
        table = self.query_one("#emp_table", DataTable)
        table.clear()

        # Fetch shifts to calculate weekly hours
        shifts_resp = await self.client.request("GET", "/shifts")
        emp_hours = {}
        if shifts_resp.status_code == 200:
            for s in shifts_resp.json():
                eid = s.get("employee_id")
                start = s.get("start_time", "")
                end = s.get("end_time", "")
                duration = 0.0
                try:

                    def parse_to_min(t: str) -> int:
                        t = t.strip().lower()
                        is_pm = t.endswith("pm")
                        is_am = t.endswith("am")
                        if is_pm or is_am:
                            t = t[:-2].strip()
                        if ":" in t:
                            parts = t.split(":")
                            h, m = int(parts[0]), int(parts[1])
                        else:
                            h, m = int(t), 0
                        if is_pm and h < 12:
                            h += 12
                        elif is_am and h == 12:
                            h = 0
                        return h * 60 + m

                    diff = parse_to_min(end) - parse_to_min(start)
                    if diff >= 0:
                        duration = diff / 60.0
                except Exception:
                    pass
                if eid is not None:
                    emp_hours[eid] = emp_hours.get(eid, 0.0) + duration

        response = await self.client.request("GET", "/employees")
        if response.status_code == 200:
            employees = response.json()
            self._employees_cache.clear()
            for emp in employees:
                emp_id = emp.get("id")
                if emp_id is not None:
                    self._employees_cache[emp_id] = emp

                avail_str = format_availability(emp.get("availability", {}))
                hours_val = emp_hours.get(emp.get("id"), 0.0)
                table.add_row(
                    str(emp.get("id", "")),
                    emp.get("name", ""),
                    emp.get("role", ""),
                    f"{hours_val:.1f}h",
                    avail_str,
                    key=str(emp.get("id", "")),
                )
        else:
            self.query_one("#emp_form_error", Label).update("Failed to fetch employees")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "btn_emp_refresh":
            await self.refresh_employees()
        elif button_id == "btn_emp_clear":
            self.clear_form()
        elif button_id == "btn_emp_delete":
            await self.delete_selected()
        elif button_id == "btn_emp_edit":
            self.edit_selected()
        elif button_id == "btn_emp_save":
            await self.save_employee()

    def clear_form(self) -> None:
        """Reset the input fields to default empty state."""
        self.editing_id = None
        self.query_one("#emp_form_title", Static).update("Add New Employee")
        self.query_one("#inp_emp_name", Input).value = ""
        self.query_one("#inp_emp_role", Input).value = ""
        for day in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]:
            self.query_one(f"#inp_avail_{day}_start", Input).value = ""
            self.query_one(f"#inp_avail_{day}_end", Input).value = ""
        self.query_one("#emp_form_error", Label).update("")

    def edit_selected(self) -> None:
        """Load selected row values into inputs to initiate edit mode."""
        table = self.query_one("#emp_table", DataTable)
        cell_key = table.coordinate_to_cell_key(table.cursor_coordinate)
        if not cell_key:
            self.query_one("#emp_form_error", Label).update("No employee selected")
            return

        row_key = cell_key.row_key.value
        if not row_key:
            return

        row = table.get_row(row_key)
        self.editing_id = int(row[0])
        self.query_one("#emp_form_title", Static).update(
            f"Edit Employee #{self.editing_id}"
        )
        self.query_one("#inp_emp_name", Input).value = row[1]
        self.query_one("#inp_emp_role", Input).value = row[2]
        emp = self._employees_cache.get(self.editing_id, {})
        avail_dict = emp.get("availability", {})
        if not isinstance(avail_dict, dict):
            avail_dict = {}

        for day in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]:
            val = avail_dict.get(day) or avail_dict.get(day.capitalize()) or ""
            start, end = "", ""
            if isinstance(val, dict):
                start = val.get("start", "")
                end = val.get("end", "")
            elif isinstance(val, str) and val:
                if "-" in val:
                    parts = val.split("-")
                    start, end = parts[0].strip(), parts[1].strip()
                else:
                    start = val

            self.query_one(f"#inp_avail_{day}_start", Input).value = start
            self.query_one(f"#inp_avail_{day}_end", Input).value = end

        self.query_one("#emp_form_error", Label).update("")

    async def delete_selected(self) -> None:
        """Delete selected employee via DELETE endpoint."""
        table = self.query_one("#emp_table", DataTable)
        try:
            cell_key = table.coordinate_to_cell_key(table.cursor_coordinate)
            row_key = cell_key.row_key.value
            row = table.get_row(row_key)
            emp_id = int(row[0])
        except Exception:
            self.query_one("#emp_form_error", Label).update("No employee selected")
            return

        response = await self.client.request("DELETE", f"/employees/{emp_id}")
        if response.status_code == 200:
            await self.refresh_employees()
            self.clear_form()
            if hasattr(self.app, "refresh_shifts_tab_dropdown"):
                await self.app.refresh_shifts_tab_dropdown()
        else:
            err = get_error_message(response, "Failed to delete employee")
            self.query_one("#emp_form_error", Label).update(err)

    async def save_employee(self) -> None:
        """Submit the employee data via POST or PUT to the REST API."""
        name = self.query_one("#inp_emp_name", Input).value.strip()
        role = self.query_one("#inp_emp_role", Input).value.strip()
        if not name or not role:
            self.query_one("#emp_form_error", Label).update(
                "Name and Role are required"
            )
            return

        availability = {}
        for day in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]:
            start = self.query_one(f"#inp_avail_{day}_start", Input).value.strip()
            end = self.query_one(f"#inp_avail_{day}_end", Input).value.strip()
            if start or end:
                availability[day] = {"start": start, "end": end}

        payload = {"name": name, "role": role, "availability": availability}

        if self.editing_id is not None:
            response = await self.client.request(
                "PUT", f"/employees/{self.editing_id}", json_data=payload
            )
        else:
            response = await self.client.request(
                "POST", "/employees", json_data=payload
            )

        if response.status_code in (200, 201):
            await self.refresh_employees()
            self.clear_form()
            if hasattr(self.app, "refresh_shifts_tab_dropdown"):
                await self.app.refresh_shifts_tab_dropdown()
        else:
            err = get_error_message(response, "Failed to save employee")
            self.query_one("#emp_form_error", Label).update(err)
