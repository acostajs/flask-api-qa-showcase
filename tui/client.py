import httpx
from typing import Any, Callable, Coroutine, Optional


class APIClient:
    """Asynchronous API client wrapper for communicating with the Pozole REST backend."""

    def __init__(self, base_url: str = "http://127.0.0.1:5000") -> None:
        self.base_url: str = base_url
        self.log_callback: Optional[
            Callable[
                [str, str, int, Optional[Any], Optional[Any]],
                Coroutine[Any, Any, None],
            ]
        ] = None

    async def request(
        self, method: str, path: str, json_data: Optional[Any] = None
    ) -> httpx.Response:
        """Send an HTTP request to the API backend asynchronously and log the transaction."""
        url: str = f"{self.base_url}{path}"
        async with httpx.AsyncClient() as client:
            try:
                if json_data is not None:
                    response = await client.request(
                        method, url, json=json_data, timeout=5.0
                    )
                else:
                    response = await client.request(method, url, timeout=5.0)

                resp_json = None
                try:
                    resp_json = response.json()
                except Exception:
                    resp_json = response.text

                if self.log_callback:
                    await self.log_callback(
                        method,
                        url,
                        response.status_code,
                        json_data,
                        resp_json,
                    )
                return response
            except Exception as e:
                if self.log_callback:
                    await self.log_callback(
                        method, url, 500, json_data, {"error": str(e)}
                    )
                return httpx.Response(500, json={"error": str(e)})


def get_error_message(response: httpx.Response, default: str) -> str:
    """Safely extract error message from a response without raising JSONDecodeError."""
    try:
        data = response.json()
        if isinstance(data, dict):
            if "error" in data:
                return str(data["error"])
            if "message" in data:
                return str(data["message"])
    except Exception:
        pass
    return f"{default} (HTTP {response.status_code})"
