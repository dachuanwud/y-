
import sys
import os
import pandas as pd

# Add current directory to sys.path
sys.path.append(os.getcwd())

try:
    from components.data_loader import load_market_data, get_data_summary
    from config import DATA_BASE_PATH, DATA_FILES
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

print(f"Configured DATA_BASE_PATH: {DATA_BASE_PATH}")

def test_loader():
    print("\n--- Testing Data Loader ---")
    
    # Check if base path exists
    if os.path.exists(DATA_BASE_PATH):
        print(f"DATA_BASE_PATH exists: {DATA_BASE_PATH}")
        # List contents of base path
        try:
            contents = os.listdir(DATA_BASE_PATH)
            print(f"Contents of DATA_BASE_PATH: {contents}")
        except Exception as e:
            print(f"Error listing DATA_BASE_PATH: {e}")
    else:
        print(f"DATA_BASE_PATH does NOT exist: {DATA_BASE_PATH}")
        # Try to find where data might be
        local_data = os.path.join(os.getcwd(), 'data')
        if os.path.exists(local_data):
             print(f"Found local 'data' directory: {local_data}")
        else:
             print(f"Local 'data' directory not found at: {local_data}")

    # Test loading specific files
    for market_type in ['swap', 'spot']:
        print(f"\nChecking {market_type} data:")
        for key, filename in DATA_FILES.items():
            # Construct expected path manually to verify
            expected_path = os.path.join(DATA_BASE_PATH, market_type, filename)
            exists = os.path.exists(expected_path)
            print(f"  File {filename} ({key}): {'EXISTS' if exists else 'MISSING'} at {expected_path}")
            
            if exists:
                # Try loading via function
                try:
                    df = load_market_data(market_type, key)
                    if df is not None and not df.empty:
                        print(f"    -> Loaded successfully. Shape: {df.shape}")
                    else:
                        print(f"    -> Loaded but empty or None.")
                except Exception as e:
                    print(f"    -> Error loading: {e}")

    # Test Summary
    print("\n--- Testing Summary ---")
    try:
        summary = get_data_summary('swap')
        print(f"Swap Summary: {summary}")
    except Exception as e:
        print(f"Error getting summary: {e}")

if __name__ == "__main__":
    test_loader()

