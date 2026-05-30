import pandas as pd
import sqlite3
import os
import numpy as np

def check_nulls(df, table_name):
    results = []
    for col in df.columns:
        null_count = df[col].isnull().sum()
        null_rate = null_count / len(df) if len(df) > 0 else 0
        status = "PASS" if null_rate <= 0.05 else "FAIL (ALARM)"
        results.append(f"  - {col}: {null_count} nulls ({null_rate:.2%}) [{status}]")
    return results

def check_duplicates(df, pk):
    return df.duplicated(subset=[pk]).sum()

def run_validation(db_path='data/humanitarian.db'):
    """
    Performs data quality checks on the Bronze layer and reports findings.
    """
    print("Running data validation checks...")
    
    conn = sqlite3.connect(db_path)
    
    # Load Bronze tables for validation
    df_beneficiaries = pd.read_sql("SELECT * FROM bronze_beneficiaries", conn)
    df_activities = pd.read_sql("SELECT * FROM bronze_activities", conn)
    df_disbursements = pd.read_sql("SELECT * FROM bronze_disbursements", conn)
    
    report = []
    report.append("--- HUMANITARIAN DATA QUALITY REPORT ---")
    report.append(f"Generated at: {pd.Timestamp.now()}")
    report.append("")
    
    # 1. Null Checks
    report.append("1. NULL VALUE ANALYSIS")
    for name, df in [('Beneficiaries', df_beneficiaries), ('Activities', df_activities), ('Disbursements', df_disbursements)]:
        report.append(f" Table: {name}")
        report.extend(check_nulls(df, name))
    report.append("")
    
    # 2. Duplicate Checks
    report.append("2. DUPLICATE RECORD ANALYSIS")
    for name, df, pk in [('Beneficiaries', df_beneficiaries, 'beneficiary_id'), 
                          ('Activities', df_activities, 'activity_id'), 
                          ('Disbursements', df_disbursements, 'disbursement_id')]:
        dup_count = check_duplicates(df, pk)
        report.append(f" Table: {name} - Duplicates found: {dup_count}")
    report.append("")
    
    # 3. Referential Integrity
    report.append("3. REFERENTIAL INTEGRITY")
    valid_b_ids = set(df_beneficiaries['beneficiary_id'])
    
    orphan_activities = df_activities[~df_activities['beneficiary_id'].isin(valid_b_ids)]
    report.append(f" Orphan Activities (no beneficiary match): {len(orphan_activities)}")
    
    orphan_disbursements = df_disbursements[~df_disbursements['beneficiary_id'].isin(valid_b_ids)]
    report.append(f" Orphan Disbursements (no beneficiary match): {len(orphan_disbursements)}")
    report.append("")
    
    # 4. Outlier Detection (Disbursements)
    report.append("4. OUTLIER DETECTION")
    amounts = df_disbursements['amount_usd']
    mean = amounts.mean()
    std = amounts.std()
    outliers = df_disbursements[np.abs(amounts - mean) > (3 * std)]
    report.append(f" Disbursement Amount Outliers (>3 std dev): {len(outliers)}")
    if len(outliers) > 0:
        report.append(f"  Top outlier value: ${outliers['amount_usd'].max():,.2f}")
    report.append("")
    
    # 5. Date Range Checks
    report.append("5. DATE RANGE VALIDATION")
    today = pd.Timestamp.now().strftime('%Y-%m-%d')
    
    # Check for future dates in beneficiaries registration
    future_regs = df_beneficiaries[df_beneficiaries['registration_date'] > today]
    report.append(f" Future registration dates found: {len(future_regs)}")
    
    # Beneficiaries registered before 2010 (hypothetical program start)
    old_regs = df_beneficiaries[df_beneficiaries['registration_date'] < '2010-01-01']
    report.append(f" Pre-program registration dates (<2010): {len(old_regs)}")
    report.append("")
    
    conn.close()
    
    # Save report
    os.makedirs('output', exist_ok=True)
    report_text = "\n".join(report)
    with open('output/quality_report.txt', 'w') as f:
        f.write(report_text)
    
    print("Validation complete. Report saved to output/quality_report.txt")
    return report_text

if __name__ == "__main__":
    run_validation()
