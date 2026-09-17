# Lumen Property Registry - Backend

FastAPI backend for the Lumen Property Registry.

The backend provides a REST API and PostgreSQL data layer for managing:

- Units
- Owners
- Locations
- Contacts
- Orders
- Ownership relationships
- Ownership history
- Search
- Dashboard statistics

The system is designed around persistent registry identities rather than treating every source row as a new entity.

---

## 1. Project Overview

The Lumen Property Registry is a property data registry designed to identify,
organize, and track relationships between physical units, owners, locations,
and transaction records.

The central principle is:

    A physical property is a persistent identity independent of source rows.

The backend separates:

    Source observations
            |
            v
    Persistent registry identities
            |
            +---- Unit
            |
            +---- Owner
            |
            +---- Location
            |
            +---- Transaction / Order
            |
            +---- Historical relationships

This allows the system to support:

- Unique Unit identification
- Unique Owner identification
- Unique Location identification
- Owner to Unit relationships
- Unit to Owner relationships
- Ownership history
- Location to Unit relationships
- Search by identifiers and names
- Dashboard statistics
- Idempotent data ingestion

---

## 2. Architecture

The system follows a simple three-layer deployment architecture:

    +-----------------------------+
    |       React Frontend        |
    |          Vercel             |
    +--------------+--------------+
                   |
                   | REST API
                   v
    +-----------------------------+
    |       FastAPI Backend       |
    |           Render            |
    +--------------+--------------+
                   |
                   v
    +-----------------------------+
    |      SQLAlchemy / Alembic   |
    +--------------+--------------+
                   |
                   v
    +-----------------------------+
    |    PostgreSQL / Supabase    |
    +-----------------------------+

The backend is responsible for:

- API routing
- Database access
- Registry identity management
- Ownership relationships
- Ownership history
- Location relationships
- Search
- Dashboard statistics
- Data ingestion
- Database migrations
- Duplicate prevention

---

## 3. Technology Stack

Language:
    Python

Package manager:
    uv

API framework:
    FastAPI

ORM:
    SQLAlchemy 2.x

Data validation and configuration:
    Pydantic

Database:
    PostgreSQL

Database hosting:
    Supabase

Database migrations:
    Alembic

Data ingestion:
    pandas
    openpyxl

Application server:
    Uvicorn

Backend hosting:
    Render

---

## 4. Core Data Model

The main entities are:

    Location
        |
        | 1-to-many
        v
      Unit
        |
        +----------------------+
        |                      |
        |                      |
        v                      v
      Owner                 Order
        |
        |
        v
    Ownership History

The main database tables are:

    locations
    units
    owners
    contacts
    orders
    order_parties
    ownership_history

The system separates permanent identities from relationships and historical
records.

---

## 5. Unit Identity

A Unit represents one physical property.

The source property_id is used as the registry unit_id.

    unit_id     = property_id
    property_id = property_id
    unit_code   = source unit

A Unit is NOT created for every source row.

For example:

    Source Row 1
    Source Row 2
    Source Row 3
          |
          v
      One Unit

This follows the "Units, never rows" principle.

Multiple source observations can therefore refer to the same physical unit
without creating duplicate Unit identities.

---

## 6. Owner Identity

Owners have persistent owner_id values.

The display name is not treated as a sufficient unique identifier.

Owner identity can be supported by attributes such as:

- Name
- Phone
- Email
- Identification information
- Owner type
- Source/community information

The purpose of this approach is to avoid incorrectly merging different
people or organizations simply because their names are similar.

Owner records are persistent identities that can be enriched with additional
information over time.

---

## 7. Location Identity

Locations have their own persistent location_id.

A location can contain multiple registered units.

Example relationship:

    Location
       |
       +---- Unit A
       |
       +---- Unit B
       |
       +---- Unit C

The Location Profile API also exposes the units registered under that
location.

---

## 8. Ownership Relationships

Ownership is represented as a relationship between:

    owner_id <----> unit_id

The relationship is stored in:

    ownership_history

This allows the registry to represent units associated with multiple owners.

Example:

    Unit A
       |
       +---- Owner A
       |
       +---- Owner B
       |
       +---- Owner C

