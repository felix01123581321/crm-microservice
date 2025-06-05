# CRM Microservice

A lightweight CRM (Customer Relationship Management) microservice that provides a RESTful API for managing leads, actions, and processes. The service uses SQLite as its database and is containerized using Docker.

## Features

- Lead Management (create, read, update, delete)
- Action Tracking (create, read, update, delete)
- Process Management (create, read, update, delete)
- RESTful API endpoints
- SQLite database with thread-safe operations
- Docker containerization

## API Endpoints

### Leads

- `POST /leads` - Create a new lead
- `GET /leads/{lead_id}` - Get lead details
- `PUT /leads/{lead_id}` - Update lead information
- `DELETE /leads/{lead_id}` - Delete a lead

### Actions

- `POST /actions` - Create a new action
- `GET /actions/{action_id}` - Get action details
- `PUT /actions/{action_id}` - Update action information
- `DELETE /actions/{action_id}` - Delete an action

### Processes

- `POST /processes` - Create a new process
- `GET /processes/{process_id}` - Get process details
- `PUT /processes/{process_id}` - Update process information
- `DELETE /processes/{process_id}` - Delete a process

## Database Schema

### Leads Table
```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    name TEXT,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Actions Table
```sql
CREATE TABLE actions (
    id INTEGER PRIMARY KEY,
    lead_id INTEGER,
    action_type TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
)
```

### Processes Table
```sql
CREATE TABLE processes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Setup and Installation

### Prerequisites

- Docker
- Docker Compose

### Running with Docker Compose

1. Build and start the service:
```bash
docker-compose up --build
```

2. The service will be available at `http://localhost:8000`

### Environment Variables

The following environment variables can be configured:

- `DATABASE_URL`: SQLite database file path (default: `crm.db`)
- `HOST`: API host address (default: `0.0.0.0`)
- `PORT`: API port number (default: `8000`)

## Development

### Project Structure

```
src/crm/
├── __init__.py
├── api.py          # FastAPI routes and endpoints
├── crm.py          # CRM business logic
├── database.py     # Database operations
├── Dockerfile      # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
└── README.md       # This file
```

## API Documentation

### Lead Management

#### Create Lead
```http
POST /leads
Content-Type: application/json

{
    "email": "john@example.com",
    "name": "John Doe",
    "status": "new"
}
```

#### Get Lead
```http
GET /leads/{lead_id}
```

#### Update Lead
```http
PUT /leads/{lead_id}
Content-Type: application/json

{
    "name": "John Updated",
    "status": "contacted"
}
```

#### Delete Lead
```http
DELETE /leads/{lead_id}
```

### Action Management

#### Create Action
```http
POST /actions
Content-Type: application/json

{
    "lead_id": 1,
    "action_type": "email",
    "details": "Sent welcome email"
}
```

#### Get Action
```http
GET /actions/{action_id}
```

#### Update Action
```http
PUT /actions/{action_id}
Content-Type: application/json

{
    "details": "Updated action details"
}
```

#### Delete Action
```http
DELETE /actions/{action_id}
```

### Process Management

#### Create Process
```http
POST /processes
Content-Type: application/json

{
    "name": "Lead Nurturing",
    "status": "active"
}
```

#### Get Process
```http
GET /processes/{process_id}
```

#### Update Process
```http
PUT /processes/{process_id}
Content-Type: application/json

{
    "status": "completed"
}
```

#### Delete Process
```http
DELETE /processes/{process_id}
```

## API Response Formats

### Lead Responses

#### Single Lead Response
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "status": "new"
}
```

#### Lead List Response
```json
[
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "status": "new"
    },
    {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane@example.com",
        "status": "contacted"
    }
]
```

### Action Responses

#### Single Action Response
```json
{
    "id": 1,
    "lead_id": 1,
    "action_type": "email",
    "details": "Sent welcome email",
    "description": "Sent welcome email"  // For backward compatibility
}
```

#### Action List Response
```json
[
    {
        "id": 1,
        "lead_id": 1,
        "action_type": "email",
        "details": "Sent welcome email",
        "description": "Sent welcome email"
    },
    {
        "id": 2,
        "lead_id": 1,
        "action_type": "follow-up",
        "details": "Sent follow-up email",
        "description": "Sent follow-up email"
    }
]
```

### Process Responses

#### Single Process Response
```json
{
    "id": 1,
    "name": "Lead Nurturing",
    "lead_id": 1,
    "channel": "email",
    "last_action_id": 1,
    "next_followup_datetime": "2024-03-20 10:00:00",
    "status": "active"
}
```

#### Process List Response
```json
[
    {
        "id": 1,
        "name": "Lead Nurturing",
        "lead_id": 1,
        "channel": "email",
        "last_action_id": 1,
        "next_followup_datetime": "2024-03-20 10:00:00",
        "status": "active"
    },
    {
        "id": 2,
        "name": "Follow-up Process",
        "lead_id": 2,
        "channel": "phone",
        "last_action_id": 2,
        "next_followup_datetime": "2024-03-21 14:00:00",
        "status": "pending"
    }
]
```

### Error Response
```json
{
    "error": "Lead not found"
}
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

Error responses include a JSON object with an `error` field containing the error message.
