# Kazlat LIMS Backend

Backend API server for the Kazlat Laboratory Information Management System.

## Overview

This backend provides RESTful API endpoints for managing laboratory operations, including:

- Job and sample management
- User authentication and authorization
- Worksheet and analysis tracking
- Document generation (invoices, COAs)
- Client management

## Tech Stack

_DJANGO X SQL- backend implementation pending_

## Getting Started

_Test Phasing and Current Testing and Documentation Writing_

1. System Info. ✓
2. Users. ✓
3. Clients. ✓
4. Jobs
5. Samples
6. Invoice
7. Invoice Item
8. COA
9. Test Template
10. Template Parameter
11. WorkSheet
12. Test Parameter

## API Endpoints

_Endpoints will be documented here once implemented_

## Development

1. Cloning the Repository: `git clone <url>`
2. Creating Virtual Environment: `python3 -m venv .venv`
3. Activating the virtual environment: `source .venv\activate\bat`
4. Installing the Virtual environmetn: `pip install < requirements.txt`
5. Make migrations:`python manage.py makemigrations`
6. Migrate: `python manage.py migrate`
7. Start the APP: `python manage.py runserver`

## Contribution

- Create your new Model or Edit Existing Model inside lims/models.py
- Make migrations and Create your Serializer
- Create your view inside views folder
- Create your url inside urls
- Link it inside lims/url.py
- Then you are good to go

The Environment Variable:
```
DJANGO_SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=
```

