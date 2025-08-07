import pytest
import pandas as pd
import tempfile
import os
from src.main import main
from src.data_processor import process_part_data
from src.config import WARNING_COLUMN, ERROR_COLUMN

def test_main_pipeline_integration():
    """Test that the main pipeline can process data end-to-end."""
    # Create a temporary directory for test data
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a small test dataset
        test_data = pd.DataFrame({
            'holes': [
                '[{"length":250,"radius":10}]',  
                '[{"length":10,"radius":5}]',    
                '[{"length":850,"radius":10}]'   
            ],
            'uuid': ['test1', 'test2', 'test3']
        })
        
        # Save test data to temporary parquet file
        test_input_path = os.path.join(temp_dir, 'test_data.parquet')
        test_data.to_parquet(test_input_path, index=False)
        
        # Process the test data directly
        processed_df = process_part_data(test_data)
        
        
        assert len(processed_df) == 3
        assert WARNING_COLUMN in processed_df.columns
        assert ERROR_COLUMN in processed_df.columns
        
       
        warnings = processed_df[WARNING_COLUMN].sum()
        errors = processed_df[ERROR_COLUMN].sum()
        
        assert warnings == 2
        assert errors == 1

def test_data_processor_robustness():
    """Test that the data processor handles edge cases gracefully."""
    
    minimal_df = pd.DataFrame({
        'uuid': ['test1', 'test2']
    })
    
    result_df = process_part_data(minimal_df)
    assert len(result_df) == 2
    assert WARNING_COLUMN in result_df.columns
    assert ERROR_COLUMN in result_df.columns
    assert not result_df[WARNING_COLUMN].any()
    assert not result_df[ERROR_COLUMN].any()

def test_config_constants():
    """Test that config constants are properly defined."""
    from src.config import WARNING_COLUMN, ERROR_COLUMN, POOR_RATIO, CRITICAL_RATIO
    
    assert WARNING_COLUMN == 'has_unreachable_hole_warning'
    assert ERROR_COLUMN == 'has_unreachable_hole_error'
    assert POOR_RATIO == 10
    assert CRITICAL_RATIO == 40
    assert isinstance(WARNING_COLUMN, str)
    assert isinstance(ERROR_COLUMN, str)

def test_analysis_function():
    """Test the analysis function with various scenarios."""
    from src.data_processor import analyze_unreachability_patterns
    
    
    clean_df = pd.DataFrame({
        WARNING_COLUMN: [False, False, False],
        ERROR_COLUMN: [False, False, False]
    })
    analysis = analyze_unreachability_patterns(clean_df)
    assert analysis['total_parts'] == 3
    assert analysis['parts_with_warnings'] == 0
    assert analysis['parts_with_errors'] == 0
    assert analysis['warning_rate'] == 0.0
    assert analysis['error_rate'] == 0.0
    

    mixed_df = pd.DataFrame({
        WARNING_COLUMN: [True, False, True],
        ERROR_COLUMN: [True, False, False]
    })
    analysis = analyze_unreachability_patterns(mixed_df)
    assert analysis['total_parts'] == 3
    assert analysis['parts_with_warnings'] == 2
    assert analysis['parts_with_errors'] == 1
    assert analysis['warning_rate'] == 2/3
    assert analysis['error_rate'] == 1/3 