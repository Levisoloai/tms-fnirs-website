# Ingestion Process README

This document outlines the process for ingesting new TMS/TBS protocols into the system.
The primary scripts involved are `ingest/search.py` for literature harvesting and `ingest/convert_to_yaml.py` for converting curated data into the required YAML format.

## Data Flow

1.  **Literature Harvesting (`search.py`)**:
    *   `ingest/search.py` is used to query scientific databases (e.g., CrossRef, PubMed) for relevant papers.
    *   Output is a JSON file (e.g., `data/literature/{yyyymmdd_query_results}.json`) containing raw paper details (title, authors, DOI, year, abstract).

2.  **Manual Curation (Analysts)**:
    *   Analysts review the JSON output from `search.py`.
    *   Key parameters, effect sizes, evidence levels, etc., are extracted and populated into a structured format (e.g., Airtable, which is then exported to CSV).

3.  **CSV Preparation**:
    *   The curated data is formatted into a CSV file (e.g., `curated/psychiatry_{date}.csv`).
    *   This CSV file serves as the input for the YAML conversion script.

4.  **YAML Conversion (`convert_to_yaml.py`)**:
    *   `ingest/convert_to_yaml.py` processes the input CSV.
    *   It generates one YAML file per diagnosis (e.g., `ingest/protocols/MajorDepressiveDisorder.yaml`) based on a Jinja2 template.
    *   These YAML files are then used for loading data into the graph database and for testing.

## CSV Input Specification for `convert_to_yaml.py`

The CSV file provided to `ingest/convert_to_yaml.py` must adhere to the following column structure:

| Column Name         | Type                       | Description                                                                      | Example                                   | Notes                                     |
|---------------------|----------------------------|----------------------------------------------------------------------------------|-------------------------------------------|-------------------------------------------|
| `diagnosis`         | string                     | The medical diagnosis the protocol pertains to.                                  | "Major Depressive Disorder"             | Used for naming the output YAML file.     |
| `protocol_id`       | string (slug)              | A unique identifier for the protocol under the diagnosis (no spaces, use hyphens). | "HF_10Hz_L_DLPFC"                         |                                           |
| `target`            | string                     | The brain region targeted by the protocol.                                       | "Left DLPFC"                              |                                           |
| `pattern`           | string                     | The TMS/TBS pattern used.                                                        | "HF-rTMS", "iTBS", "Seq-HF/LF"            |                                           |
| `frequency_hz`      | float / string             | The stimulation frequency in Hertz.                                              | 10, 50, "10 (L) / 1 (R)"                  | String for bilateral/sequential protocols.|
| `intensity_pct_mt`  | float                      | Stimulation intensity as a percentage of Motor Threshold (MT).                   | 120                                       | Use if intensity is MT-based.             |
| `intensity_pct_amt` | float                      | Stimulation intensity as a percentage of Active Motor Threshold (AMT).           | 80                                        | Use if intensity is AMT-based.             |
| `pulses`            | integer                    | The number of pulses delivered per session.                                      | 3000                                      |                                           |
| `train_s`           | float                      | Duration of each stimulation train in seconds.                                   | 4, 0.190                                  | Nullable (leave empty if not applicable). |
| `iti_s`             | float                      | Inter-Train Interval in seconds.                                                 | 26, 8                                     | Nullable (leave empty if not applicable). |
| `sessions`          | string                     | Total number of sessions or range.                                               | "20-30", "20", "30-36 + maintenance"      |                                           |
| `schedule`          | string                     | The typical session schedule.                                                    | "5×/week"                                 |                                           |
| `evidence_level`    | string                     | The level of evidence supporting the protocol.                                   | "High", "Moderate", "Emerging"          | Based on predefined rubric.               |
| `evidence_refs`     | string                     | List of citation strings for evidence, separated by semicolons (`;`).           | "Ref 1 Details...; Ref 2 Details..."      | Each part becomes an item in YAML list.   |

**Note on Intensity:** Provide a value for *either* `intensity_pct_mt` *or* `intensity_pct_amt`, not both. The script should handle which one is present.

## Command-Line Examples

### Running `search.py`:

Used to query scientific databases for relevant papers. Supports pagination and date filtering.

**New Example:**
```bash
python ingest/search.py --query "TMS AND fNIRS" --since 2024-01-01 --max-results 150 --out data/literature/20240608_tms_fnirs.json
```
*   `--query`: The search terms.
*   `--since`: Optional start date (YYYY-MM-DD) for results.
*   `--max-results`: Optional. Maximum number of results to retrieve (default is 100). The script handles pagination to fetch these results.
*   `--out`: Specifies the output JSON file path. If not provided, a default name is generated in `data/literature/`.
*   `--results-per-page`: Optional. Number of results per API call (default 100).

### Running `convert_to_yaml.py`:

Processes a curated CSV file and generates protocol YAML files, one per diagnosis.
Supports input validation and a dry-run mode.

**New Example (Dry Run):**
```bash
python ingest/convert_to_yaml.py --input curated/psychiatry_20240608.csv --dry-run
```

**Example (File Output):**
```bash
python ingest/convert_to_yaml.py --input curated/psychiatry_20240608.csv --output_dir ingest/protocols/
```
*   `--input`: Path to the input CSV file.
*   `--output_dir`: Directory to save generated YAML files (required if not using `--dry-run`).
*   `--dry-run`: Optional. If specified, prints rendered YAML to standard output instead of writing to files. Useful for previews.
*   `--template_dir`: Optional. Directory containing the Jinja2 template (defaults to `ingest/`).
*   `--template_name`: Optional. Name of the Jinja2 template file (defaults to `protocol_template.yaml.j2`).


This README will be updated as the scripts are developed and refined.
