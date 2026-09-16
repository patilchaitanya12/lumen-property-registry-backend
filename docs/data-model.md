# Lumen Property Registry — Data Model

## 1. Overview

The application data model is based on stable domain entities rather than
directly mirroring spreadsheet sheets.

The processed dataset provides the initial data source for the prototype.

The primary domain entities are:

- Owners
- Units
- Locations
- Orders
- Order Parties
- Ownership History
- Contacts

---

## 2. Conceptual ERD

```text
                         ┌──────────────┐
                         │  LOCATIONS   │
                         │──────────────│
                         │ location_id  │
                         │ area         │
                         │ community    │
                         │ project      │
                         │ building     │
                         └──────┬───────┘
                                │
                                │ 1:N
                                v
                         ┌──────────────┐
                         │    UNITS     │
                         │──────────────│
                         │ unit_id      │
                         │ unit_code    │
                         │ unit_number  │
                         │ location_id  │
                         │ property_type│
                         │ size         │
                         └───┬──────┬───┘
                             │      │
                         1:N │      │ 1:N
                             │      │
                             v      v
                 ┌────────────────┐ ┌──────────────┐
                 │  OWNERSHIP     │ │    ORDERS    │
                 │   HISTORY      │ │──────────────│
                 │────────────────│ │ order_id     │
                 │ history_id     │ │ source_regis │
                 │ unit_id        │ │ unit_id      │
                 │ owner_id       │ │ location_id  │
                 │ start_date     │ │ procedure    │
                 │ end_date       │ │ value        │
                 └───────┬────────┘ └──────┬───────┘
                         │                 │
                         │ N:1             │ 1:N
                         v                 v
                  ┌──────────────┐  ┌──────────────┐
                  │    OWNERS    │  │ ORDER_PARTY  │
                  │──────────────│  │──────────────│
                  │ owner_id     │  │ order_party_id
                  │ record_id    │  │ order_id     │
                  │ name         │  │ owner_id     │
                  │ country      │  │ role         │
                  │ identifiers  │  │ source_row_id│
                  └──────┬───────┘  └──────────────┘
                         │
                         │ 1:N
                         v
                  ┌──────────────┐
                  │   CONTACTS   │
                  │──────────────│
                  │ contact_id   │
                  │ owner_id     │
                  │ phone/email  │
                  │ is_primary   │
                  └──────────────┘