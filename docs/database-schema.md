# Lumen Property Registry — Database Schema

## 1. Purpose

This document defines the initial PostgreSQL schema for the Lumen
Property Registry application.

The schema translates the conceptual domain model into relational tables.

The schema is designed to:

- Preserve stable identities
- Prevent duplicate domain entities
- Represent owner/property relationships
- Preserve ownership history
- Represent transactions/orders and their parties
- Preserve source lineage
- Support search and UI navigation

---

## 2. Tables

The initial schema contains:

1. `owners`
2. `contacts`
3. `locations`
4. `units`
5. `orders`
6. `order_parties`
7. `ownership_history`
8. `source_files`
9. `source_rows`

---

## 3. owners

Stores canonical owner/client identities.

```text
owners
--------------------------------
owner_id              PK
record_id             UNIQUE
name
normalized_name
owner_type
country
id_number
uae_id_number
unified_number
passport_expiry_date
birth_date
created_at
updated_at