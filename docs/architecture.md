# Lumen Property Registry — Architecture

## 1. Purpose

The Lumen Property Registry is a data-driven application for organizing
property, owner, transaction/order, location, and historical ownership data.

The system is designed around stable identities and explicit relationships
rather than treating individual spreadsheet rows as independent entities.

The application must provide a functional UI for navigating:

- Owners
- Units / Properties
- Orders / Transactions
- Locations
- Ownership history
- Search and identification

---

## 2. High-Level Architecture

```text
                Processed Excel Dataset
                         |
                         v
                Local Data Ingestion
                         |
                         v
              Identity / Transformation
                         |
                         v
              PostgreSQL / Supabase
                         |
                         v
                    FastAPI API
                         |
                         v
                 React Frontend