The system does not force a physical unit into a single-owner structure.

---

## 9. Ownership History

Ownership history is stored separately from Unit and Owner entities.

A history record contains:

    history_id
    unit_id
    owner_id
    start_date
    end_date
    source_order_id

The history API allows the frontend to display historical ownership records
for a Unit.

The Owner Profile also exposes the ownership records associated with that
owner.

Dates are not fabricated.

If the source data does not contain reliable ownership dates, the backend
returns null and the frontend displays the period as unavailable.

---

## 10. Duplicate Prevention

The backend prevents duplicate ownership relationships.

The primary relationship is:

    owner_id + unit_id

The database enforces uniqueness for the V1 registry relationship.

This prevents repeated ingestion of the same relationship from creating
duplicate records.

Example:

    First import:
        Owner A + Unit X
        -> relationship created

    Second import:
        Owner A + Unit X
        -> existing relationship detected
        -> no duplicate created

---

## 11. Idempotent Ingestion

The ingestion process is designed to be idempotent.

The general process is:

    Source Row
        |
        v
    Normalize / validate
        |
        v
    Match Unit
        |
        +---- Existing -> reuse Unit ID
        |
        +---- Missing  -> create Unit
        |
        v
    Match Owner
        |
        +---- Existing -> reuse Owner ID
        |
        +---- Missing  -> create Owner
        |
        v
    Validate relationship
        |
        v
    Create ownership record if required

Running the same source data again should not duplicate existing registry
identities or ownership relationships.

---

## 12. Data Ingestion

The registry was populated from the supplied workbook.

Important source sheets include:

    OWNERS
    OWNERS_NEW
    OWNERS_UPDATES
    PROPERTIES
    PROPERTIES_NEW
    CONTACTS
    MULTI_PROPERTY_OWNERS
    DEDUP_LOG_V2
    DATA_DICTIONARY
    COMMUNITY_SUMMARY
    PROP_BLDG_ENRICHED

The important distinction is:

    Source rows = observations

    Registry entities = persistent identities

The ingestion process therefore resolves source observations into persistent
Unit and Owner identities instead of treating every row as a separate entity.

---

## 13. Registry Counts

The current PostgreSQL registry contains approximately:

    Owners:
        381,996

    Units:
        1,377,629

    Locations:
        48,375

    Ownership relationships:
        1,378,572

    Orders:
        0

These are the current database counts after registry ingestion.

The source data contains units associated with multiple owners, and those
relationships are preserved.

---

## 14. Orders

Orders are intentionally not fabricated.

The supplied workbook contains transaction-related information including:

    transaction_date

and:

    TRANSACTIONS_SUMMARY

However, the available data does not provide reliable row-level transaction
or order identity.

Therefore:

    transaction_date is not an order_id

and:

    TRANSACTIONS_SUMMARY is not a transaction-level order dataset

Creating Orders from these fields would create synthetic transaction
identities that are not supported by the source data.

The current system therefore keeps:

    orders = 0

while maintaining the Order database model and API structure.

When a transaction-level dataset containing reliable transaction/order
identifiers becomes available, it can be integrated into the existing
architecture.

---

## 15. API Endpoints

### Health

    GET /health

### Dashboard

    GET /api/dashboard

### Owners

    GET /api/owners
    GET /api/owners/{owner_id}
    GET /api/owners/{owner_id}/units
    GET /api/owners/{owner_id}/history

### Units

    GET /api/units
    GET /api/units/{unit_id}
    GET /api/units/{unit_id}/owners
    GET /api/units/{unit_id}/history

### Locations

    GET /api/locations
    GET /api/locations/{location_id}

The Location detail endpoint returns the units registered under that
location.

### Orders

    GET /api/orders
    GET /api/orders/{order_id}

### History

    GET /api/history

### Search

    GET /api/search

The React frontend consumes these REST endpoints.

---

## 16. Service Layer

Database and business logic are separated into service modules.

Current services include:

    dashboard_service.py
    owner_service.py
    unit_service.py
    order_service.py
    location_service.py
    history_service.py
    search_service.py

This keeps API route handling separate from database query and registry
logic.

