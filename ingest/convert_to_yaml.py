# ingest/convert_to_yaml.py

import argparse
import csv
import os
import re
import yaml # PyYAML for YAML dumping
from jinja2 import Environment, FileSystemLoader # Jinja2 for templating

# --- Helper Functions ---
def slugify_filename(text):
    """Convert text to a safe YAML filename (CamelCase, no special chars)."""
    text = text.replace('-', ' ').replace('_', ' ') # Treat hyphens/underscores as spaces
    # Capitalize first letter of each word
    text = "".join(word.capitalize() for word in text.split())
    text = re.sub(r'[^a-zA-Z0-9]', '', text) # Remove non-alphanumeric
    return text if text else "UnnamedDiagnosis"

def parse_nullable_float(value_str):
    """Convert string to float, or return None if empty/invalid."""
    if value_str and value_str.strip():
        try:
            return float(value_str.strip())
        except ValueError:
            return None # Or raise error, depending on strictness
    return None

def parse_frequency(value_str):
    """
    Return frequency as float if possible, otherwise as string.
    This is to handle cases like "10" vs "10 (L) / 1 (R)".
    In YAML, numbers should not be quoted, strings should.
    Jinja template will handle quoting based on type if needed,
    but easier to pass it ready.
    For YAML output, numerical floats should be numbers, strings quoted.
    """
    if not value_str: return None
    value_str = value_str.strip()
    try:
        return float(value_str)
    except ValueError:
        return value_str # Keep as string

def format_for_yaml(value):
    """Format value for YAML representation (numbers unquoted, null for None, strings quoted)."""
    if value is None:
        return 'null' # YAML null
    if isinstance(value, (int, float)):
        return str(value) # Return numbers as their string representation
    # For string values that need to be output as YAML strings (i.e., quoted if they contain special characters)
    # or as the literal 'null'.
    return yaml.dump(str(value), allow_unicode=True).strip() # .strip() to remove trailing newline from dump

# --- Main Conversion Logic ---
def convert_csv_to_yaml(csv_filepath, template_dir, template_name, output_dir):
    """
    Converts data from a CSV file to multiple YAML files, one per diagnosis,
    using a Jinja2 template.
    """
    if not os.path.exists(csv_filepath):
        print(f"Error: CSV file not found at {csv_filepath}")
        return

    # Initialize Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
    try:
        template = env.get_template(template_name)
    except Exception as e:
        print(f"Error loading Jinja2 template '{template_name}' from '{template_dir}': {e}")
        return

    # Group protocols by diagnosis
    diagnoses_data = {}

    try:
        with open(csv_filepath, mode='r', encoding='utf-8-sig') as csvfile: # utf-8-sig handles BOM
            reader = csv.DictReader(csvfile)
            if not reader.fieldnames:
                print(f"Error: CSV file {csv_filepath} is empty or has no header row.")
                return

            expected_cols = [
                'diagnosis', 'protocol_id', 'target', 'pattern', 'frequency_hz',
                'intensity_pct_mt', 'intensity_pct_amt', 'pulses', 'train_s', 'iti_s',
                'sessions', 'schedule', 'evidence_level', 'evidence_refs'
            ]
            missing_cols = [col for col in expected_cols if col not in reader.fieldnames]
            if missing_cols:
                print(f"Error: CSV missing expected columns: {', '.join(missing_cols)}")
                return

            for row_num, row in enumerate(reader, 1):
                diagnosis = row.get('diagnosis', '').strip()
                protocol_id = row.get('protocol_id', '').strip()

                if not diagnosis or not protocol_id:
                    print(f"Warning: Skipping row {row_num} due to missing diagnosis or protocol_id.")
                    continue

                if diagnosis not in diagnoses_data:
                    diagnoses_data[diagnosis] = {}

                intensity_mt = parse_nullable_float(row.get('intensity_pct_mt'))
                intensity_amt = parse_nullable_float(row.get('intensity_pct_amt'))

                protocol_details = {
                    'target': row.get('target', '').strip(),
                    'pattern': row.get('pattern', '').strip(),
                    'frequency_hz': parse_frequency(row.get('frequency_hz')),
                    'intensity_pct_mt': intensity_mt,
                    'intensity_pct_amt': intensity_amt,
                    'pulses': int(row.get('pulses', 0)) if row.get('pulses', '').strip() else 0,
                    'train_s': parse_nullable_float(row.get('train_s')),
                    'iti_s': parse_nullable_float(row.get('iti_s')),
                    'sessions': row.get('sessions', '').strip(),
                    'schedule': row.get('schedule', '').strip(),
                    'evidence_level': row.get('evidence_level', '').strip(),
                    'evidence_refs': [ref.strip() for ref in row.get('evidence_refs', '').split(';') if ref.strip()]
                }
                protocol_details['frequency_hz_yaml'] = format_for_yaml(protocol_details['frequency_hz'])
                protocol_details['train_s_yaml'] = format_for_yaml(protocol_details['train_s'])
                protocol_details['iti_s_yaml'] = format_for_yaml(protocol_details['iti_s'])

                if protocol_id in diagnoses_data[diagnosis]:
                    print(f"Warning: Duplicate protocol_id '{protocol_id}' for diagnosis '{diagnosis}'. Overwriting.")

                diagnoses_data[diagnosis][protocol_id] = protocol_details

    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_filepath}")
        return
    except Exception as e:
        print(f"Error reading or processing CSV file {csv_filepath}: {e}")
        return

    if not diagnoses_data:
        print("No data processed from CSV.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    for diagnosis_name, protocols in diagnoses_data.items():
        yaml_filename = f"{slugify_filename(diagnosis_name)}.yaml"
        yaml_filepath = os.path.join(output_dir, yaml_filename)

        context = {
            'diagnosis_name': diagnosis_name,
            'protocols': protocols
        }

        try:
            rendered_yaml_content = template.render(context)
            # For more robust YAML (especially with complex strings or types), parse and re-dump:
            # loaded_content = yaml.safe_load(rendered_yaml_content)
            # with open(yaml_filepath, 'w', encoding='utf-8') as f:
            #    yaml.dump(loaded_content, f, sort_keys=False, allow_unicode=True, indent=2, default_flow_style=False)
            # Sticking to direct template output for this version:
            with open(yaml_filepath, 'w', encoding='utf-8') as f:
                f.write(rendered_yaml_content)
            print(f"Successfully generated YAML for '{diagnosis_name}' at: {yaml_filepath}")
        except Exception as e:
            print(f"Error rendering or writing YAML for diagnosis '{diagnosis_name}': {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert curated CSV data to protocol YAML files.")
    parser.add_argument("--input", required=True, help="Path to the input CSV data file.")
    parser.add_argument("--output_dir", required=True, help="Directory to save the generated YAML files.")
    parser.add_argument("--template_dir", default="ingest/", help="Directory containing the Jinja2 template. Defaults to 'ingest/'.")
    parser.add_argument("--template_name", default="protocol_template.yaml.j2", help="Name of the Jinja2 template file. Defaults to 'protocol_template.yaml.j2'.")

    args = parser.parse_args()

    convert_csv_to_yaml(args.input, args.template_dir, args.template_name, args.output_dir)
