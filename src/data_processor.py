import pandas as pd
import json
from src.config import WARNING_COLUMN, ERROR_COLUMN, POOR_RATIO, CRITICAL_RATIO

def process_part_data(df: pd.DataFrame) -> pd.DataFrame:
    processed_df = df.copy()
    # Initialize unreachable hole columns
    processed_df[WARNING_COLUMN] = False
    processed_df[ERROR_COLUMN] = False
    
    print(f"Processing {len(processed_df)} parts for unreachable holes...")
 
    for idx, row in processed_df.iterrows():
        has_warning = False
        has_error = False
    
        if 'holes' in row and pd.notna(row['holes']):
            try:
                holes_data = json.loads(row['holes'])
                if isinstance(holes_data, list):
                    for hole in holes_data:
                        if isinstance(hole, dict) and 'length' in hole and 'radius' in hole:
                            length = hole['length']
                            radius = hole['radius']
                            
                            if isinstance(length, (int, float)) and isinstance(radius, (int, float)) and radius > 0:
                                ratio = length / (radius * 2)
                                
                                if ratio > CRITICAL_RATIO:
                                    has_error = True
                                    has_warning = True  
                                    break  
                                
                                elif ratio > POOR_RATIO:
                                    has_warning = True
                                    
                                    
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
        
        # warning and error flags
        processed_df.at[idx, WARNING_COLUMN] = has_warning
        processed_df.at[idx, ERROR_COLUMN] = has_error
    
    print(f"Processing complete. Found {processed_df[WARNING_COLUMN].sum()} warnings and {processed_df[ERROR_COLUMN].sum()} errors.")
    
    return processed_df

def analyze_unreachability_patterns(df: pd.DataFrame) -> dict:
    analysis = {
        'total_parts': len(df),
        'parts_with_warnings': df[WARNING_COLUMN].sum(),
        'parts_with_errors': df[ERROR_COLUMN].sum(),
        'warning_rate': df[WARNING_COLUMN].mean(),
        'error_rate': df[ERROR_COLUMN].mean(),
        'critical_parts': df[df[ERROR_COLUMN] == True].shape[0]
    }
    
    return analysis
