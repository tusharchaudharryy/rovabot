import json
from table_core import TableExtractor
from visualizer import TableVisualizer

INPUT_PDF = "RedBook.pdf"
PAGE_NUM = 6
TABLE_BBOX = (50, 480, 550, 680) 

def main():
    print(f"Processing {INPUT_PDF} on Page {PAGE_NUM+1}...")

    extractor = TableExtractor(INPUT_PDF)
    
    settings = {
        'min_col_gap': 8,
        'min_row_gap': 5,
    }
    
    result = extractor.extract_table(PAGE_NUM, TABLE_BBOX, settings)

    print("\n--- Extracted Data (JSON) ---")
    print(json.dumps(result['cells'][:3], indent=2))
    print(f"... and {len(result['cells']) - 3} more cells.")

    viz = TableVisualizer(INPUT_PDF)
    viz.visualize(result, output_path="redbook_debug.pdf")

if __name__ == "__main__":
    main()