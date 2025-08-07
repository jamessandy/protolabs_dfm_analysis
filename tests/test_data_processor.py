# tests/test_data_processor.py
import pytest
import pandas as pd
import json
from src.data_processor import process_part_data, analyze_unreachability_patterns
from src.config import WARNING_COLUMN, ERROR_COLUMN

def test_no_flags_triggered():
    """Tests a part with holes that meet neither warning nor error criteria."""
    df = pd.DataFrame({
        'holes': ['[{"length":10,"radius":5}]']  
    })
    result_df = process_part_data(df)
    assert not result_df[WARNING_COLUMN].iloc[0]
    assert not result_df[ERROR_COLUMN].iloc[0]

def test_warning_only():
    """Tests a part with holes that trigger a warning but not an error."""
    df = pd.DataFrame({
        'holes': ['[{"length":250,"radius":10}]']  
    })
    result_df = process_part_data(df)
    assert result_df[WARNING_COLUMN].iloc[0]
    assert not result_df[ERROR_COLUMN].iloc[0]

def test_error_and_warning():
    """Tests a part with holes that trigger an error (and implicitly a warning)."""
    df = pd.DataFrame({
        'holes': ['[{"length":850,"radius":10}]']  
    })
    result_df = process_part_data(df)
    assert result_df[WARNING_COLUMN].iloc[0]
    assert result_df[ERROR_COLUMN].iloc[0]

def test_multiple_holes_with_error():
    """Tests a part with multiple holes where one triggers the highest severity."""
    holes_json = '[{"length":10,"radius":1}, {"length":850,"radius":10}]'
    df = pd.DataFrame({'holes': [holes_json]})
    result_df = process_part_data(df)
    assert result_df[WARNING_COLUMN].iloc[0]
    assert result_df[ERROR_COLUMN].iloc[0]

def test_multiple_holes_with_warning():
    """Tests a part with multiple holes where some trigger warnings."""
    holes_json = '[{"length":220,"radius":10}, {"length":330,"radius":15}]'  
    df = pd.DataFrame({'holes': [holes_json]})
    result_df = process_part_data(df)
    assert result_df[WARNING_COLUMN].iloc[0]
    assert not result_df[ERROR_COLUMN].iloc[0]

def test_malformed_data_handling():
    """Tests that various forms of bad data are handled gracefully."""
    data = {
        'holes': [
            None,                
            'invalid_json',      
            '[{"length":"bad","radius":10}]',   
            '[{"length":100,"radius":"bad"}]',  
            '[{"length":100}]',  
            '[{"radius":10}]',   
            '[{"length":0,"radius":0}]',  
            '[]'                 
        ]
    }
    df = pd.DataFrame(data)
    result_df = process_part_data(df)
    
    assert len(result_df) == 8
    assert WARNING_COLUMN in result_df.columns
    assert ERROR_COLUMN in result_df.columns

def test_empty_dataframe():
    df = pd.DataFrame()
    result_df = process_part_data(df)
    assert len(result_df) == 0
    assert WARNING_COLUMN in result_df.columns
    assert ERROR_COLUMN in result_df.columns

def test_analyze_unreachability_patterns():
    df = pd.DataFrame({
        WARNING_COLUMN: [True, True, False, False, True],
        ERROR_COLUMN: [True, False, False, True, False]
    })
    
    analysis = analyze_unreachability_patterns(df)
    
    assert analysis['total_parts'] == 5
    assert analysis['parts_with_warnings'] == 3
    assert analysis['parts_with_errors'] == 2
    assert analysis['warning_rate'] == 0.6
    assert analysis['error_rate'] == 0.4
    assert analysis['critical_parts'] == 2

def test_column_names_match_config():
    df = pd.DataFrame({
        'holes': ['[{"length":10,"radius":5}]']
    })
    result_df = process_part_data(df)
    
    assert WARNING_COLUMN in result_df.columns
    assert ERROR_COLUMN in result_df.columns
    assert result_df.columns.tolist().count(WARNING_COLUMN) == 1
    assert result_df.columns.tolist().count(ERROR_COLUMN) == 1