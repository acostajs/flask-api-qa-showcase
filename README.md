# Vanier Pozole – Employee Shift API

Vanier College study project for **Web Development Environment 2**.

Vanier Pozole is a RESTful API built with **Flask** to manage restaurant employees and their work shifts. The project focuses on backend API design, data modeling, and clean JSON-based communication rather than front-end development.

The API allows creating, reading, updating, and deleting employees and shifts, using a lightweight SQLite database for persistence.

---

## Features

- CRUD operations for employees (name, role, availability)
- CRUD operations for shifts (start time, end time, day, employee assignment)
- REST-style JSON API
- SQLite database for persistent storage
- Marshmallow schemas for model serialization
- Simple, clear project structure for academic purposes

---

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy  
- **Serialization:** Marshmallow, marshmallow-sqlalchemy  
- **Database:** SQLite  
- **Environment & Packaging:** uv  
- **Testing:** curl, Postman, or any HTTP client  

---

## Project Structure

```text
.
├── main.py               # Entry point (uv run main.py)
├── pyproject.toml        # uv dependencies
├── backend/
│   ├── app.py            # Flask routes and API logic
│   ├── database.py       # Shared SQLAlchemy instance
│   ├── schemas.py        # Marshmallow schemas
│   └── models/
│       └── models.py     # Employee and Shift models
└── instance/
    └── site.db           # SQLite database (gitignored)
````

---

## Setup & Run

### 1. Clone the repository

```bash
git clone <repo>
cd vanier-pozole
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Run the server

```bash
uv run main.py
```

The server will start at:

```
http://127.0.0.1:5000
```

---

## API Endpoints

### Employees

```
GET    /employees            # List all employees
POST   /employees            # Create employee
GET    /employees/<id>       # Get employee by ID
PUT    /employees/<id>       # Update employee
DELETE /employees/<id>       # Delete employee
```

Example request body:

```json
{
  "name": "Juan",
  "role": "Cook",
  "availability": "Mon-Fri"
}
```

---

### Shifts

```
GET    /shifts               # List all shifts
POST   /shifts               # Create shift
GET    /shifts/<id>          # Get shift by ID
PUT    /shifts/<id>          # Update shift
DELETE /shifts/<id>          # Delete shift
```

Example request body:

```json
{
  "start_time": "09:00",
  "end_time": "17:00",
  "day": "Monday",
  "employee_id": 1
}
```

---

## Testing with curl

Create an employee:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Juan", "role": "Backend", "availability": "Full-time"}' \
  http://127.0.0.1:5000/employees
```

List employees:

```bash
curl http://127.0.0.1:5000/employees
```

---

## Notes

* This project is backend-only and does not include a front-end UI
* The focus is on API structure, data modeling, and request handling
* Designed to be simple, readable, and easy to explain during evaluation

---

## Academic Disclaimer

This project was developed for academic purposes as part of a Vanier College course. It is intended to demonstrate understanding of REST APIs, Flask, and database-backed applications.
