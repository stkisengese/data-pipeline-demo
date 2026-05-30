# Bronze Layer: Raw Data (Source of Truth)

The **Bronze Layer** is the entry point for the pipeline. It serves as an immutable "Source of Truth," preserving raw data as-is from field CSV exports before any business logic or cleaning is applied.

### Purpose
- **Auditability:** Retains the original state of data for troubleshooting and historical reference.
- **Traceability:** Adds ingestion metadata to track when data entered the system.
- **Simplicity:** Rapid ingestion without risk of transformation errors.

### Tables Managed
- `bronze_beneficiaries`: Raw registration records.
- `bronze_activities`: Raw program activity logs.
- `bronze_disbursements`: Raw financial disbursement data.

### Transformation Logic (applied in `pipeline/ingest.py`)
- **Metadata Addition:** Appends `ingestion_timestamp` to every record.
- **Format Preservation:** Loads data directly from CSV to SQL with minimal type interference (standard pandas `read_csv` defaults).
