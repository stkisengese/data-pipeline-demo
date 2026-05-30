import pandas as pd
import sqlite3
import os
from datetime import datetime

def transform_to_silver(db_path='data/humanitarian.db'):
    """
    Cleans and standardizes Bronze data into Silver layer.
    """
    print("Transforming Bronze to Silver...")
    conn = sqlite3.connect(db_path)
    
    # 1. Beneficiaries Silver
    df_b = pd.read_sql("SELECT * FROM bronze_beneficiaries", conn)
    
    # Standardise Gender
    gender_map = {
        'male': 'M', 'Male': 'M', 'M': 'M',
        'female': 'F', 'Female': 'F', 'F': 'F'
    }
    df_b['gender'] = df_b['gender'].map(gender_map).fillna('Unknown')
    
    # Standardise Ages
    df_b.loc[(df_b['age'] < 0) | (df_b['age'] > 120), 'age'] = None
    
    # Deduplicate (keep latest registration_date)
    df_b['registration_date'] = pd.to_datetime(df_b['registration_date'])
    df_b = df_b.sort_values('registration_date', ascending=False).drop_duplicates('beneficiary_id')
    
    # Save to Silver
    df_b.to_sql('silver_beneficiaries', conn, if_exists='replace', index=False)
    print(f"Loaded {len(df_b)} records into silver_beneficiaries.")
    
    # 2. Activities Silver
    df_a = pd.read_sql("SELECT * FROM bronze_activities", conn)
    # Join with beneficiaries to check for orphans (but we keep them in silver, maybe flag them)
    # For simplicity, we just save them as is, but we could filter or flag.
    df_a['activity_date'] = pd.to_datetime(df_a['activity_date'])
    df_a.to_sql('silver_activities', conn, if_exists='replace', index=False)
    print(f"Loaded {len(df_a)} records into silver_activities.")
    
    # 3. Disbursements Silver
    df_d = pd.read_sql("SELECT * FROM bronze_disbursements", conn)
    
    # Filter verified only
    df_rejected = df_d[df_d['verified'] == 0].copy()
    df_verified = df_d[df_d['verified'] == 1].copy()
    
    df_verified['disbursement_date'] = pd.to_datetime(df_verified['disbursement_date'])
    
    df_verified.to_sql('silver_disbursements', conn, if_exists='replace', index=False)
    df_rejected.to_sql('rejected_disbursements', conn, if_exists='replace', index=False)
    print(f"Loaded {len(df_verified)} records into silver_disbursements ({len(df_rejected)} rejected).")
    
    conn.close()

def transform_to_gold(db_path='data/humanitarian.db'):
    """
    Aggregates Silver data into Gold analytical marts.
    """
    print("Transforming Silver to Gold...")
    conn = sqlite3.connect(db_path)
    
    # Load Silver tables
    df_b = pd.read_sql("SELECT * FROM silver_beneficiaries", conn)
    df_a = pd.read_sql("SELECT * FROM silver_activities", conn)
    df_d = pd.read_sql("SELECT * FROM silver_disbursements", conn)
    
    # 1. beneficiary_summary: per program, per country
    beneficiary_summary = df_b.groupby(['program_id', 'country']).agg(
        total_beneficiaries=('beneficiary_id', 'count'),
        avg_age=('age', 'mean'),
        avg_vulnerability=('vulnerability_score', 'mean')
    ).reset_index()
    
    # Gender breakdown (pivoted)
    gender_counts = df_b.groupby(['program_id', 'country', 'gender']).size().unstack(fill_value=0).reset_index()
    beneficiary_summary = beneficiary_summary.merge(gender_counts, on=['program_id', 'country'], how='left')
    
    beneficiary_summary.to_sql('gold_beneficiary_summary', conn, if_exists='replace', index=False)
    
    # 2. program_activity_report: activity counts by type and status, per program
    activity_report = df_a.groupby(['activity_type', 'status']).size().reset_index(name='count')
    # Actually, the prompt says "per program"
    activity_report_prog = df_a.merge(df_b[['beneficiary_id', 'program_id']], on='beneficiary_id', how='left')
    activity_report_prog = activity_report_prog.groupby(['program_id', 'activity_type', 'status']).size().reset_index(name='activity_count')
    
    activity_report_prog.to_sql('gold_program_activity_report', conn, if_exists='replace', index=False)
    
    # 3. disbursement_report: total disbursed per program
    # Need to link disbursements to programs via beneficiaries
    df_d_prog = df_d.merge(df_b[['beneficiary_id', 'program_id']], on='beneficiary_id', how='left')
    disbursement_report = df_d_prog.groupby('program_id').agg(
        total_amount_usd=('amount_usd', 'sum'),
        avg_disbursement=('amount_usd', 'mean'),
        disbursement_count=('disbursement_id', 'count')
    ).reset_index()
    
    disbursement_report.to_sql('gold_disbursement_report', conn, if_exists='replace', index=False)
    
    print("Gold marts created successfully.")
    conn.close()

if __name__ == "__main__":
    transform_to_silver()
    transform_to_gold()
