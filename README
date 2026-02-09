# Learning ManageNet System

A Django-based learning management / school administration backend that models users, courses, scheduling, assessments, and content delivery. The project is structured as a multi-app Django monolith with a REST API, custom authentication, and PostgreSQL persistence.

## Key Features

- **Custom user system** with roles (student, teacher, supervisor, admin) and profile/verification data.
- **Course management** with semesters, sessions, time slots, and memberships.
- **Content distribution** for course sessions with tracking of member access.
- **Assignments & exams** with file/text question types, student submissions, and scoring.
- **Token-based API authentication** for DRF endpoints.
- **Jalali (Persian) calendar support** for date representations.

## Tech Stack

- **Backend**: Django 4.x, Django REST Framework.
- **Database**: PostgreSQL (default), with SQLite settings commented for local dev.
- **Authentication**: Custom user model + token auth implementation.
- **Utilities**: django-extensions (ERD graphing), django-cors-headers, WhiteNoise for static files, python-dotenv/environs for environment variables, and Jalali date utilities.
- **Infrastructure**: Docker + docker-compose with PostgreSQL and pgAdmin.

## Architecture Overview

This project uses a modular Django app structure:

- **accounts**: Custom `User` model, role logic, verification codes, and auth token subsystem.
- **courses**: Course definitions, memberships (student/teacher/assistant roles), and course sessions.
- **trs**: Scheduling objects (semesters, rooms, time slots).
- **assignments** / **exams**: Assessment models, question types, and member participation.
- **contents**: Course session content distribution and access tracking.
- **teachers** / **students**: Domain-specific profiles and metadata.
- **apis**: REST endpoints wired into the global API namespace.

### Design Patterns & Conventions

- **App-per-domain design**: Each major domain area is encapsulated in its own Django app.
- **Custom user model**: Extends `AbstractBaseUser` and `PermissionsMixin` with a dedicated user manager.
- **Mixins for cross-cutting concerns**: `TimeStampMixin` provides `created_at`, `updated_at`, and soft-delete markers across models.
- **Token authentication**: A custom auth token model and DRF authentication class implement token-based sessions with expiry/refresh behavior.
- **Relational constraints**: `UniqueConstraint` is used to enforce domain rules (e.g., unique course membership, unique assignments per member, unique time slots).

## Project Structure

```
app/
  accounts/      # Users, auth, verification
  apis/          # API routers
  assignments/   # Assignment models & participation
  contents/      # Course content & access logging
  core/          # Shared utilities (e.g., DB mixins)
  courses/       # Course catalog, sessions, memberships
  django_config/ # Settings, URLs, WSGI
  exams/         # Exam models & participation
  students/      # Student profiles & financial aids
  teachers/      # Teacher profiles & publications
  trs/           # Scheduling (semesters, rooms, time slots)
```

## API & Documentation

The API is exposed under `/apis/` and is wired to Django REST Framework. An OpenAPI schema endpoint is available at `/openapi`, and a ReDoc UI is served at `/redoc/` for API exploration.

## Configuration

Environment variables are loaded via `environs`:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`

Database configuration defaults to PostgreSQL in `django_config/settings.py`. Adjust these values or provide a different database configuration as needed.

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (if running outside Docker)

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file at the repository root with the required settings:

```env
DJANGO_SECRET_KEY=changeme
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

Run migrations and start the server:

```bash
cd app
python manage.py migrate
python manage.py runserver
```

## Docker Usage

This project includes a Docker setup with PostgreSQL and pgAdmin:

```bash
docker compose up --build
```

- API server is exposed on **http://localhost:80**
- PostgreSQL is exposed on **localhost:8080**
- pgAdmin is available at **http://localhost:5050**

## Database ERD

The `app/docs/db` directory contains scripts and instructions for generating ERD diagrams using `django-extensions`.

## Testing & Quality

- Development dependency: `flake8`.
- No dedicated test suite is defined in the repository yet.

## License

No license file is present; treat the code as proprietary until a license is added.
