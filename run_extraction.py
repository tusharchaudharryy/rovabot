import json
import fitz  
from table_core import TableExtractor
from visualizer import TableVisualizer

INPUT_PDF = "RedBook.pdf"
PAGE_NUM = 6 

TABLE_BBOX = None  

def main():
    doc = fitz.open(INPUT_PDF)
    page = doc[PAGE_NUM]
    
    if TABLE_BBOX is None:
        bbox = page.rect  
    else:
        bbox = TABLE_BBOX
        
    print(f"--- DIAGNOSTICS FOR PAGE {PAGE_NUM + 1} ---")
    print(f"Scanning Area (BBox): {bbox}")

    words = page.get_text("words", clip=bbox)
    drawings = page.get_drawings()
    relevant_lines = [p for p in drawings if fitz.Rect(p['rect']).intersects(bbox)]
    
    print(f"Words found in BBox: {len(words)}")
    print(f"Vector paths found in BBox: {len(relevant_lines)}")
    
    if len(words) == 0:
        print("ERROR: No text found in this area! The visualizer will be empty.")
        return

    print("\nRunning extraction logic...")
    extractor = TableExtractor(INPUT_PDF)
    
    settings = {
        'min_col_gap': 5,    
        'min_row_gap': 2,    
    }
    
    bbox_tuple = (bbox.x0, bbox.y0, bbox.x1, bbox.y1)
    result = extractor.extract_table(PAGE_NUM, bbox_tuple, settings)

    print(f"Detected {len(result['cells'])} cells.")

    print("\nGenerating redbook_debug.pdf...")
    viz = TableVisualizer(INPUT_PDF)
    viz.visualize(result, output_path="redbook_debug.pdf")
    print("Done! Open 'redbook_debug.pdf' to see the red grid.")

if __name__ == "__main__":
    main()