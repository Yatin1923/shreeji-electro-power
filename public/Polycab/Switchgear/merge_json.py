import os
import json
import glob
from pathlib import Path

def merge_json_from_fan_folders():
    """
    Merge all JSON data from folders containing 'fan' in their name
    Handles both objects and arrays appropriately
    """
    merged_objects = {}
    merged_arrays = []
    processed_files = []
    
    # Get all directories containing 'fan' in their name
    for root, dirs, files in os.walk('.'):
        # Check if current directory contains 'fan' (case-insensitive)
        print(f"Processing folder: {root}")
        
        # Find all JSON files in this directory
        json_files = glob.glob(os.path.join(root, '*.json'))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle different data types
                if isinstance(data, dict):
                    merged_objects.update(data)
                elif isinstance(data, list):
                    merged_arrays.extend(data)
                else:
                    print(f"  ! Skipping {json_file}: Unsupported data type")
                    continue
                
                processed_files.append(json_file)
                print(f"  ✓ Processed: {json_file}")
                
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"  ✗ Error processing {json_file}: {e}")
    
    # Determine final output structure
    if merged_objects and merged_arrays:
        # Both exist - create a combined structure
        final_data = merged_objects
        final_data['__arrays__'] = merged_arrays
    elif merged_arrays and not merged_objects:
        # Only arrays
        final_data = merged_arrays
    else:
        # Only objects (or nothing)
        final_data = merged_objects
    
    # Save merged data
    with open('merged_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nMerged {len(processed_files)} JSON files")
    print(f"Output saved to: merged_data.json")
    
    return final_data

if __name__ == "__main__":
    result = merge_json_from_fan_folders()
