# Pozole | Flask REST API QA Showcase

[![Coverage Status](https://coveralls.io/repos/github/acostajs/vanier-pozole/badge.svg?branch=main)](https://coveralls.io/github/acostajs/vanier-pozole?branch=main)

A REST API built with **Flask** to manage restaurant employees and work shifts.

Although the application provides a complete backend for employee scheduling, the main purpose of this repository is to showcase my **Software QA and Test Automation** skills. The project demonstrates how to test REST APIs using unit, integration, smoke, and performance testing, along with automated quality checks and continuous integration.

---

# What This Project Demonstrates

This repository highlights my experience with:

* Building automated API tests with **pytest**
* Writing **unit, integration, smoke, and performance tests**
* Testing REST endpoints, validation, and database workflows
* Measuring API performance with **Locust**
* Enforcing code quality with **Ruff** and **Git hooks**
* Running automated checks with **GitHub Actions**

---

# Tech Stack

### Backend

* Flask
* Flask-SQLAlchemy
* SQLite
* Marshmallow

### Testing

* pytest
* Requests
* Locust
* pytest-cov

### Code Quality

* Ruff
* Lefthook
* GitHub Actions

### Development

* Astral uv

---

# Project Structure

```text
backend/
    models/
    app.py
    database.py
    schemas.py

tests/
    integration/
    performance/
    smoke/
    unit/
    conftest.py

.github/workflows/
main.py
```

The **tests/** folder contains different types of automated tests:

* **Unit tests** for API endpoints and validation
* **Integration tests** for complete employee and shift workflows
* **Smoke tests** to verify the API is running and responding
* **Performance tests** using Locust to simulate API traffic

---

# Getting Started

## Requirements

* Python
* Astral uv

Install the project dependencies:

```bash
uv sync
```

Install the Git hooks:

```bash
uv run lefthook install
```

Start the development server:

```bash
uv run main.py
```

The API will be available at:

```text
http://127.0.0.1:5000
```

---

# API Endpoints

## Employees

| Method | Endpoint          |
| ------ | ----------------- |
| GET    | `/employees`      |
| POST   | `/employees`      |
| GET    | `/employees/<id>` |
| PUT    | `/employees/<id>` |
| DELETE | `/employees/<id>` |

## Shifts

| Method | Endpoint       |
| ------ | -------------- |
| GET    | `/shifts`      |
| POST   | `/shifts`      |
| GET    | `/shifts/<id>` |
| PUT    | `/shifts/<id>` |
| DELETE | `/shifts/<id>` |

---

# Running Tests

Run the complete test suite:

```bash
uv run pytest
```

Generate a coverage summary:

```bash
uv run task cov
```

Generate an HTML coverage report:

```bash
uv run task coverage-report
```

Run the smoke tests:

```bash
uv run pytest tests/smoke/
```

Run the performance tests:

```bash
uv run task perf
```

Generate a performance report:

```bash
uv run task perf-report
```

---

# Test Coverage

The project currently has **99% test coverage**.

The automated test suite validates:

* REST API endpoints
* Request validation
* CRUD operations
* Database relationships
* Employee and shift workflows
* Error handling
* API availability
* Performance under load

---

# Code Quality

The project uses **Lefthook** to automatically run quality checks before code is committed.

The pre-commit workflow includes:

* Ruff formatting
* Ruff linting
* Automated pytest execution

Run the checks manually:

```bash
uv run ruff format .
uv run ruff check .
```

---

# Continuous Integration

GitHub Actions automatically runs quality checks whenever code is pushed to the repository.

The CI pipeline includes:

* Ruff linting
* Automated test execution
* Continuous validation of the codebase
