# Mortgage Data Model (MISMO 3.4 Canonical)

LOS-Agnostic residential mortgage repository. First integration: ICE Encompass.

## Structure
- **schemas/**: MISMO 3.4 Reference Model XSDs.
- **mappings/**: Encompass Data Dictionary + transformations.
- **samples/**: Test data for validation.

## Usage
1. `pip install -r requirements.txt`
2. `python generator.py` → Generates DDL, ERD, etc.
3. Load into Postgres/Snowflake.

See `docs/` for ERD and mappings.
