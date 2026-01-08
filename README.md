# Table Structure Reconstruction

A robust, heuristic-based table extraction tool for digital PDFs using `PyMuPDF`.

## Overview
This tool reconstructs the row/column structure of a table given a PDF page and a bounding box. Unlike ML-based approaches (Tabula, Camelot), this uses explicit "Grid Projection" logic. This ensures that the results are explainable and the logic can be fine-tuned via thresholds.

## Algorithm
The extraction follows a **"Decompose & Map"** strategy:

1.  **Input**: PDF Page + Table Bounding Box (BBox).
2.  **Filter**: Extract text words and vector graphics (lines) strictly within the BBox.
3.  **X-Projection (Columns)**: 
    * Project text presence onto the X-axis to find "Whitespace Rivers" (vertical gaps).
    * Validate gaps: A gap is a column boundary ONLY IF it contains a drawn vertical line OR is wider than `min_col_gap`.
4.  **Y-Projection (Rows)**:
    * Cluster text into visual lines based on Y-coordinates.
    * Insert Row Breaks where drawn horizontal lines exist OR where the vertical gap > `min_row_gap`.
5.  **Atomic Grid**:
    * Intersect the Column and Row boundaries to create a grid of "Atomic Cells".
    * Map every text word to the Atomic Cell it visually overlaps.

## Installation

```bash
pip install pymupdf