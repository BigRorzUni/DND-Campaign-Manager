# DnD Campaign Manager API

## Overview
The **DnD Campaign Manager API** is a RESTful web service designed to help a Dungeon Master (DM) manage campaigns, record gameplay events, and analyse how encounters play out over time.

The system records detailed **combat and gameplay events** during encounters and uses this data to produce analytics such as damage statistics, healing totals, and spell usage across a campaign.

The API also supports **simulated encounters**, allowing encounters to be automatically resolved using the combat rules implemented in the service. Simulated encounters generate event logs in the same format as manual gameplay.

The service is implemented using **FastAPI**, **SQLAlchemy**, and **SQLite**, following a layered architecture that separates routes, services, repositories, schemas, and database models.

---

## Running the API

### Live Deployment
Live demo accessible at:
```bash
https://dnd-campaign-manager-production.up.railway.app
```

### Running with Docker
Build the image:

```bash
docker build -t dnd-campaign-manager .
```

Seed the database:

```bash
docker run --rm \
  --env-file .env \
  dnd-campaign-manager \
  python reset_and_seed_db.py
```

Start the application:

```bash
docker run -d \
  --name dnd-campaign-manager-app \
  -p 8000:8000 \
  --env-file .env \
  dnd-campaign-manager
```

Open the app at:

```text
http://127.0.0.1:8000
```
### Running Locally
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

Create  .env file:
```bash
DATABASE_URL=sqlite:///./dev.db
OPENAI_API_KEY=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
OPENAI_MODEL=gpt-4o-mini
AI_REVIEW_ENABLED=true
```
Initialise database (if you want a demo campaign)
```
python reset_and_seed_db.py
```

Access the app at:

```
http://127.0.0.1:8000
```

Swagger documentation:

```
http://127.0.0.1:8000/docs
```

ReDoc documentation:

```
http://127.0.0.1:8000/redoc
```

---

## Architecture

The API models a hierarchical structure representing a DnD campaign:

Campaign → Session → Encounter → Event

- **Campaign**: a long-running DnD story managed by a Dungeon Master.
- **Session**: an individual play session within a campaign.
- **Encounter**: a combat or interaction occurring during a session.
- **Event**: an atomic gameplay action such as damage, healing, or spell use.

Events form the **core dataset used for campaign analytics**.

---

## Core Entities

### Characters
Characters represent player characters or NPCs belonging to a campaign.

Characters track:

- class
- level
- hit points
- armour class
- spell slots
- known spells
- equipped equipment

### Participants
Participants represent characters or enemies within a specific encounter.

Participants may be:

- party members (linked to characters)
- enemies imported from monster data
- custom entities

Participants maintain **combat state**, including hit points and spell slots.

### Events
Events record actions that occur during encounters.

Examples include:

- damage dealt
- healing
- spell usage
- ability actions

Events are used to generate campaign analytics and encounter summaries.

---

## Features

### Core API
- Campaign CRUD operations
- Session management
- Encounter management
- Participant management
- Event logging

### Encounter Simulation
Encounters can be simulated automatically.

Simulated encounters:

- randomise initiative order
- generate combat events automatically
- track damage, healing, and spell usage
- determine encounter outcomes

Simulated encounters generate events but **do not contribute to campaign-wide analytics** as those are for the DM to keep track of
their in-person sessions.

### Character System
Characters can:

- learn spells
- equip items
- track spell slots
- track hit points and armour class

Spells and equipment reference external datasets while storing snapshots to ensure historical consistency.

### Dataset Integration
The API integrates with external DnD datasets for:

- spells
- equipment
- monsters
- classes

These endpoints allow searching and importing official DnD content into encounters.

---

## Analytics

Analytics endpoints aggregate gameplay data across campaigns.

Supported analytics include:

### Damage Leaderboard
Ranks participants by total damage dealt.

```
GET /api/v1/analytics/campaigns/{campaign_id}/damage-leaderboard
```

### Damage Taken
Shows how much damage each character has received.

```
GET /api/v1/analytics/campaigns/{campaign_id}/damage-taken
```

### Healing Received
Aggregates healing received by each character.

```
GET /api/v1/analytics/campaigns/{campaign_id}/healing-received
```

### Spell Usage
Tracks spell slot consumption across encounters.

```
GET /api/v1/analytics/campaigns/{campaign_id}/spell-usage
```

### Time Played
Calculates total playtime across campaign sessions.

```
GET /api/v1/analytics/campaigns/{campaign_id}/time-played
```

---

## AI Encounter Review

The API includes an endpoint that analyses encounter results and compares them with the intended difficulty.

The analysis considers:

- damage taken by the party
- healing used
- spell slot consumption
- characters reduced to zero hit points

The endpoint returns advice to help the DM balance future encounters.

---

## Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest

---

## Project Structure

```
app/
 ├── api/            # FastAPI route definitions
 ├── models/         # SQLAlchemy models
 ├── schemas/        # Pydantic schemas
 ├── repositories/   # Data access layer
 ├── services/       # Business logic
 ├── db/             # Database configuration
 └── main.py         # Application entry point
```

This layered structure separates:

- routing
- data persistence
- business logic

which improves maintainability and testability.

---

## Running Tests

Run the automated test suite:

```bash
pytest
```

or for concise output:

```bash
pytest -q
```

Tests cover:

- campaign CRUD operations
- session management
- encounter lifecycle
- participant management
- event logging
- analytics endpoints

---

## API Documentation

The full API documentation is available at:

```
docs/redoc.pdf
```

This document contains the OpenAPI specification exported from the FastAPI application.

---

## Example Workflow

Typical API usage:

1. Create a campaign  
2. Create a session  
3. Create an encounter  
4. Add participants  
5. Log events or simulate the encounter  
6. Retrieve campaign analytics  

Example analytics endpoint:

```
GET /api/v1/analytics/campaigns/{campaign_id}/damage-leaderboard
```

---

## Future Improvements

Potential extensions include:

- user authentication for multiple DMs
- persistent character registries across campaigns
- improved encounter simulation models
- web-based frontend interface
- deployment using Docker or cloud infrastructure