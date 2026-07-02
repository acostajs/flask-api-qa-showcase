import argparse
import logging
import socket
import threading
import sys
from backend.app import app
from tui.app import PozoleTUIApp
from tui.client import APIClient


def is_port_in_use(host: str, port: int) -> bool:
    """Check if a specific host and port is already bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def check_if_our_server(host: str, port: int) -> bool:
    """Verify if the service running on the port is our Flask server."""
    try:
        import httpx

        # Send a quick GET request to check if it returns a list of employees
        resp = httpx.get(f"http://{host}:{port}/employees", timeout=1.0)
        if resp.status_code == 200 and isinstance(resp.json(), list):
            return True
    except Exception:
        pass
    return False


def run_backend_server(port: int) -> None:
    """Run Flask server in a quiet mode suited for threading."""
    # Suppress console logs to avoid corrupting the terminal UI
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def main() -> None:
    """Application entry point parsing arguments and starting either API or TUI."""
    parser = argparse.ArgumentParser(
        description="Pozole REST API and Terminal User Interface Console"
    )
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Run only the Flask API server in the foreground.",
    )
    args = parser.parse_args()

    if args.api_only or "--api-only" in sys.argv:
        # Standalone foreground server mode
        print("Starting Pozole REST API Server on http://127.0.0.1:5000...")
        app.run(host="127.0.0.1", port=5000, debug=True)
    else:
        port = 5000
        backend_running = is_port_in_use("127.0.0.1", 5000)

        if backend_running:
            if check_if_our_server("127.0.0.1", 5000):
                # Our server is already running, TUI can just connect to it
                pass
            else:
                # Port 5000 is occupied by a foreign service (e.g. AirPlay), scan for next free port
                port = 5001
                while is_port_in_use("127.0.0.1", port):
                    port += 1

        if not backend_running or port != 5000:
            # Start backend in a background daemon thread
            server_thread = threading.Thread(
                target=run_backend_server, args=(port,), daemon=True
            )
            server_thread.start()

        # Run TUI application
        client = APIClient(base_url=f"http://127.0.0.1:{port}")
        tui_app = PozoleTUIApp(client=client)
        tui_app.run()


if __name__ == "__main__":
    main()
