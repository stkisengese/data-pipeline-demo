import sys
import os
import time
from datetime import datetime

# Add the project root to sys.path to allow imports if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ingest
import validate
import transform

def log_step(step_name):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{timestamp}] >>> STARTING STEP: {step_name}")

def main():
    start_time = time.time()
    print("====================================================")
    print("   HUMANITARIAN DATA PIPELINE EXECUTION STARTED")
    print("====================================================")
    
    try:
        # Step 1: Ingestion
        log_step("INGESTION (Bronze Layer)")
        ingest.main()
        
        # Step 2: Validation
        log_step("VALIDATION (Data Quality Checks)")
        validate.run_validation()
        
        # Step 3: Transformation - Silver
        log_step("TRANSFORMATION (Silver Layer)")
        transform.transform_to_silver()
        
        # Step 4: Transformation - Gold
        log_step("TRANSFORMATION (Gold Layer)")
        transform.transform_to_gold()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n====================================================")
        print(f"   PIPELINE COMPLETED SUCCESSFULLY IN {duration:.2f}s")
        print("   Quality report: output/quality_report.txt")
        print("   Database: data/humanitarian.db")
        print("====================================================")
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
