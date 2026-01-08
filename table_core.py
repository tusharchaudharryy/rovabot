import fitz
import statistics

class TableExtractor:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)

    def extract_table(self, page_num, bbox, settings=None):
        """
        Reconstructs table structure from a specific bbox.
        
        Args:
            page_num (int): 0-based page index.
            bbox (tuple): (x0, y0, x1, y1) defining the table area.
            settings (dict): Configuration for thresholds.
        """
        if settings is None:
            settings = {
                'min_col_gap': 10,
                'min_row_gap': 4,
                'line_snap_tol': 2
            }

        page = self.doc[page_num]
        
        raw_words = page.get_text("words", clip=bbox) 
        
        drawings = page.get_drawings()
        v_lines, h_lines = self._filter_lines(drawings, bbox)

        col_dividers = self._detect_columns(raw_words, v_lines, bbox, settings)

        row_dividers = self._detect_rows(raw_words, h_lines, bbox, settings)

        cells = self._map_cells(raw_words, col_dividers, row_dividers)

        return {
            "meta": {
                "page": page_num,
                "bbox": bbox,
                "rows_count": len(row_dividers) - 1,
                "cols_count": len(col_dividers) - 1
            },
            "structure": {
                "col_boundaries": col_dividers,
                "row_boundaries": row_dividers
            },
            "cells": cells
        }

    def _filter_lines(self, drawings, bbox):
        """Separates vector graphics into vertical and horizontal ruling lines."""
        v_lines = []
        h_lines = []
        table_rect = fitz.Rect(bbox)

        for path in drawings:
            if not table_rect.intersects(path['rect']):
                continue
            
            r = path['rect']
            if r.width < 2 and r.height > 5:
                v_lines.append(r.x0)
            elif r.height < 2 and r.width > 5:
                h_lines.append(r.y0)
        
        return sorted(list(set(v_lines))), sorted(list(set(h_lines)))

    def _detect_columns(self, words, v_lines, bbox, settings):
        """Finds column boundaries using 'Whitespace Rivers' and Ruler snapping."""
        x0, _, x1, _ = bbox
        width = int(x1 - x0)
        
        mask = [0] * width
        for w in words:
            rel_x0 = max(0, int(w[0] - x0))
            rel_x1 = min(width, int(w[2] - x0))
            for i in range(rel_x0, rel_x1):
                mask[i] = 1

        dividers = [x0, x1]

        current_gap_len = 0
        gap_start_idx = 0
        
        current_gap_len = 0
        gap_start_idx = 0

        for i, occupied in enumerate(mask):
            if occupied == 0:
                if current_gap_len == 0:
                    gap_start_idx = i
                current_gap_len += 1
            else:
                if current_gap_len > 0:
                    abs_gap_start = x0 + gap_start_idx
                    abs_gap_end = x0 + i
                    gap_center = (abs_gap_start + abs_gap_end) / 2
                    
                    has_line = any(abs_gap_start - 2 <= vl <= abs_gap_end + 2 for vl in v_lines)
                    
                    is_wide = current_gap_len >= settings['min_col_gap']

                    if has_line or is_wide:
                        snap_line = next((vl for vl in v_lines if abs_gap_start - 2 <= vl <= abs_gap_end + 2), None)
                        dividers.append(snap_line if snap_line else gap_center)

                current_gap_len = 0

        return sorted(list(set(dividers)))

    def _detect_rows(self, words, h_lines, bbox, settings):
        """Finds row boundaries using Y-Clustering and Ruling Lines."""
        y_clusters = {}
        for w in words:
            y_center = round((w[1] + w[3]) / 2 / 2) * 2 
            if y_center not in y_clusters: y_clusters[y_center] = []
            y_clusters[y_center].append(w)
        
        sorted_ys = sorted(y_clusters.keys())
        dividers = [bbox[1], bbox[3]]

        if not sorted_ys:
            return sorted(dividers)

        for i in range(len(sorted_ys) - 1):
            curr_y = sorted_ys[i]
            next_y = sorted_ys[i+1]
            
            curr_words = y_clusters[curr_y]
            next_words = y_clusters[next_y]
            
            curr_bottom = max(w[3] for w in curr_words)
            next_top = min(w[1] for w in next_words)
            
            gap_size = next_top - curr_bottom
            mid_point = (curr_bottom + next_top) / 2

            has_line = any(curr_bottom < hl < next_top for hl in h_lines)
            
            avg_height = statistics.mean([w[3]-w[1] for w in curr_words])
            is_wide_gap = gap_size > (avg_height * 0.8)

            if has_line or is_wide_gap:
                dividers.append(mid_point)

        return sorted(list(set(dividers)))

    def _map_cells(self, words, col_divs, row_divs):
        """Maps words into the atomic grid defined by cols and rows."""
        cells = []
        
        for r in range(len(row_divs) - 1):
            for c in range(len(col_divs) - 1):
                cell_box = fitz.Rect(col_divs[c], row_divs[r], col_divs[c+1], row_divs[r+1])
                
                contained_words = []
                for w in words:
                    w_rect = fitz.Rect(w[:4])
                    if w_rect.intersect(cell_box).get_area() > (w_rect.get_area() * 0.5):
                        contained_words.append(w)
                
                if contained_words:
                    contained_words.sort(key=lambda x: x[0])
                    text_content = " ".join([w[4] for w in contained_words])
                    
                    cells.append({
                        "row_idx": r,
                        "col_idx": c,
                        "text": text_content,
                        "bbox": [cell_box.x0, cell_box.y0, cell_box.x1, cell_box.y1]
                    })
        return cells