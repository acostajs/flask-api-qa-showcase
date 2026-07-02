from typing import Any, Optional
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import RichLog, Static


class LogsTab(Container):
    """TUI Pane that displays a real-time console log of API request and response details."""

    def compose(self) -> ComposeResult:
        yield Static("API Requests & Responses Log Console", classes="tab-title")
        yield RichLog(id="api_log", highlight=True, markup=True)

    async def log_request(
        self,
        method: str,
        url: str,
        status_code: int,
        request_body: Optional[Any] = None,
        response_body: Optional[Any] = None,
    ) -> None:
        """Appends a new logged API transaction to the console log widget."""
        log_widget = self.query_one("#api_log", RichLog)

        # Style status codes (green for success, red for errors)
        if 200 <= status_code < 300:
            status_style = "[bold green]"
        else:
            status_style = "[bold red]"

        log_widget.write(f"\n[bold cyan]▶ {method} {url}[/bold cyan]")
        if request_body is not None:
            log_widget.write(f"  [bold]Payload:[/bold] {request_body}")

        log_widget.write(
            f"  [bold]Response:[/bold] {status_style}{status_code}[/{status_style}]"
        )
        if response_body is not None:
            log_widget.write(f"  [bold]Body:[/bold] {response_body}")
