import fitz

class TableVisualizer:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)

    def visualize(self, extraction_result, output_path="debug_output.pdf"):
        page_num = extraction_result['meta']['page']
        page = self.doc[page_num]
        
        shape = page.new_shape()
        cols = extraction_result['structure']['col_boundaries']
        rows = extraction_result['structure']['row_boundaries']
        
        min_y, max_y = rows[0], rows[-1]
        min_x, max_x = cols[0], cols[-1]

        for x in cols:
            shape.draw_line(fitz.Point(x, min_y), fitz.Point(x, max_y))
        for y in rows:
            shape.draw_line(fitz.Point(min_x, y), fitz.Point(max_x, y))
            
        shape.finish(color=(0, 1, 0), width=0.5)
        shape.commit(overlay=True) 

        shape = page.new_shape()
        for cell in extraction_result['cells']:
            rect = fitz.Rect(cell['bbox'])
            shape.draw_rect(rect)
        
        shape.finish(color=(1, 0, 0), width=0.5)
        shape.commit(overlay=True)
        
        self.doc.save(output_path)