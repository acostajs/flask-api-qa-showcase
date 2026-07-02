from typing import Any, Optional
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane
from tui.client import APIClient
from tui.employees_tab import EmployeesTab
from tui.logs_tab import LogsTab
from tui.shifts_tab import ShiftsTab


class PozoleTUIApp(App[None]):
    """Main Textual Application for controlling the Pozole API backend."""

    TITLE = "Pozole Restaurant Manager"
    SUB_TITLE = "REST API Administrative Terminal"

    CSS = """
    Screen {
        background: #0f172a;
    }
    Header {
        background: #1e293b;
        color: #38bdf8;
        text-style: bold;
    }
    Footer {
        background: #1e293b;
        color: #94a3b8;
    }
    TabbedContent {
        margin: 0;
        padding: 0;
    }
    .tab-title {
        text-align: center;
        background: #1e293b;
        color: #38bdf8;
        padding: 1 2;
        margin-bottom: 1;
        text-style: bold;
    }
    .section-title {
        text-align: center;
        background: #334155;
        color: #e2e8f0;
        padding: 0 1;
        margin-bottom: 1;
        text-style: bold;
    }
    #emp_list_pane, #shift_list_pane {
        width: 60%;
        height: 100%;
        border-right: tall #334155;
        padding: 1;
    }
    #emp_form_pane, #shift_form_pane {
        width: 40%;
        height: 100%;
        padding: 1 2;
        overflow-y: auto;
    }
    #emp_table {
        height: 75%;
        border: round #475569;
    }
    #shift_table {
        height: 42%;
        border: round #475569;
    }
    #emp_controls, #shift_controls {
        height: 3;
        margin-top: 1;
        align: center middle;
    }
    #emp_controls Button, #shift_controls Button {
        margin-right: 1;
    }
    #emp_form_buttons, #shift_form_buttons {
        height: 3;
        margin-top: 2;
        align: center middle;
    }
    #emp_form_buttons Button, #shift_form_buttons Button {
        margin-right: 2;
    }
    Input {
        margin-bottom: 1;
        border: round #475569;
        background: #1e293b;
        color: #f8fafc;
    }
    Select {
        margin-bottom: 1;
        border: round #475569;
        background: #1e293b;
        color: #f8fafc;
    }
    Label {
        color: #cbd5e1;
        text-style: bold;
        margin-top: 1;
    }
    .error-label {
        color: #ef4444;
        text-style: italic;
        height: 2;
    }
    #api_log {
        border: round #334155;
        background: #020617;
        padding: 1;
    }
    #emp_avail_container {
        height: 24;
        margin-top: 1;
        border: round #334155;
        padding: 0 1;
    }
    .avail-row {
        height: 3;
        align: left middle;
        margin-bottom: 0;
    }
    .avail-day-label {
        width: 5;
        text-align: right;
        margin-top: 0;
        margin-right: 1;
    }
    .avail-input-start, .avail-input-end {
        width: 10;
        height: 3;
        border: round #475569;
        margin-bottom: 0;
        padding: 0 1;
    }
    .avail-to {
        width: 4;
        text-align: center;
        color: #64748b;
    }
    #shift_summary_container {
        height: 11;
        margin-top: 1;
        border: round #334155;
        padding: 0 1;
        background: #1e293b;
    }
    .summary-title {
        text-align: center;
        background: #475569;
        color: #38bdf8;
        text-style: bold;
        height: 1;
    }
    .summary-markup {
        padding: 0 1;
        margin-top: 1;
        text-align: center;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit Pozole"),
        ("r", "refresh_all_tabs", "Refresh Data"),
    ]

    def __init__(self, client: APIClient, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client: APIClient = client
        self.client.log_callback = self.on_api_log

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="tab_employees"):
            with TabPane("Employees", id="tab_employees"):
                yield EmployeesTab(self.client, id="employees_tab")
            with TabPane("Shifts", id="tab_shifts"):
                yield ShiftsTab(self.client, id="shifts_tab")
            with TabPane("API Logs", id="tab_logs"):
                yield LogsTab(id="logs_tab")
        yield Footer()

    async def on_api_log(
        self,
        method: str,
        url: str,
        status_code: int,
        request_body: Optional[Any] = None,
        response_body: Optional[Any] = None,
    ) -> None:
        """Route logged HTTP transaction parameters to the LogsTab logger widget."""
        try:
            logs_widget = self.query_one("#logs_tab", LogsTab)
            await logs_widget.log_request(
                method, url, status_code, request_body, response_body
            )
        except Exception:
            pass

    async def refresh_shifts_tab_dropdown(self) -> None:
        """Updates the shift creation employee select choices when directory changes."""
        try:
            shifts_widget = self.query_one("#shifts_tab", ShiftsTab)
            await shifts_widget.refresh_employees_list()
        except Exception:
            pass

    async def action_refresh_all_tabs(self) -> None:
        """Triggers data re-fetching across all tabs."""
        try:
            emp_widget = self.query_one("#employees_tab", EmployeesTab)
            await emp_widget.refresh_employees()
        except Exception:
            pass

        try:
            shifts_widget = self.query_one("#shifts_tab", ShiftsTab)
            await shifts_widget.refresh_all()
        except Exception:
            pass
