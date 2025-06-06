# CRM Microservice

A lightweight CRM (Customer Relationship Management) microservice that provides a RESTful API for managing leads, actions, and processes. The service uses SQLite as its database and is containerized using Docker.

## Features

- Lead Management (create, read, update, delete)
  - Mandatory status field with default value "new"
  - Status cannot be set to null
  - URL tracking and filtering
  - Email validation and formatting
  - Duplicate email prevention (case-insensitive)
- Action Tracking (create, read, update, delete)
  - Automatic timestamp tracking
  - Automatic process management
  - Compatible with both 'description' and 'details' fields
- Process Management (read, update, delete)
  - Automatically created and updated based on actions
  - 7-day follow-up window from last action
  - Status tracking and channel management
- RESTful API endpoints
- SQLite database with thread-safe operations
- Docker containerization
- Debug logging for database operations

## API Endpoints

### Leads

- `POST /leads/` - Create a new lead
  - Status defaults to "new" if not provided
  - Status cannot be null
  - Email must be valid and will be converted to lowercase
  - Duplicate emails (case-insensitive) are not allowed
- `GET /leads/{lead_id}` - Get lead details
- `PUT /leads/{lead_id}` - Update lead information
  - Status cannot be set to null
  - Email must be valid and will be converted to lowercase
  - Cannot update to an email that already exists (case-insensitive)
- `DELETE /leads/{lead_id}` - Delete a lead
- `GET /leads/` - Search leads (optional filters: status, url)

### Actions

- `POST /actions/` - Create a new action
  - Automatically sets timestamp if not provided
  - Creates or updates associated process
  - Sets next follow-up to 7 days after action
  - Accepts both 'description' and 'details' fields
- `GET /actions/{action_id}` - Get action details
- `GET /actions/` - Search actions (optional filter: action_type)

### Processes

- `GET /processes/{process_id}` - Get process details
- `GET /processes/` - Search processes (optional filter: status)
- `POST /processes/` - Create a new process (only available in test environment via create_app_with_db())

## Database Schema

### Leads Table
```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    url TEXT
)
```

### Actions Table
```sql
CREATE TABLE actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    action_type TEXT,
    details TEXT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
)
```

### Processes Table
```sql
CREATE TABLE processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    lead_id INTEGER,
    channel TEXT,
    last_action_id INTEGER,
    next_followup_datetime TEXT,
    status TEXT
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
    "status": "new"  // Optional, defaults to "new"
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
    "status": "contacted"  // Cannot be null
}
```

#### Delete Lead
```http
DELETE /leads/{lead_id}
```

#### Search Leads
```http
GET /leads/?status=new&url=https://example.com
```

### Action Management

#### Create Action
```http
POST /actions
Content-Type: application/json

{
    "lead_id": 1,
    "action_type": "email",
    "details": "Sent welcome email",  // Can also use "description" field
    "timestamp": "2024-03-20 10:00:00"  // Optional, defaults to current time
}
```

#### Get Action
```http
GET /actions/{action_id}
```

#### Search Actions
```http
GET /actions/?action_type=email
```

### Process Management

#### Get Process
```http
GET /processes/{process_id}
```

#### Search Processes
```http
GET /processes/?status=active
```

## API Response Formats

### Lead Responses

#### Single Lead Response
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",  // Always stored in lowercase
    "status": "new",
    "url": "https://example.com"
}
```

#### Lead List Response
```json
[
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "status": "new",
        "url": "https://example.com"
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
    "description": "Sent welcome email",  // For backward compatibility
    "timestamp": "2024-03-20 10:00:00"
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
        "description": "Sent welcome email",  // For backward compatibility
        "timestamp": "2024-03-20 10:00:00"
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
    "next_followup_datetime": "2024-03-27 10:00:00",
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
        "next_followup_datetime": "2024-03-27 10:00:00",
        "status": "active"
    }
]
```

### Error Response
```json
{
    "detail": "Lead status cannot be None"
}
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request (e.g., invalid status value, duplicate email)
- 404: Not Found
- 422: Unprocessable Entity (e.g., invalid email format)
- 500: Internal Server Error

Error responses include a JSON object with a `detail` field containing the error message. Common error messages include:

- "Lead status cannot be None"
- "A lead with this email already exists"
- "Invalid email format"

## Automatic Process Management

The system automatically manages processes based on actions:

1. When a new action is created:
   - If no process exists for the lead, a new process is created
   - If a process exists, it is updated with the new action details
   - The next follow-up datetime is set to 7 days after the action's timestamp
   - The process channel is updated to match the action type

2. Process updates include:
   - Last action ID
   - Channel (based on action type)
   - Next follow-up datetime
   - Status tracking

## Database Connection

- Thread-safe SQLite operations
- Automatic connection management
- Debug logging for database operations
- Connection pooling for concurrent requests
