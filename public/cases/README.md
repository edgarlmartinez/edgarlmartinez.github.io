# Educational cases

Content lives in `src/data/cases.yaml`; images live in `images/`.

Before adding an image, de-identify its pixel data with `scripts/deid-image.py`:
mask any burned-in text (initials, accession or MRN, dates, scanner or coil labels, PACS overlays),
then the script normalizes intensity, resamples, adds faint noise and re-encodes a fresh PNG with no metadata.
Use year-month or relative intervals only, never exact study dates.
