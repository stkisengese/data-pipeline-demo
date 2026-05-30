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
