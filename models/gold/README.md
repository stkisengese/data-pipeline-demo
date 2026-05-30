# Gold Layer: Analytical Marts

The **Gold Layer** contains highly aggregated and curated data models designed for direct consumption by business users, program managers, and visualization tools. It represents the "Product" of the data pipeline.

### Purpose
- **Reporting Readiness:** Tables are optimized for analytical queries (aggregations, summaries).
- **Business Alignment:** Models are structured around humanitarian program KPIs.
- **Performance:** Complex joins are pre-computed to allow for fast dashboarding.

### Models / Analytical Marts
1. **`gold_beneficiary_summary`**
   - **Focus:** Demographic breakdown and vulnerability analysis.
   - **Grains:** `program_id`, `country`.
   - **KPIs:** Total beneficiaries, average age, average vulnerability score, and gender distribution.

2. **`gold_program_activity_report`**
   - **Focus:** Program operational performance.
   - **Grains:** `program_id`, `activity_type`, `status`.
   - **KPIs:** Count of activities completed, pending, or cancelled.

3. **`gold_disbursement_report`**
   - **Focus:** Financial accountability and spend tracking.
   - **Grains:** `program_id`.
   - **KPIs:** Total amount disbursed (USD), average disbursement value, and transaction volume.

### Transformation Logic (applied in `pipeline/transform.py`)
- **Joins:** Links activity and disbursement records back to beneficiary metadata (e.g., to attribute spend to specific programs).
- **Aggregations:** Performs `GROUP BY` operations and calculate summary statistics (`MEAN`, `COUNT`, `SUM`).
- **Pivoting:** Transforms categorical distributions (like gender) into dedicated columns for easier reporting.
