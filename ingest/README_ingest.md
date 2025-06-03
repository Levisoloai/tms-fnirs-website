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

### Running `convert_to_yaml.py`:

To convert a curated CSV file into protocol YAML files:

```bash
python ingest/convert_to_yaml.py --input curated/psychiatry_20250607.csv --output_dir ingest/protocols/
```
*(Assuming the script takes `--input` and `--output_dir` arguments. The placeholder script will need to be updated to reflect actual argument parsing.)*

### Running `search.py` (Example):
*(This section will be updated once `search.py` is implemented.)*

```bash
# Example placeholder - actual arguments to be defined
# python ingest/search.py --query "rTMS Major Depressive Disorder" --since 2023-01-01 --out data/literature/YYYYMMDD_MDD_search.json
```

This README will be updated as the scripts are developed and refined.
