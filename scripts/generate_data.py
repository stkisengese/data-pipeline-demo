import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from datetime import datetime, timedelta

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)
fake = Faker()

def generate_beneficiaries(num_rows=500):
    """
    Generates synthetic beneficiary data.
    Includes intentional issues: nulls, duplicates, invalid ages.
    """
    countries = ['Kenya', 'Ethiopia', 'South Sudan', 'Somalia', 'DRC']
    data = []
    
    for _ in range(num_rows):
        reg_date = fake.date_between(start_date='-2y', end_date='today')
        data.append({
            'beneficiary_id': f"BEN-{fake.unique.random_number(digits=6, fix_len=True)}",
            'program_id': f"PROG-{random.randint(101, 105)}",
            'registration_date': reg_date.isoformat(),
            'country': random.choice(countries),
            'age': random.randint(0, 100),
            'gender': random.choice(['M', 'F', 'Male', 'Female', 'male', 'female', None]),
            'household_size': random.randint(1, 12),
            'vulnerability_score': round(random.uniform(0.1, 1.0), 2)
        })
    
    df = pd.DataFrame(data)
    
    # Inject intentional data quality issues
    
    # 1. Nulls in vulnerability_score (approx 7% to exceed 5% threshold)
    null_indices = random.sample(range(num_rows), int(num_rows * 0.07))
    df.loc[null_indices, 'vulnerability_score'] = np.nan
    
    # 2. Invalid ages (< 0 or > 120)
    invalid_age_indices = random.sample(range(num_rows), 10)
    for idx in invalid_age_indices[:5]:
        df.loc[idx, 'age'] = -1
    for idx in invalid_age_indices[5:]:
        df.loc[idx, 'age'] = 150
        
    # 3. Duplicates
    duplicates = df.sample(n=15, replace=True)
    df = pd.concat([df, duplicates], ignore_index=True)
    
    return df

def generate_activities(beneficiary_ids, num_rows=300):
    """
    Generates synthetic activity data.
    Includes intentional orphans (beneficiary_id not in beneficiaries).
    """
    activity_types = ['cash transfer', 'food assistance', 'health screening', 'education support']
    statuses = ['completed', 'pending', 'cancelled']
    data = []
    
    for _ in range(num_rows):
        # 95% of the time, use a valid beneficiary_id
        if random.random() > 0.05:
            b_id = random.choice(beneficiary_ids)
        else:
            b_id = f"BEN-{fake.random_number(digits=6, fix_len=True)}" # Potential orphan
            
        data.append({
            'activity_id': f"ACT-{fake.unique.random_number(digits=6, fix_len=True)}",
            'beneficiary_id': b_id,
            'activity_type': random.choice(activity_types),
            'activity_date': fake.date_between(start_date='-1y', end_date='today').isoformat(),
            'staff_id': f"STAFF-{random.randint(1, 20)}",
            'status': random.choice(statuses)
        })
    
    return pd.DataFrame(data)

def generate_disbursements(beneficiary_ids, num_rows=400):
    """
    Generates synthetic disbursement data.
    Includes outliers and unverified records.
    """
    payment_methods = ['Mobile Money', 'Cash in Hand', 'Bank Transfer', 'Voucher']
    data = []
    
    for _ in range(num_rows):
        # 98% of the time, use a valid beneficiary_id
        if random.random() > 0.02:
            b_id = random.choice(beneficiary_ids)
        else:
            b_id = f"BEN-{fake.random_number(digits=6, fix_len=True)}"
            
        amount = round(random.uniform(20.0, 150.0), 2)
        
        # Inject outliers (> 3 std dev roughly)
        if random.random() < 0.02:
            amount = round(random.uniform(1000.0, 2000.0), 2)
            
        data.append({
            'disbursement_id': f"DISB-{fake.unique.random_number(digits=6, fix_len=True)}",
            'beneficiary_id': b_id,
            'amount_usd': amount,
            'disbursement_date': fake.date_between(start_date='-1y', end_date='today').isoformat(),
            'payment_method': random.choice(payment_methods),
            'verified': random.random() > 0.1 # 10% unverified
        })
        
    return pd.DataFrame(data)

def main():
    print("Generating synthetic humanitarian data...")
    
    os.makedirs('data/raw', exist_ok=True)
    
    df_beneficiaries = generate_beneficiaries(500)
    beneficiary_ids = df_beneficiaries['beneficiary_id'].unique().tolist()
    
    df_activities = generate_activities(beneficiary_ids, 300)
    df_disbursements = generate_disbursements(beneficiary_ids, 400)
    
    df_beneficiaries.to_csv('data/raw/beneficiaries.csv', index=False)
    df_activities.to_csv('data/raw/activities.csv', index=False)
    df_disbursements.to_csv('data/raw/disbursements.csv', index=False)
    
    print(f"Generated {len(df_beneficiaries)} beneficiaries.")
    print(f"Generated {len(df_activities)} activities.")
    print(f"Generated {len(df_disbursements)} disbursements.")
    print("Files saved to data/raw/")

if __name__ == "__main__":
    main()