---

## 17. Database Migrations

Alembic is used for database schema versioning.

Run migrations with:

    uv run alembic upgrade head

The migration history contains changes for:

- Initial database schema
- Core entity relationships
- Ownership relationship constraints
- Unit-code uniqueness changes

The database can therefore be reproduced and evolved through versioned
migrations rather than manually changing production tables.

---

## 18. Backend Project Structure

    .
    |
    +-- alembic/
    |   +-- versions/
    |
    +-- app/
    |   +-- models/
    |   +-- services/
    |   +-- main.py
    |
    +-- data/
    |
    +-- docs/
    |
    +-- scripts/
    |
    +-- alembic.ini
    +-- pyproject.toml
    +-- uv.lock
    +-- .env.example
    +-- README.md

---

## 19. Local Development

### Requirements

Install:

- Python
- uv
- PostgreSQL or Supabase database
- Git

### Install dependencies

    uv sync

### Configure environment

Copy the example environment file:

    cp .env.example .env

Configure the database connection and application settings inside .env.

### Run migrations

    uv run alembic upgrade head

### Start development server

    uv run uvicorn app.main:app --reload

The local API will normally be available at:

    http://127.0.0.1:8000

FastAPI Swagger documentation:

    http://127.0.0.1:8000/docs

---

## 20. Production Deployment

Backend hosting:

    Render

Production API:

    https://lumen-property-registry-backend.onrender.com

Health endpoint:

    https://lumen-property-registry-backend.onrender.com/health

Database:

    Supabase PostgreSQL

Frontend:

    Vercel

The frontend communicates with the production backend through the REST API.

---

## 21. Design Principles

### 21.1 Persistent identity

An identity should be created once and enriched over time.

### 21.2 Units, never rows

Multiple source rows can describe the same physical unit.

### 21.3 No unsupported assumptions

If the source does not provide a reliable value, the system does not invent
one.

### 21.4 Historical traceability

Ownership relationships are stored separately from current entity records.

### 21.5 Idempotent ingestion

Repeated ingestion should not create duplicate registry entities or
relationships.

### 21.6 Explicit data limitations

When the source cannot support a reliable entity or relationship, the system
preserves that limitation instead of generating synthetic data.

---

## 22. Frontend Relationship Flow

The backend supports the following navigation model:

    Owner
      |
      +---- Units
              |
              +---- Location
              |
              +---- Owners
              |
              +---- Ownership History
              |
              +---- Orders


    Location
      |
      +---- Registered Units


    Unit
      |
      +---- Owners
      |
      +---- Ownership History
      |
      +---- Location
      |
      +---- Orders

This allows the UI to navigate between related registry entities.

---

## 23. Related Repository

Frontend repository:

    lumen-property-registry-frontend

The frontend contains:

- Dashboard
- Owner list
- Owner profile
- Unit list
- Unit profile
- Location list
- Location profile
- Orders
- History
- Search

---

## 24. Project Status

Implemented:

    [x] PostgreSQL / Supabase database
    [x] FastAPI backend
    [x] SQLAlchemy models
    [x] Alembic migrations
    [x] Owner registry
    [x] Unit registry
    [x] Location registry
    [x] Contact registry
    [x] Owner to Unit relationships
    [x] Unit to Owner relationships
    [x] Ownership history
    [x] Duplicate relationship prevention
    [x] Idempotent registry ingestion
    [x] Dashboard statistics
    [x] Search API
    [x] Owner APIs
    [x] Unit APIs
    [x] Location APIs
    [x] Order API structure
    [x] Production deployment

Pending:

    [ ] Transaction-level Order population

The remaining Order population requires a source containing reliable
row-level transaction/order identifiers.

---

## 25. Summary

The backend provides the persistent registry foundation for the Lumen
Property Registry.

Its primary responsibilities are:

    Persistent identity
    Relationship integrity
    Historical ownership
    Location relationships
    Search
    Data ingestion
    API access
    Database versioning

The architecture intentionally avoids fabricating transaction data or
merging identities based only on ambiguous information.

The result is a registry foundation that can be extended with additional
transaction-level data while preserving the existing Unit and Owner identity
model.