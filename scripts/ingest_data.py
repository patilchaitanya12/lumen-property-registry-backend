from __future__ import annotations

import argparse
import hashlib
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from openpyxl import load_workbook
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Contact, Location, Owner, OwnershipHistory, Unit


DEFAULT_FILE = Path("data/raw/04_data_model_v7.xlsx")

OWNER_SHEET = "OWNERS"
CONTACTS_SHEET = "CONTACTS"

PROPERTY_SHEETS = {
    "properties": "PROPERTIES",
    "properties_new": "PROPERTIES_NEW",
}


NULL_VALUES = {
    "",
    "[NOT FOUND]",
    "N/A",
    "NA",
    "NULL",
    "NONE",
    "NAN",
}


# ============================================================================
# NORMALIZATION
# ============================================================================

def clean_value(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if value.upper() in NULL_VALUES:
            return None

        return value

    return value


def normalize_name(value: Any) -> str | None:
    value = clean_value(value)

    if value is None:
        return None

    value = str(value).upper()
    value = re.sub(r"[^A-Z0-9 ]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    return value or None


def normalize_bool(value: Any) -> bool | None:
    value = clean_value(value)

    if value is None:
        return None

    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()

    if normalized in {"true", "1", "yes", "y"}:
        return True

    if normalized in {"false", "0", "no", "n"}:
        return False

    return None


def parse_date(value: Any) -> date | None:
    value = clean_value(value)

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        for fmt in (
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
        ):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                pass

    return None


def make_location_id(
    community: Any,
    building: Any,
) -> str | None:

    community = clean_value(community)
    building = clean_value(building)

    if community is None and building is None:
        return None

    key = f"{community or ''}|{building or ''}"

    digest = hashlib.sha1(
        key.encode("utf-8")
    ).hexdigest()[:16]

    return f"LOC-{digest}"


# ============================================================================
# EXCEL READER
# ============================================================================

def read_sheet(
    path: Path,
    sheet_name: str,
    limit: int | None = None,
    start_row: int = 2,
):
    workbook = load_workbook(
        path,
        read_only=True,
        data_only=True,
    )

    try:
        worksheet = workbook[sheet_name]

        rows = worksheet.iter_rows(
            values_only=True,
        )

        headers = next(rows)

        headers = [
            str(header).strip()
            if header is not None
            else None
            for header in headers
        ]

        for row_number, row in enumerate(
            rows,
            start=2,
        ):
            if row_number < start_row:
                continue

            if (
                limit is not None
                and row_number >= start_row + limit
            ):
                break

            yield row_number, dict(
                zip(headers, row)
            )

    finally:
        workbook.close()


# ============================================================================
# OWNER IMPORT
# ============================================================================

def owner_from_row(
    row: dict[str, Any],
) -> Owner | None:

    owner_id = clean_value(
        row.get("owner_id")
    )

    if owner_id is None:
        return None

    owner_id = str(owner_id).strip()

    name = clean_value(
        row.get("full_name")
    )

    return Owner(
        owner_id=owner_id,
        record_id=clean_value(
            row.get("record_id")
        ),
        name=name or owner_id,
        normalized_name=normalize_name(
            name
        ),
        owner_type=clean_value(
            row.get("owner_type")
        ),
        country=clean_value(
            row.get("nationality")
        ),
        id_number=clean_value(
            row.get("emirates_id")
        ),
        uae_id_number=clean_value(
            row.get("emirates_id")
        ),
        unified_number=None,
        passport_expiry_date=parse_date(
            row.get("passport_expiry_date")
        ),
        birth_date=parse_date(
            row.get("birth_date")
        ),
    )


def ingest_owners(
    path: Path,
    limit: int | None,
    batch_size: int,
    commit: bool,
) -> None:

    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    print()
    print("=" * 70)
    print("OWNER INGESTION")
    print("=" * 70)
    print(f"Source     : {path}")
    print(f"Limit      : {limit or 'ALL'}")
    print(f"Batch size : {batch_size}")
    print(f"Commit     : {commit}")
    print("=" * 70)

    db = SessionLocal()

    created = 0
    existing = 0
    skipped = 0
    processed = 0

    try:
        batch: list[Owner] = []

        for row_number, row in read_sheet(
            path,
            OWNER_SHEET,
            limit=limit,
        ):
            processed += 1

            owner = owner_from_row(row)

            if owner is None:
                skipped += 1
                continue

            batch.append(owner)

            if len(batch) >= batch_size:
                created_now, existing_now = insert_owner_batch(
                    db,
                    batch,
                )

                created += created_now
                existing += existing_now

                db.commit()

                print(
                    f"Processed {processed:,} | "
                    f"Created {created:,} | "
                    f"Existing {existing:,}"
                )

                batch.clear()

        if batch:
            created_now, existing_now = insert_owner_batch(
                db,
                batch,
            )

            created += created_now
            existing += existing_now

            db.commit()

        if not commit:
            # The implementation above commits batches so that large
            # imports don't consume one giant transaction. For dry-run,
            # this function should not be used.
            print(
                "WARNING: owner importer requires --commit."
            )

        print()
        print("=" * 70)
        print("OWNER INGESTION RESULT")
        print("=" * 70)
        print(f"Rows processed : {processed:,}")
        print(f"Owners created : {created:,}")
        print(f"Owners existing: {existing:,}")
        print(f"Rows skipped   : {skipped:,}")
        print("=" * 70)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def insert_owner_batch(
    db: Session,
    owners: list[Owner],
) -> tuple[int, int]:

    if not owners:
        return 0, 0

    owner_ids = [
        owner.owner_id
        for owner in owners
    ]

    existing_ids = set(
        db.scalars(
            select(Owner.owner_id).where(
                Owner.owner_id.in_(owner_ids)
            )
        ).all()
    )

    new_owners = [
        owner
        for owner in owners
        if owner.owner_id not in existing_ids
    ]

    if new_owners:
        db.add_all(new_owners)
        db.flush()

    return len(new_owners), len(existing_ids)


# ============================================================================
# PROPERTY IMPORT
# ============================================================================

def ingest_properties(
    path: Path,
    sheet_name: str,
    limit: int | None,
    batch_size: int,
    commit: bool,
) -> None:

    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    print()
    print("=" * 70)
    print("PROPERTY INGESTION")
    print("=" * 70)
    print(f"Source     : {path}")
    print(f"Sheet      : {sheet_name}")
    print(f"Limit      : {limit or 'ALL'}")
    print(f"Batch size : {batch_size}")
    print(f"Commit     : {commit}")
    print("=" * 70)

    db = SessionLocal()

    stats = {
        "rows_processed": 0,
        "rows_skipped": 0,
        "owners_missing": 0,
        "units_created": 0,
        "units_existing": 0,
        "locations_created": 0,
        "locations_existing": 0,
        "ownership_created": 0,
        "ownership_existing": 0,
    }

    try:
        rows = read_sheet(
            path,
            sheet_name,
            limit=limit,
        )

        batch: list[tuple[int, dict[str, Any]]] = []

        for row_number, row in rows:
            batch.append(
                (row_number, row)
            )

            if len(batch) >= batch_size:
                process_property_batch(
                    db,
                    batch,
                    stats,
                )

                if commit:
                    db.commit()
                else:
                    db.rollback()

                print_progress(stats)

                batch.clear()

        if batch:
            process_property_batch(
                db,
                batch,
                stats,
            )

            if commit:
                db.commit()
            else:
                db.rollback()

            print_progress(stats)

        print()
        print("=" * 70)
        print("PROPERTY INGESTION RESULT")
        print("=" * 70)

        for key, value in stats.items():
            print(
                f"{key.replace('_', ' ').title():28} "
                f"{value:,}"
            )

        print("=" * 70)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def process_property_batch(
    db: Session,
    rows: list[tuple[int, dict[str, Any]]],
    stats: dict[str, int],
) -> None:

    # ------------------------------------------------------------------
    # Prepare valid rows and collect IDs for batch queries
    # ------------------------------------------------------------------

    valid_rows: list[tuple[int, dict[str, Any], str, str]] = []
    property_ids: set[str] = set()
    owner_ids: set[str] = set()

    for row_number, row in rows:
        property_id = clean_value(row.get("property_id"))
        owner_id = clean_value(row.get("owner_id"))

        if property_id is None or owner_id is None:
            stats["rows_skipped"] += 1
            continue

        property_id = str(property_id).strip()
        owner_id = str(owner_id).strip()

        valid_rows.append(
            (row_number, row, property_id, owner_id)
        )

        property_ids.add(property_id)
        owner_ids.add(owner_id)

    if not valid_rows:
        return

    # ------------------------------------------------------------------
    # Batch: owners
    # ------------------------------------------------------------------

    existing_owner_ids = set(
        db.scalars(
            select(Owner.owner_id).where(
                Owner.owner_id.in_(owner_ids)
            )
        ).all()
    )

    stats["owners_missing"] += (
        len(owner_ids - existing_owner_ids)
    )

    # ------------------------------------------------------------------
    # Batch: existing units
    # ------------------------------------------------------------------

    existing_units = {
        unit.unit_id: unit
        for unit in db.scalars(
            select(Unit).where(
                Unit.unit_id.in_(property_ids)
            )
        ).all()
    }

    stats["units_existing"] += len(existing_units)

    # ------------------------------------------------------------------
    # Batch: locations
    #
    # Build the location information first. Multiple properties can
    # legitimately point to the same location.
    # ------------------------------------------------------------------

    location_data: dict[str, dict[str, Any]] = {}

    for _, row, _, owner_id in valid_rows:

        if owner_id not in existing_owner_ids:
            continue

        location_id = make_location_id(
            row.get("community"),
            row.get("building"),
        )

        if not location_id:
            continue

        if location_id not in location_data:
            location_data[location_id] = {
                "community": clean_value(
                    row.get("community")
                ),
                "building_name": clean_value(
                    row.get("building")
                ),
            }

    existing_locations = {
        location.location_id: location
        for location in db.scalars(
            select(Location).where(
                Location.location_id.in_(
                    location_data.keys()
                )
            )
        ).all()
    }

    new_locations = []

    for location_id, data in location_data.items():

        if location_id in existing_locations:
            stats["locations_existing"] += 1
            continue

        location = Location(
            location_id=location_id,
            community=data["community"],
            building_name=data["building_name"],
        )

        new_locations.append(location)
        existing_locations[location_id] = location

    if new_locations:
        db.add_all(new_locations)
        db.flush()

        stats["locations_created"] += len(new_locations)

    # ------------------------------------------------------------------
    # Create new units
    # ------------------------------------------------------------------

    new_units = []

    for _, row, property_id, owner_id in valid_rows:

        if owner_id not in existing_owner_ids:
            continue

        if property_id in existing_units:
            continue

        location_id = make_location_id(
            row.get("community"),
            row.get("building"),
        )

        unit = Unit(
            unit_id=property_id,
            property_id=property_id,

            # IMPORTANT:
            # unit_code is NOT globally unique.
            unit_code=clean_value(
                row.get("unit")
            ),

            unit_number=clean_value(
                row.get("unit")
            ),

            location_id=location_id,

            property_type=clean_value(
                row.get("property_type")
            ),

            size=clean_value(
                row.get("area_sqm")
            ),

            dm_no=clean_value(
                row.get("dm_no")
            ),

            dm_sub_no=clean_value(
                row.get("dm_sub_no")
            ),

            land_sub_number=clean_value(
                row.get("land_sub_number")
            ),
        )

        new_units.append(unit)

        # Keep local set so duplicate property IDs inside the same
        # Excel batch are not inserted twice.
        existing_units[property_id] = unit

    if new_units:
        db.add_all(new_units)
        db.flush()

        stats["units_created"] += len(new_units)

    # ------------------------------------------------------------------
    # Batch: existing ownership relationships
    # ------------------------------------------------------------------

    ownership_pairs = {
        (property_id, owner_id)
        for _, _, property_id, owner_id in valid_rows
        if owner_id in existing_owner_ids
    }

    if not ownership_pairs:
        stats["rows_processed"] += len(valid_rows)
        return

    ownership_unit_ids = {
        unit_id
        for unit_id, _ in ownership_pairs
    }

    ownership_owner_ids = {
        owner_id
        for _, owner_id in ownership_pairs
    }

    existing_ownership = {
        (unit_id, owner_id)
        for unit_id, owner_id in db.execute(
            select(
                OwnershipHistory.unit_id,
                OwnershipHistory.owner_id,
            ).where(
                OwnershipHistory.unit_id.in_(
                    ownership_unit_ids
                ),
                OwnershipHistory.owner_id.in_(
                    ownership_owner_ids
                ),
            )
        ).all()
    }

    new_ownership = []

    for unit_id, owner_id in ownership_pairs:

        if (unit_id, owner_id) in existing_ownership:
            stats["ownership_existing"] += 1
            continue

        new_ownership.append(
            OwnershipHistory(
                unit_id=unit_id,
                owner_id=owner_id,
            )
        )

    if new_ownership:
        db.add_all(new_ownership)
        db.flush()

        stats["ownership_created"] += len(new_ownership)

    # ------------------------------------------------------------------
    # Processed rows
    # ------------------------------------------------------------------

    stats["rows_processed"] += len(valid_rows)


def print_progress(
    stats: dict[str, int],
) -> None:

    print(
        f"Processed {stats['rows_processed']:,} | "
        f"Units +{stats['units_created']:,} | "
        f"Owners missing {stats['owners_missing']:,} | "
        f"Ownership +{stats['ownership_created']:,}"
    )


# ============================================================================
# CONTACT IMPORT
# ============================================================================

def ingest_contacts(
    path: Path,
    limit: int | None,
    commit: bool,
) -> None:

    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    print()
    print("=" * 70)
    print("CONTACT INGESTION")
    print("=" * 70)
    print(f"Source : {path}")
    print(f"Limit  : {limit or 'ALL'}")
    print(f"Commit : {commit}")
    print("=" * 70)

    db = SessionLocal()

    created = 0
    existing = 0
    skipped = 0
    processed = 0

    try:
        for _, row in read_sheet(
            path,
            CONTACTS_SHEET,
            limit=limit,
        ):
            processed += 1

            owner_id = clean_value(
                row.get("owner_id")
            )

            contact_type = clean_value(
                row.get("contact_type")
            )

            contact_value = clean_value(
                row.get("contact_value")
            )

            if (
                owner_id is None
                or contact_type is None
                or contact_value is None
            ):
                skipped += 1
                continue

            owner_id = str(owner_id).strip()
            contact_type = str(contact_type).strip()
            contact_value = str(contact_value).strip()

            if db.get(Owner, owner_id) is None:
                skipped += 1
                continue

            existing_contact = db.scalar(
                select(Contact).where(
                    Contact.owner_id == owner_id,
                    Contact.contact_type == contact_type,
                    Contact.contact_value == contact_value,
                )
            )

            if existing_contact is not None:
                existing += 1
                continue

            db.add(
                Contact(
                    owner_id=owner_id,
                    contact_type=contact_type,
                    contact_value=contact_value,
                    is_primary=normalize_bool(
                        row.get("is_primary")
                    ) or False,
                )
            )

            created += 1

            if processed % 500 == 0:
                db.flush()

        if commit:
            db.commit()
        else:
            db.rollback()

        print()
        print("=" * 70)
        print("CONTACT INGESTION RESULT")
        print("=" * 70)
        print(f"Rows processed : {processed:,}")
        print(f"Contacts created: {created:,}")
        print(f"Contacts existing: {existing:,}")
        print(f"Rows skipped   : {skipped:,}")
        print("=" * 70)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================================
# CLI
# ============================================================================

def main() -> None:

    parser = argparse.ArgumentParser(
        description="Lumen Property Registry data ingestion."
    )

    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_FILE,
    )

    parser.add_argument(
        "--entity",
        choices={
            "owners",
            "properties",
            "contacts",
        },
        default="properties",
    )

    parser.add_argument(
        "--sheet",
        choices=PROPERTY_SHEETS.keys(),
        default="properties",
        help="Property source sheet.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
    )

    parser.add_argument(
        "--commit",
        action="store_true",
        help="Commit changes to PostgreSQL.",
    )

    args = parser.parse_args()

    if not args.file.exists():
        raise FileNotFoundError(
            f"Workbook not found: {args.file}"
        )

    if args.entity == "owners":

        ingest_owners(
            path=args.file,
            limit=args.limit,
            batch_size=args.batch_size,
            commit=args.commit,
        )

    elif args.entity == "properties":

        ingest_properties(
            path=args.file,
            sheet_name=PROPERTY_SHEETS[args.sheet],
            limit=args.limit,
            batch_size=args.batch_size,
            commit=args.commit,
        )

    elif args.entity == "contacts":

        ingest_contacts(
            path=args.file,
            limit=args.limit,
            commit=args.commit,
        )


if __name__ == "__main__":
    main()