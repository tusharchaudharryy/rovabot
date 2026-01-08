import fitz  
import statistics

class TableExtractor:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)

    def extract_table(self, page_num, bbox, settings=None):
        if settings is None:
            settings = {
                'min_col_gap': 3,      
                'min_row_gap': 1,     
            }

        page = self.doc[page_num]
        
        clip_rect = fitz.Rect(bbox)
        raw_words = page.get_text("words", clip=clip_rect)
        
        drawings = page.get_drawings()
        v_lines, h_lines = self._filter_lines(drawings, bbox)

        col_dividers = self._detect_columns(raw_words, v_lines, bbox, settings)

        row_dividers = self._detect_rows(raw_words, h_lines, bbox, settings)

        cells = self._map_cells(raw_words, col_dividers, row_dividers)
        
        print(f"   -> Logic found {len(col_dividers)-1} columns and {len(row_dividers)-1} rows.")

        return {
            "meta": {"page": page_num, "bbox": bbox},
            "structure": {"col_boundaries": col_dividers, "row_boundaries": row_dividers},
            "cells": cells
        }

    def _filter_lines(self, drawings, bbox):
        v_lines, h_lines = [], []
        table_rect = fitz.Rect(bbox)
        for path in drawings:
            if not table_rect.intersects(path['rect']): continue
            r = path['rect']
            if r.width < 3 and r.height > 5: v_lines.append(r.x0)
            elif r.height < 3 and r.width > 5: h_lines.append(r.y0)
        return sorted(list(set(v_lines))), sorted(list(set(h_lines)))

    def _detect_columns(self, words, v_lines, bbox, settings):
        x0, _, x1, _ = bbox
        width = int(x1 - x0)
        if width <= 0: return [x0, x1]

        histogram = [0] * width
        for w in words:
            rel_start = max(0, int(w[0] - x0))
            rel_end = min(width, int(w[2] - x0))
            for i in range(rel_start, rel_end):
                histogram[i] += 1

        dividers = [x0, x1]
        
        current_gap_len = 0
        gap_start_idx = 0

        for i, density in enumerate(histogram):
            if density == 0: 
                if current_gap_len == 0: gap_start_idx = i
                current_gap_len += 1
            else:
                if current_gap_len > 0:
                    mid_x = x0 + gap_start_idx + (current_gap_len / 2)

                    is_wide = current_gap_len >= settings['min_col_gap']
                    
                    abs_gap_start = x0 + gap_start_idx
                    abs_gap_end = x0 + i
                    has_line = any(abs_gap_start - 2 <= vl <= abs_gap_end + 2 for vl in v_lines)

                    if is_wide or has_line:
                        dividers.append(mid_x)
                current_gap_len = 0
                
        return sorted(list(set(dividers)))

    def _detect_rows(self, words, h_lines, bbox, settings):
        y_clusters = {}
        for w in words:
            y_base = int(w[3]) 
            if y_base not in y_clusters: y_clusters[y_base] = []
            y_clusters[y_base].append(w)
        
        sorted_ys = sorted(y_clusters.keys())
        dividers = [bbox[1], bbox[3]]

        if len(sorted_ys) < 2: return dividers

        for i in range(len(sorted_ys) - 1):
            curr_y = sorted_ys[i]
            next_y = sorted_ys[i+1]
            
            curr_words = y_clusters[curr_y]
            next_words = y_clusters[next_y]
            
            curr_bottom = max(w[3] for w in curr_words)
            next_top = min(w[1] for w in next_words)
            
            gap = next_top - curr_bottom
            mid = (curr_bottom + next_top) / 2
            
            has_line = any(curr_bottom < hl < next_top for hl in h_lines)
            
            if has_line or gap >= settings['min_row_gap']:
                dividers.append(mid)

        return sorted(list(set(dividers)))

    def _map_cells(self, words, col_divs, row_divs):
        cells = []
        for r in range(len(row_divs) - 1):
            for c in range(len(col_divs) - 1):
                x0, x1 = col_divs[c], col_divs[c+1]
                y0, y1 = row_divs[r], row_divs[r+1]
                cell_rect = fitz.Rect(x0, y0, x1, y1)
                
                cell_words = [w for w in words if fitz.Rect(w[:4]).intersects(cell_rect)]
                
                if cell_words:
                    cell_words.sort(key=lambda w: w[0])
                    text = " ".join([w[4] for w in cell_words])
                    cells.append({
                        "row_idx": r, "col_idx": c,
                        "text": text,
                        "bbox": [x0, y0, x1, y1]
                    })
        return cells