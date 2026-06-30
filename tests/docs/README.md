# Test Suite Documentation

This folder contains the automated test suite for the **Pozole Employee Shift API**.

The goal of this project is to demonstrate a complete testing strategy for a production-style Flask REST API. The test suite covers everything from isolated unit tests to full integration workflows and performance testing.

---

# Test Types

The project includes several types of automated tests.

| Folder               | Purpose                                                                                                                         |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `tests/unit/`        | Tests for API endpoints, validation rules, and request/response behavior.                                                       |
| `tests/integration/` | Tests that verify multiple parts of the system work together, including database constraints and full employee-shift workflows. |
| `tests/smoke/`       | Fast health checks that confirm the API is running and responding correctly.                                                    |
| `tests/performance/` | Load testing with Locust to measure API performance under concurrent traffic.                                                   |

---

# Tools Used

* pytest
* Requests
* Locust
* Coverage.py
* Ruff
* GitHub Actions
* Lefthook

---

# Getting Started

## Requirements

* Python 3.13+
* Astral uv

Install the project dependencies:

```
uv sync
```

Install Git hooks:

```
uv run lefthook install
```

---

# Running Tests

Run the complete test suite:

```
uv run pytest
```

Run tests with a coverage report:

```
uv run task cov
```

Generate an HTML coverage report:

```
uv run task coverage-report
```

Run only the smoke tests:

```
uv run pytest tests/smoke/
```

---

# Test Coverage

The project currently has **99% test coverage** across the API backend.

| Module              | Coverage |
| ------------------- | -------- |
| backend/app.py      | 100%     |
| backend/database.py | 100%     |
| backend/schemas.py  | 100%     |
| backend/models      | 89%      |
| **Total**           | **99%**  |

---

# Performance Testing

Performance testing is done with **Locust** to simulate multiple users interacting with the API, including listing employees, listing shifts, creating employees, and running full lifecycle operations.

Start the interactive Locust dashboard:

```
uv run task perf
```

Run the headless performance test:

```
uv run task perf-report
```

The included benchmark produced the following results:

| Metric                | Result    |
| --------------------- | --------- |
| Average response time | **4 ms**  |
| Median response time  | **4 ms**  |
| Minimum response time | **1 ms**  |
| Maximum response time | **12 ms** |
| Failure rate          | **0.00%** |
| Total requests        | **80**    |

These results show that the API remains fast and stable under concurrent load.
