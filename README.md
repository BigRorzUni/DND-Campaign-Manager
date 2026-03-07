# DnD Campaign Manager API

## Overview
The aim of this project is to allow the Dungeon Master (DM) to manage campaigns with the generation detailed event logs and analytics based on gameplay over their sessions. 

It implements a RESTful web service using **FastAPI**, **SQLAlchemy**, and **SQLite**, with a layered architecture that separates routes, repos, models and schemas.

## Architecture

This API follows the architecture of:

Campaign → Session → Encounter → Event

- **Campaign**: a long-running DnD story.
- **Session**: an individual play session within a campaign.
- **Encounter**: a combat or interaction within a session.
- **Event**: an atomic action such as damage, healing, spell use, or character status change.
    - Events are used as the basis for analytics endpoints.

## Features

### Core API
- Campaign CRUD
- Session management
- Encounter management
- Event logging

### Analytics
- Damage leaderboard
- Encounter difficulty summaries
- Event type breakdown

### Testing
Automated tests using **pytest** verify the behaviour of the API and analytics endpoints.

## Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pytest

## Running the API

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Run the server:
```bash
uvicorn app.main:app --reload
```
Access the API at: http://127.0.0.1:8000

Access the swagger documentation at:
http://127.0.0.1:8000/docs

## Running Tests
```bash
pytest
```
or for more concise output
```bash
pytest -q
```

## API Documentation
The full documentation is available at \docs\documentation.pdf

This document contains the OpenAPI specification exported from the FastAPI application.

## Example Workflow

### Example usage of the API:
	1.	Create campaign
	2.	Create session
	3.	Create encounter
	4.	Log events
	5.	Retrieve analytics

### Example analytics endpoint:
```code
GET /api/v1/analytics/campaigns/{campaign_id}/damage-leaderboard
```
## Future Improvements

Potential extensions include:
- campaign character registry
- integration with external spell databases
- authentication for multiple DMs
- deployment using Docker or cloud infrastructure
