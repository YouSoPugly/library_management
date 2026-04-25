# University Library System

## Overview

This project implements a University Library Management System using a relational database and a RESTful API. The system models a multi-university environment with multiple campuses, libraries, and users, while supporting core library operations such as item management, checkouts, holds, fines, and room reservations.

The system is built using:

- MySQL for the database
- FastAPI for the backend API
- SQLAlchemy for database interaction
- Jupyter Notebook for testing and demonstration
- Docker Compose for containerized deployment

---

## Team

- Daniel P
- Dylan P
- Thomas P
- Gentry R
- Chris R

Group 10

---

## Running the Project

### 1. Clone the Repository

``` bash
git clone <your-repo-url>
cd <your-project-folder>
```

---

### 2. Configure Environment Variables

Copy the template file:

```bash
cp .env.example .env
```

Update values as needed (e.g., passwords, ports).

---

### 3. Start the Services

``` bash
docker compose up --build -d
```

---

### 4. Stop the Services

``` bash
docker compose down
```

To completely reset the database:

```bash
docker compose down -v
```

---

## Services

| Service  | Description              | Port |
|----------|--------------------------|------|
| MySQL    | Database                 | 3306 |
| API      | FastAPI backend          | 8000 |
| Jupyter  | Notebook environment     | 8888 |

---

## API Service

The backend API is implemented using FastAPI and provides RESTful endpoints for interacting with the system.

- Base URL (host machine): http://localhost:8000
- Base URL (inside Docker network): http://api:8000

---

## Authentication

The API is protected using password-based authentication.

- Staff users must register before accessing protected endpoints
- Passwords are securely hashed using bcrypt

---

## Registering a User

A new user can be created using the /auth/register endpoint.

### Example HTTP Request

```http
POST /auth/register HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "first_name": "Dylan",
  "last_name": "Priebe",
  "email": "dylan@library.edu",
  "password": "supersecret123",
  "library_id": 1
}
```

### Requirements

- The library_id must exist in the LIBRARY table  
- The email field must be unique  

---

## API Demonstration

A complete demonstration of the API is provided in the Jupyter notebook:

```text
proj3-apiDemo.ipynb
```

This notebook includes:

- User registration
- Example API requests
- End-to-end interaction with the backend

Jupyter can be accessed at:

```text
http://localhost:8888
```

---

## Database Schema

The database schema includes the following entities:

### Core Structure
- UNIVERSITY
- LOCATION
- LIBRARY

### Users
- PATRON
- STUDENT
- FACULTY
- STAFF

### Access Control
- ROLE
- PERMISSION
- STAFF_ROLE
- ROLE_PERMISSION

### Library Items
- ITEM_TITLE
- ITEM_COPY
- AUTHOR
- ITEM_AUTHOR

### Transactions
- CHECKOUT
- HOLD
- INTER_LIBRARY_LOAN
- FINE

### Facilities
- ROOM
- ROOM_RESERVATION

---

## Development Notes

- Schema initialization scripts are located in:
```text
 ./mysql/init/
```

- These scripts are executed only when the MySQL container is initialized for the first time

- To reapply schema changes:

```bash
docker compose down -v
docker compose up --build
```

---

## Common Issues

### Database Changes Not Applying

```bash
docker compose down -v
docker compose up --build
```

---

### API Cannot Connect to Database

Ensure:
- MYSQL_HOST=mysql (not localhost)
- All containers are running

---

### API Requests from Jupyter Fail

Use:

```text
http://api:8000
```

Do not use:

```text
http://localhost:8000
```

---

### Authentication Errors

Ensure compatible versions of bcrypt and passlib are installed. Rebuild containers after updating dependencies.

---

## Technology Stack

- FastAPI
- SQLAlchemy
- MySQL 8
- Docker and Docker Compose
- Jupyter Notebook
- Passlib (bcrypt)
- python-jose
