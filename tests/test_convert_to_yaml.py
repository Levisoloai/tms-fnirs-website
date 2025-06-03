import os
import sys
import tempfile
import shutil
import yaml
import pytest
from unittest import mock

# Add ingest directory to sys.path to allow direct import of convert_to_yaml
# This assumes 'tests/' and 'ingest/' are sibling directories.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ingest')))
try:
    import convert_to_yaml # Now we can import it
except ImportError:
    pytest.fail("Failed to import convert_to_yaml from ingest directory. Check sys.path setup.")

# Define paths relative to this test file
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
CSV_INPUT_FIXTURE = os.path.join(FIXTURE_DIR, 'sample_converter_input.csv')
TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ingest'))
TEMPLATE_NAME = "protocol_template.yaml.j2"

@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for YAML output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

def test_csv_to_yaml_conversion_valid_data(temp_output_dir):
    """Test round-trip conversion for valid CSV data."""
    assert os.path.exists(CSV_INPUT_FIXTURE), f"Fixture CSV not found: {CSV_INPUT_FIXTURE}"
    assert os.path.exists(os.path.join(TEMPLATE_DIR, TEMPLATE_NAME)), f"Template not found: {TEMPLATE_NAME}"

    # Run the conversion script's main function
    # We need to simulate command line arguments or call the core function directly
    # For simplicity, let's call the core function `convert_csv_to_yaml`
    success = convert_to_yaml.convert_csv_to_yaml(
        csv_filepath=CSV_INPUT_FIXTURE,
        template_dir=TEMPLATE_DIR,
        template_name=TEMPLATE_NAME,
        output_dir=temp_output_dir,
        dry_run=False
    )
    assert success, "convert_csv_to_yaml script function reported failure."

    # Check for expected output files
    expected_dep_yaml = os.path.join(temp_output_dir, "Depression.yaml")
    expected_anx_yaml = os.path.join(temp_output_dir, "Anxiety.yaml")

    assert os.path.exists(expected_dep_yaml), "Depression.yaml not generated."
    assert os.path.exists(expected_anx_yaml), "Anxiety.yaml not generated."

    # Load and validate content of Depression.yaml
    with open(expected_dep_yaml, 'r') as f:
        dep_data = yaml.safe_load(f)

    assert "Depression" in dep_data
    assert "Dep_Proto1" in dep_data["Depression"]
    assert "Dep_Proto2" in dep_data["Depression"]

    proto1 = dep_data["Depression"]["Dep_Proto1"]
    assert proto1["target"] == "L DLPFC"
    assert proto1["frequency_hz"] == 10 # Expecting int conversion
    assert proto1["intensity_pct_mt"] == 120 # Expecting int conversion
    assert proto1["pulses"] == 3000
    assert proto1["train_s"] == 4 # Expecting int conversion
    assert proto1["iti_s"] == 26 # Expecting int conversion
    assert proto1["evidence_level"] == "High"
    assert proto1["evidence_refs"] == ["Ref D1", "Ref D2"]

    proto2 = dep_data["Depression"]["Dep_Proto2"]
    assert proto2["frequency_hz"] == 50
    assert proto2["intensity_pct_amt"] == 80
    assert proto2["train_s"] == 0.19 # Expecting float
    assert proto2["iti_s"] is None # Blank in CSV, should be null

    # Load and validate content of Anxiety.yaml
    with open(expected_anx_yaml, 'r') as f:
        anx_data = yaml.safe_load(f)

    assert "Anxiety" in anx_data
    assert "Anx_Proto1" in anx_data["Anxiety"]
    anx_proto1 = anx_data["Anxiety"]["Anx_Proto1"]
    assert anx_proto1["target"] == "R DLPFC"
    assert anx_proto1["frequency_hz"] == 1
    assert anx_proto1["intensity_pct_mt"] == 110
    assert anx_proto1["iti_s"] == 0 # Blank in CSV, should be null for number, or 0 if parsed as 0? CSV has 0.
                                    # The current parse_nullable_float will make 0 into 0.0. format_for_yaml makes 0.0 into 0.
                                    # If CSV has '0', it should be 0. If blank, it should be 'null'.
                                    # The sample CSV has '0' for Anx_Proto1 iti_s.
    assert anx_proto1["evidence_level"] == "Emerging"
    assert anx_proto1["evidence_refs"] == ["Ref A1"]

# (Add more tests for convert_to_yaml, e.g., edge cases, invalid inputs, dry-run if desired)
