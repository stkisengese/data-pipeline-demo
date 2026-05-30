# Silver Layer: Cleaned & Standardized Data

The **Silver Layer** transforms raw Bronze data into a clean, consistent format suitable for analysis. It resolves data quality issues identified in the ingestion phase, such as duplicates, inconsistent categorical values, and invalid numeric entries.

### Purpose
- **Standardization:** Ensures data follows a uniform format (e.g., standard ISO dates, uniform gender codes).
- **Deduplication:** Removes redundant records to ensure a "Single Source of Truth" for entities like beneficiaries.
- **Validation:** Filters out impossible values and segregates high-risk data (e.g., unverified disbursements).

### Tables Managed
- `silver_beneficiaries`: Unique, cleaned list of program participants.
- `silver_activities`: Standardized activity logs with parsed dates.
- `silver_disbursements`: Verified financial records only.
- `rejected_disbursements`: Audit table for unverified or failed disbursement records.

### Transformation Logic (applied in `pipeline/transform.py`)
- **Deduplication:** Beneficiary records are sorted by `registration_date` and deduplicated by `beneficiary_id`, keeping only the most recent entry.
- **Categorical Standardization:** Maps various gender inputs (e.g., "male", "M", "Male") to standard codes ('M', 'F', or 'Unknown').
- **Age Validation:** Numeric ranges for age are enforced; values `< 0` or `> 120` are nulled out to prevent skewed averages.
- **Verification Filtering:** Only disbursements marked as `verified = 1` are promoted to the Silver layer; others are moved to a rejected table for follow-up.
- **Temporal Alignment:** All date strings are parsed into standardized `datetime` objects.
