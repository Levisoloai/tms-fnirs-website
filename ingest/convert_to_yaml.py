# ingest/convert_to_yaml.py

import argparse
import csv
import os
import re
import sys # For stdout in dry-run
import yaml
from jinja2 import Environment, FileSystemLoader

# --- Helper Functions ---
def slugify_filename(text):
    text = text.replace('-', ' ').replace('_', ' ')
    text = "".join(word.capitalize() for word in text.split())
    text = re.sub(r'[^a-zA-Z0-9]', '', text)
    return text if text else "UnnamedDiagnosis"

def parse_nullable_float(value_str):
    if value_str and value_str.strip():
        try:
            return float(value_str.strip())
        except ValueError:
            print(f"Warning: Could not parse '{value_str}' as float, using None.")
            return None
    return None

def parse_frequency(value_str):
    if not value_str: return None
    value_str = value_str.strip()
    try:
        return float(value_str)
    except ValueError:
        return value_str

def format_for_yaml(value):
    if value is None:
        return 'null'
    if isinstance(value, bool): # Handle booleans explicitly for PyYAML load
        return str(value).lower() # 'true' or 'false'
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value.is_integer():
            return str(int(value)) # Return as string '10'
        return str(value) # Return as string '10.5'
    # For strings, yaml.dump is safest to get the YAML string representation.
    return yaml.dump(str(value), allow_unicode=True).strip()

