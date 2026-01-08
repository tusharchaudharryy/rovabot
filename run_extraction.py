import json
from table_core import TableExtractor
from visualizer import TableVisualizer

# 1. CONFIGURATION
INPUT_PDF = "RedBook.pdf"
PAGE_NUM = 6  # Page 7 is index 6
# Approx bbox for the "DEVIATED WELL CALCULATIONS" table. 
# In production, this comes from your Marker API.
TABLE_BBOX = (50, 480, 550, 680) 

def main():
    print(f"Processing {INPUT_PDF} on Page {PAGE_NUM+1}...")

    # 2. RUN EXTRACTION
    extractor = TableExtractor(INPUT_PDF)
    
    # You can tweak thresholds here if rows/cols are being missed
    settings = {
        'min_col_gap': 8,   # Decrease if columns are merged erroneously
        'min_row_gap': 5,   # Decrease if rows are merged erroneously
    }
    
    result = extractor.extract_table(PAGE_NUM, TABLE_BBOX, settings)

    # 3. PRINT JSON RESULTS
    print("\n--- Extracted Data (JSON) ---")
    print(json.dumps(result['cells'][:3], indent=2)) # Print first 3 cells as preview
    print(f"... and {len(result['cells']) - 3} more cells.")

    # 4. GENERATE VISUAL DEBUG
    viz = TableVisualizer(INPUT_PDF)
    viz.visualize(result, output_path="redbook_debug.pdf")

if __name__ == "__main__":
    main()