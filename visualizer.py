import fitz

class TableVisualizer:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def visualize(self, extraction_result, output_path="debug_output.pdf"):
        """
        Overlays the extracted table structure onto the original PDF.
        Green Lines = Computed Column/Row Boundaries
        Red Rects = Computed Cells
        """
        page_num = extraction_result['meta']['page']
        page = self.doc[page_num]
        
        cols = extraction_result['structure']['col_boundaries']
        rows = extraction_result['structure']['row_boundaries']
        
        shape = page.new_shape()
        shape.finish()
        
        for x in cols:
            p1 = fitz.Point(x, rows[0])
            p2 = fitz.Point(x, rows[-1])
            shape.draw_line(p1, p2)
        
        for y in rows:
            p1 = fitz.Point(cols[0], y)
            p2 = fitz.Point(cols[-1], y)
            shape.draw_line(p1, p2)
            
        shape.finish(color=(0, 1, 0), width=0.5)
        shape.commit()

        shape = page.new_shape()
        for cell in extraction_result['cells']:
            rect = fitz.Rect(cell['bbox'])
            shape.draw_rect(rect)
        
        shape.finish(color=(1, 0, 0), width=0.5)
        shape.commit()
        
        self.doc.save(output_path)
        print(f"Visualization saved to: {output_path}")