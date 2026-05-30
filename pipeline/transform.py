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


if __name__ == "__main__":
    transform_to_silver()