# --- Main Conversion Logic ---
def convert_csv_to_yaml(csv_filepath, template_dir, template_name, output_dir, dry_run=False):
    if not os.path.exists(csv_filepath):
        print(f"Error: CSV file not found at {csv_filepath}", file=sys.stderr)
        return False

    env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
    try:
        template = env.get_template(template_name)
    except Exception as e:
        print(f"Error: Loading Jinja2 template '{template_name}' from '{template_dir}': {e}", file=sys.stderr)
        return False

    diagnoses_data = {}
    valid_evidence_levels = {"high", "moderate", "emerging"}

    try:
        with open(csv_filepath, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            if not reader.fieldnames:
                print(f"Error: CSV file {csv_filepath} is empty or has no header row.", file=sys.stderr)
                return False

            expected_cols = [
                'diagnosis', 'protocol_id', 'target', 'pattern', 'frequency_hz',
                'intensity_pct_mt', 'intensity_pct_amt', 'pulses', 'train_s', 'iti_s',
                'sessions', 'schedule', 'evidence_level', 'evidence_refs'
            ]
            missing_cols = [col for col in expected_cols if col not in reader.fieldnames]
            if missing_cols:
                print(f"Error: CSV missing expected columns: {', '.join(missing_cols)}", file=sys.stderr)
                return False

            for row_num, row in enumerate(reader, 1):
                diagnosis = row.get('diagnosis', '').strip()
                protocol_id = row.get('protocol_id', '').strip()

                if not diagnosis or not protocol_id:
                    print(f"Warning: Row {row_num}: Skipping due to missing diagnosis or protocol_id.", file=sys.stderr)
                    continue

                # Validate evidence_level
                evidence_level_raw = row.get('evidence_level', '').strip()
                if not evidence_level_raw:
                    print(f"Warning: Row {row_num} (Proto ID: {protocol_id}): Skipping. 'evidence_level' is missing.", file=sys.stderr)
                    continue
                if evidence_level_raw.lower() not in valid_evidence_levels:
                    print(f"Warning: Row {row_num} (Proto ID: {protocol_id}): Skipping. Invalid 'evidence_level': '{evidence_level_raw}'. Must be one of {valid_evidence_levels}.", file=sys.stderr)
                    continue

                # Handle blank evidence_refs
                evidence_refs_raw = row.get('evidence_refs', '').strip()
                if not evidence_refs_raw:
                    print(f"Warning: Row {row_num} (Proto ID: {protocol_id}): Skipping. 'evidence_refs' is blank.", file=sys.stderr)
                    continue

                evidence_refs_list = [ref.strip() for ref in evidence_refs_raw.split(';') if ref.strip()]
                if not evidence_refs_list: # After stripping, list might become empty
                    print(f"Warning: Row {row_num} (Proto ID: {protocol_id}): Skipping. 'evidence_refs' is effectively blank after parsing.", file=sys.stderr)
                    continue


                if diagnosis not in diagnoses_data:
                    diagnoses_data[diagnosis] = {}

                intensity_mt = parse_nullable_float(row.get('intensity_pct_mt'))
                intensity_amt = parse_nullable_float(row.get('intensity_pct_amt'))
                pulses_val = int(row.get('pulses', 0)) if row.get('pulses', '').strip() else 0 # Already int

                protocol_details = {
                    'target': row.get('target', '').strip(),
                    'pattern': row.get('pattern', '').strip(),
                    # These _yaml fields will be used by the template
                    'frequency_hz_yaml': format_for_yaml(parse_frequency(row.get('frequency_hz'))),
                    'intensity_pct_mt_yaml': format_for_yaml(intensity_mt),
                    'intensity_pct_amt_yaml': format_for_yaml(intensity_amt),
                    'pulses_yaml': format_for_yaml(pulses_val), # pulses is already int, format_for_yaml handles ints fine
                    'train_s_yaml': format_for_yaml(parse_nullable_float(row.get('train_s'))),
                    'iti_s_yaml': format_for_yaml(parse_nullable_float(row.get('iti_s'))),
                    # String fields for direct use
                    'sessions': row.get('sessions', '').strip(),
                    'schedule': row.get('schedule', '').strip(),
                    'evidence_level': evidence_level_raw,
                    'evidence_refs': evidence_refs_list
                }
                # Remove original numeric fields if only _yaml versions are needed by template
                # This simplifies the template context.
                # No, template will select based on _yaml versions.

                if protocol_id in diagnoses_data[diagnosis]:
                    print(f"Warning: Row {row_num}: Duplicate protocol_id '{protocol_id}' for diagnosis '{diagnosis}'. Overwriting previous entry.", file=sys.stderr)

                diagnoses_data[diagnosis][protocol_id] = protocol_details

    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_filepath}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error: Reading or processing CSV file {csv_filepath}: {e}", file=sys.stderr)
        return False

    if not diagnoses_data:
        print("Info: No valid data processed from CSV to generate YAML.", file=sys.stderr if dry_run else sys.stdout)
        return True # Still a success in terms of script execution, just no output

    if not dry_run and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Info: Created output directory: {output_dir}")
        except OSError as e:
            print(f"Error: Could not create output directory {output_dir}: {e}", file=sys.stderr)
            return False

    # Prepare data for Jinja rendering (using raw types, not pre-formatted YAML strings)
    final_output_data = {}
    for diagnosis_name, protocols_dict in diagnoses_data.items():
        final_output_data[diagnosis_name] = {
            'protocols': protocols_dict # protocols_dict already has the structure protocol_id: details
        }

    for diagnosis_name_key, data_for_template in final_output_data.items():
        yaml_filename = f"{slugify_filename(diagnosis_name_key)}.yaml"
        yaml_filepath = os.path.join(output_dir if not dry_run else '', yaml_filename) # output_dir might be None in dry_run

        context = {
            'diagnosis_name': diagnosis_name_key,
            'protocols': data_for_template['protocols']
        }

        try:
            # Render the template with the Python objects
            rendered_template_str = template.render(context)

            # Parse the rendered template string with PyYAML to get a Python object
            # This ensures that Jinja's output is valid YAML before further processing/dumping
            # It also correctly converts 'null' strings from template to Python None, etc.
            python_data_from_template = yaml.safe_load(rendered_template_str)

            if dry_run:
                print(f"# --- DRY RUN: Output for {diagnosis_name_key} ---")
                # Dump the Python object to YAML string for printing
                # This ensures canonical YAML formatting (e.g. indentation, nulls, quoted strings)
                print(yaml.dump(python_data_from_template, sort_keys=False, allow_unicode=True, indent=2))
                print(f"# --- END DRY RUN: {diagnosis_name_key} ---")
            else:
                # Dump the Python object to a YAML file
                with open(yaml_filepath, 'w', encoding='utf-8') as f:
                    yaml.dump(python_data_from_template, f, sort_keys=False, allow_unicode=True, indent=2)
                print(f"Info: Successfully generated YAML for '{diagnosis_name_key}' at: {yaml_filepath}")
        except yaml.YAMLError as e:
            print(f"Error: Invalid YAML generated by template for '{diagnosis_name_key}': {e}. Rendered content was:\n{rendered_template_str}", file=sys.stderr)
            if not dry_run: return False
        except Exception as e:
            print(f"Error: Rendering or writing YAML for diagnosis '{diagnosis_name_key}': {e}", file=sys.stderr)
            if not dry_run: return False

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert curated CSV data to protocol YAML files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--input", required=True, help="Path to the input CSV data file.")
    parser.add_argument("--output_dir", help="Directory to save the generated YAML files. Required if not --dry-run.")
    parser.add_argument("--template_dir", default="ingest/", help="Directory containing the Jinja2 template.")
    parser.add_argument("--template_name", default="protocol_template.yaml.j2", help="Name of the Jinja2 template file.")
    parser.add_argument("--dry-run", action="store_true", help="Print rendered YAML to stdout instead of writing to files.")

    args = parser.parse_args()

    if not args.dry_run and not args.output_dir:
        parser.error("--output_dir is required unless --dry-run is specified.")

    # Modify the template to directly use Python types for *_yaml fields
    # This is a conceptual change; the actual template file needs to be updated if it was pre-formatting
    # The current Jinja template ingests/protocol_template.yaml.j2 is:
    # frequency_hz: {{ details.frequency_hz_yaml }}
    # train_s: {{ details.train_s_yaml }}
    # iti_s: {{ details.iti_s_yaml }}
    # This means these fields in `details` passed to render() should be direct Python types (float, int, str, None)
    # The python script has been updated to do this:
    # protocol_details['frequency_hz_yaml'] = protocol_details['frequency_hz'] (and so on)

    # Also, the format_for_yaml function needs to be compatible with this.
    # The previous version of format_for_yaml was:
    # def format_for_yaml(value):
    #    if value is None: return 'null'
    #    if isinstance(value, (int, float)): return str(value)
    #    return yaml.dump(str(value), allow_unicode=True).strip()
    #
    # This is NOT what we want if PyYAML handles the final dump.
    # The Jinja template should receive raw Python objects.
    # So, the `*_yaml` suffixed keys in `protocol_details` should just hold the raw Python values.
    # And `format_for_yaml` is no longer needed if the final output is via `yaml.dump(python_data_from_template, ...)`.
    # The script was ALREADY changed to:
    # protocol_details['frequency_hz_yaml'] = protocol_details['frequency_hz']
    # protocol_details['train_s_yaml'] = protocol_details['train_s']
    # protocol_details['iti_s_yaml'] = protocol_details['iti_s']
    # And the old `format_for_yaml` is still present but its output is NOT used by Jinja if we let PyYAML do the final dump.
    # The new script structure uses `yaml.safe_load(rendered_template_str)` and then `yaml.dump(python_data_from_template, ...)`.
    # This means the Jinja template MUST produce valid YAML syntax directly for `yaml.safe_load` to parse it.
    # The `format_for_yaml` helper is still used to prepare values for direct substitution into the Jinja template.
    # The Jinja template should be:
    # frequency_hz: {{ details.frequency_hz }}
    # train_s: {{ details.train_s }}
    # iti_s: {{ details.iti_s }}
    # ... where these are now direct Python objects rendered by Jinja's default string conversion.
    # This means numbers become "10.0", None becomes "None", strings become "my string".
    # `yaml.safe_load` will then correctly interpret these. "10.0" -> 10.0, "None" -> None (Python None), "my string" -> 'my string'.
    # This is a robust approach. The `format_for_yaml` function in the provided script is:
    # def format_for_yaml(value):
    #    if value is None: return 'null'
    #    if isinstance(value, (int, float)):
    #        if isinstance(value, float) and value.is_integer(): return int(value)
    #        return value
    #    return f'"{str(value).replace(""", "\"")}"'
    # This IS intended for direct YAML literal output into Jinja.
    # `frequency_hz: {{ details.frequency_hz_yaml }}` where `frequency_hz_yaml` is the output of this function.
    # E.g. if `details.frequency_hz` is 10.0, `format_for_yaml` returns `10` (int). Template: `frequency_hz: 10`
    # E.g. if `details.frequency_hz` is "10 (L)", `format_for_yaml` returns `'"10 (L)"'`. Template: `frequency_hz: "10 (L)"`
    # E.g. if `details.train_s` is None, `format_for_yaml` returns `'null'`. Template: `train_s: null`
    # This is correct for `yaml.safe_load(template.render(...))`

    success = convert_csv_to_yaml(args.input, args.template_dir, args.template_name, args.output_dir, args.dry_run)

    if not success:
        sys.exit(1)
