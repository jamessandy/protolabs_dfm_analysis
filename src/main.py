# src/main.py
import pandas as pd
from src.data_processor import process_part_data
from src.config import WARNING_COLUMN, ERROR_COLUMN

# Define file paths relative to the dataset's location
INPUT_PATH = '/Users/icon/protolabs_dfm_analysis/data/raw/2023 DE_case_dataset.gz.parquet'
OUTPUT_PATH = '/Users/icon/protolabs_dfm_analysis/data/processed/processed_data.parquet'

def main():
    try:
        print(f"Loading data from {INPUT_PATH}...")
        raw_df = pd.read_parquet(INPUT_PATH)
        print("Data loaded successfully.")

        print("\n  Processing part data to add unreachable hole flags...")
        processed_df = process_part_data(raw_df)
        print(" Processing complete.")

        print("\n Results:")
        print("Unreachable hole warning column value counts:")
        print(processed_df[WARNING_COLUMN].value_counts())
        print("\nUnreachable hole error column value counts:")
        print(processed_df[ERROR_COLUMN].value_counts())
        
        print(f"\n Saving processed data to {OUTPUT_PATH}...")
        processed_df.to_parquet(OUTPUT_PATH, index=False)
        print(" Pipeline finished successfully.")

    except FileNotFoundError:
        print(f" Error: Input file not found at {INPUT_PATH}")
    except Exception as e:
        print(f" An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()