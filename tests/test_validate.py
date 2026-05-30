import pandas as pd
import pytest
from pipeline.validate import check_nulls, check_duplicates

def test_check_nulls_pass():
    df = pd.DataFrame({'col1': [1, 2, 3, 4, 5, None]}) # 1/6 = 16.6% nulls -> FAIL
    # Wait, 1/6 is > 5%. 
    df_pass = pd.DataFrame({'col1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, None]}) # 1/21 < 5%
    results = check_nulls(df_pass, 'test_table')
    assert any("PASS" in res for res in results)

def test_check_nulls_fail():
    df_fail = pd.DataFrame({'col1': [1, None, None, None]}) # 75% nulls
    results = check_nulls(df_fail, 'test_table')
    assert any("FAIL" in res for res in results)

def test_check_duplicates():
    df = pd.DataFrame({'id': [1, 1, 2, 3]})
    assert check_duplicates(df, 'id') == 1
    
    df_no_dup = pd.DataFrame({'id': [1, 2, 3]})
    assert check_duplicates(df_no_dup, 'id') == 0
