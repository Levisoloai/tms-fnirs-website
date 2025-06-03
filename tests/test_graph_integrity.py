# tests/test_graph_integrity.py

import yaml
import os
import pytest

# Define the path to the YAML file relative to this test file
# Assuming 'tests/' and 'ingest/' are sibling directories at the project root
PROTOCOLS_YAML_PATH = os.path.join(
    os.path.dirname(__file__), # Current directory (tests/)
    '..',                     # Project root
    'ingest',                 # ingest/
    'protocols',              # protocols/
    'psychiatry.yaml'         # psychiatry.yaml
)

def load_protocols(yaml_path):
    """Loads YAML data from the given path."""
    if not os.path.exists(yaml_path):
        pytest.fail(f"YAML file not found at {yaml_path}")
    with open(yaml_path, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Error parsing YAML file: {e}")

def test_evidence_refs_not_empty():
    """
    Test that every protocol entry has at least one citation string
    in its evidence_refs.
    """
    data = load_protocols(PROTOCOLS_YAML_PATH)

    assert data is not None, "No data loaded from YAML file."
    assert isinstance(data, dict), "YAML content should be a dictionary (diagnoses)."

    if not data:
        # If the YAML is empty (but valid), this test could technically pass.
        # Depending on requirements, one might want to fail if there are no diagnoses.
        # For now, an empty file means no protocols to check, so no failures.
        return

    for diagnosis, protocols in data.items():
        assert isinstance(protocols, dict), \
            f"Protocols for diagnosis '{diagnosis}' should be a dictionary."

        if not protocols: # No protocols for this diagnosis
            continue

        for protocol_id, details in protocols.items():
            assert isinstance(details, dict), \
                f"Details for protocol '{diagnosis}/{protocol_id}' should be a dictionary."

            # Check for 'evidence_refs' key
            assert 'evidence_refs' in details, \
                f"'evidence_refs' missing in protocol '{diagnosis}/{protocol_id}'."

            evidence_refs = details['evidence_refs']

            # Check that evidence_refs is a list
            assert isinstance(evidence_refs, list), \
                f"'evidence_refs' in '{diagnosis}/{protocol_id}' should be a list, found {type(evidence_refs).__name__}."

            # Check that evidence_refs is not empty
            assert len(evidence_refs) > 0, \
                f"'evidence_refs' list is empty in protocol '{diagnosis}/{protocol_id}'."

            # Check that all references in evidence_refs are non-empty strings
            for i, ref in enumerate(evidence_refs):
                assert isinstance(ref, str), \
                    f"Reference #{i+1} in 'evidence_refs' for '{diagnosis}/{protocol_id}' is not a string (found {type(ref).__name__})."
                assert len(ref.strip()) > 0, \
                    f"Reference #{i+1} in 'evidence_refs' for '{diagnosis}/{protocol_id}' is an empty or whitespace-only string."

# Example of how to run this test with pytest:
# Ensure PyYAML is installed: pip install PyYAML pytest
# Then run: pytest tests/test_graph_integrity.py
