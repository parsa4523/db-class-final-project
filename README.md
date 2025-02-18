# Advanced Database Final Project

This is the final project for the Advanced Database course. The project implements a web application with a FastAPI backend and Streamlit frontend for managing apps, developers, and categories with comprehensive database functionality.

## Tech Stack

- Backend: FastAPI
- Frontend: Streamlit
- Database: PostgreSQL
- ORM: SQLAlchemy
- Migrations: Alembic
- Package Manager: uv
- Containerization: Docker & Docker Compose

## Prerequisites

- Python 3.x
- Docker and Docker Compose
- Git

## Installation & Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install uv package manager:
```bash
# Using pip
pip install uv

# Or using curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create and activate virtual environment using uv:
```bash
uv venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

4. Install dependencies using uv:
```bash
uv pip install -r requirements.txt
```

## Running the Application

1. Start the PostgreSQL database using Docker:
```bash
docker-compose up -d
```

2. Run database migrations:
```bash
alembic upgrade head
```

3. Start the application using the provided script:
```bash
chmod +x start.sh  # Make the script executable (Unix/macOS only)
./start.sh
```

This will:
- Ensure the database is running
- Start the FastAPI backend on http://localhost:8000
- Launch the Streamlit frontend

## Accessing the Application

- Frontend UI: http://localhost:8501
- API Documentation: http://localhost:8000/docs
- Alternative API Documentation: http://localhost:8000/redoc

## Project Structure

```
.
├── alembic/            # Database migration files
├── app/                # Backend application
│   ├── api/           # API routes
│   ├── models/        # SQLAlchemy models
│   └── schemas/       # Pydantic schemas
├── frontend/          # Streamlit frontend application
└── data/             # Sample data and data import scripts
```

## Features

- RESTful API with FastAPI
- Interactive frontend with Streamlit
- PostgreSQL database with SQLAlchemy ORM
- Database migrations with Alembic
- Docker containerization
- Sample data import functionality
- API documentation with Swagger UI and ReDoc
