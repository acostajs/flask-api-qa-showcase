from typing import Any, Dict, Optional
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Input, Label, Select, Static
from tui.client import APIClient, get_error_message


class ShiftsTab(Horizontal):
    """TUI Pane for viewing and scheduling employee work shifts."""

    def __init__(self, client: APIClient, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client: APIClient = client
        self.editing_id: Optional[int] = None
        self._employees_cache: Dict[int, str] = {}

    def compose(self) -> ComposeResult:
        with Vertical(id="shift_list_pane"):
            yield Static("Shift Schedule", classes="section-title")
            yield DataTable(id="shift_table")
            with Vertical(id="shift_summary_container"):
                yield Static("Daily Hours Coverage Status", classes="summary-title")
                yield Static("", id="lbl_shift_summary", classes="summary-markup")
            with Horizontal(id="shift_controls"):
                yield Button("Refresh", id="btn_shift_refresh", variant="primary")
                yield Button("Edit Selected", id="btn_shift_edit", variant="warning")
                yield Button("Delete Selected", id="btn_shift_delete", variant="error")

        with Vertical(id="shift_form_pane"):
            yield Static(
                "Add New Shift", id="shift_form_title", classes="section-title"
            )
            yield Label("Employee:")
            yield Select(options=[], id="sel_shift_employee", prompt="Select Employee")
            yield Label("Day of Week:")
            yield Input(placeholder="e.g. Monday", id="inp_shift_day")
            yield Label("Start Time:")
            yield Input(placeholder="e.g. 09:00", id="inp_shift_start")
            yield Label("End Time:")
            yield Input(placeholder="e.g. 17:00", id="inp_shift_end")
            yield Label("", id="shift_form_error", classes="error-label")
            with Horizontal(id="shift_form_buttons"):
                yield Button("Save", id="btn_shift_save", variant="success")
                yield Button("Clear", id="btn_shift_clear")

    def on_mount(self) -> None:
        table = self.query_one("#shift_table", DataTable)
        table.cursor_type = "row"
        table.add_columns("ID", "Employee", "Day", "Start Time", "End Time", "Duration")
        self.run_worker(self.refresh_all())

    async def refresh_all(self) -> None:
        """Refresh employee list cache and shifts table."""
        await self.refresh_employees_list()
        await self.refresh_shifts()

    async def refresh_employees_list(self) -> None:
        """Fetch list of employees to update the cache and dynamic dropdown menu."""
        response = await self.client.request("GET", "/employees")
        options = []
        self._employees_cache.clear()

        if response.status_code == 200:
            employees = response.json()
            for emp in employees:
                emp_id = emp.get("id")
                emp_name = emp.get("name", "Unknown")
                if emp_id is not None:
                    self._employees_cache[emp_id] = emp_name
                    options.append((f"{emp_name} (ID: {emp_id})", emp_id))

        select_widget = self.query_one("#sel_shift_employee", Select)
        select_widget.set_options(options)

    async def refresh_shifts(self) -> None:
        """Fetch and populate the DataTable of shifts from the REST backend."""
        table = self.query_one("#shift_table", DataTable)
        table.clear()

        # Day hours totals mapping
        day_hours = {
            d: 0.0
            for d in [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
        }

        response = await self.client.request("GET", "/shifts")
        if response.status_code == 200:
            shifts = response.json()

            # Sort shifts by day of the week, then by start time
            DAY_ORDER = {
                "monday": 1,
                "tuesday": 2,
                "wednesday": 3,
                "thursday": 4,
                "friday": 5,
                "saturday": 6,
                "sunday": 7,
            }

            def get_shift_sort_key(s):
                day_name = s.get("day", "").lower()
                day_num = DAY_ORDER.get(day_name, 99)
                start_time = s.get("start_time", "")
                return (day_num, start_time)

            shifts.sort(key=get_shift_sort_key)

            for shift in shifts:
                emp_id = shift.get("employee_id")
                emp_name = (
                    self._employees_cache.get(emp_id, f"Employee #{emp_id}")
                    if emp_id is not None
                    else "N/A"
                )
                start = shift.get("start_time", "")
                end = shift.get("end_time", "")
                day = shift.get("day", "").lower()

                duration = 0.0
                duration_str = "N/A"
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
                        duration_str = f"{duration:.1f}h"
                except Exception:
                    pass

                if day in day_hours:
                    day_hours[day] += duration

                table.add_row(
                    str(shift.get("id", "")),
                    emp_name,
                    shift.get("day", ""),
                    start,
                    end,
                    duration_str,
                    key=str(shift.get("id", "")),
                )

            # Update coverage summary panel
            DAILY_REQUIREMENT = {
                "monday": 32.0,
                "tuesday": 32.0,
                "wednesday": 32.0,
                "thursday": 32.0,
                "friday": 32.0,
                "saturday": 16.0,
                "sunday": 16.0,
            }

            lines = []
            for d in [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]:
                curr = day_hours[d]
                req = DAILY_REQUIREMENT[d]
                pct = int((curr / req) * 100) if req > 0 else 0
                if curr >= req:
                    style = "bold green"
                elif curr > 0:
                    style = "bold yellow"
                else:
                    style = "dim"
                lines.append(
                    f"[{style}]{d.capitalize()}: {curr:.1f}/{req:.0f}h ({pct}%)[/{style}]"
                )

            summary_markup = "\n".join(lines)
            self.query_one("#lbl_shift_summary", Static).update(summary_markup)
        else:
            self.query_one("#shift_form_error", Label).update("Failed to fetch shifts")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "btn_shift_refresh":
            await self.refresh_all()
        elif button_id == "btn_shift_clear":
            self.clear_form()
        elif button_id == "btn_shift_delete":
            await self.delete_selected()
        elif button_id == "btn_shift_edit":
            self.edit_selected()
        elif button_id == "btn_shift_save":
            await self.save_shift()

    def clear_form(self) -> None:
        """Reset input fields to default state."""
        self.editing_id = None
        self.query_one("#shift_form_title", Static).update("Add New Shift")
        self.query_one("#sel_shift_employee", Select).clear()
        self.query_one("#inp_shift_day", Input).value = ""
        self.query_one("#inp_shift_start", Input).value = ""
        self.query_one("#inp_shift_end", Input).value = ""
        self.query_one("#shift_form_error", Label).update("")

    def edit_selected(self) -> None:
        """Load selected row values into inputs to initiate edit mode."""
        table = self.query_one("#shift_table", DataTable)
        cell_key = table.coordinate_to_cell_key(table.cursor_coordinate)
        if not cell_key:
            self.query_one("#shift_form_error", Label).update("No shift selected")
            return

        row_key = cell_key.row_key.value
        if not row_key:
            return

        row = table.get_row(row_key)
        self.editing_id = int(row[0])

        emp_display = row[1]
        emp_id = None
        for eid, ename in self._employees_cache.items():
            if ename == emp_display or f"Employee #{eid}" == emp_display:
                emp_id = eid
                break

        self.query_one("#shift_form_title", Static).update(
            f"Edit Shift #{self.editing_id}"
        )
        self.query_one("#sel_shift_employee", Select).value = (
            emp_id if emp_id is not None else Select.NULL
        )
        self.query_one("#inp_shift_day", Input).value = row[2]
        self.query_one("#inp_shift_start", Input).value = row[3]
        self.query_one("#inp_shift_end", Input).value = row[4]
        self.query_one("#shift_form_error", Label).update("")

    async def delete_selected(self) -> None:
        """Delete selected shift via DELETE endpoint."""
        table = self.query_one("#shift_table", DataTable)
        try:
            cell_key = table.coordinate_to_cell_key(table.cursor_coordinate)
            row_key = cell_key.row_key.value
            row = table.get_row(row_key)
            shift_id = int(row[0])
        except Exception:
            self.query_one("#shift_form_error", Label).update("No shift selected")
            return

        response = await self.client.request("DELETE", f"/shifts/{shift_id}")
        if response.status_code == 200:
            await self.refresh_shifts()
            self.clear_form()
        else:
            err = get_error_message(response, "Failed to delete shift")
            self.query_one("#shift_form_error", Label).update(err)

    async def save_shift(self) -> None:
        """Submit shift data via POST or PUT to REST backend."""
        emp_id = self.query_one("#sel_shift_employee", Select).value
        day = self.query_one("#inp_shift_day", Input).value.strip()
        start = self.query_one("#inp_shift_start", Input).value.strip()
        end = self.query_one("#inp_shift_end", Input).value.strip()

        if emp_id is Select.NULL or emp_id is None:
            self.query_one("#shift_form_error", Label).update(
                "Employee must be selected"
            )
            return
        if not day or not start or not end:
            self.query_one("#shift_form_error", Label).update(
                "Day, Start Time, and End Time are required"
            )
            return

        payload = {
            "employee_id": int(emp_id),
            "day": day,
            "start_time": start,
            "end_time": end,
        }

        if self.editing_id is not None:
            response = await self.client.request(
                "PUT", f"/shifts/{self.editing_id}", json_data=payload
            )
        else:
            response = await self.client.request("POST", "/shifts", json_data=payload)

        if response.status_code in (200, 201):
            await self.refresh_shifts()
            self.clear_form()
        else:
            err = get_error_message(response, "Failed to save shift")
            self.query_one("#shift_form_error", Label).update(err)
