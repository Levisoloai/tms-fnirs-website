import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Adjust the import path according to your project structure
# This assumes your tests are in src/apge/tests and main.py is in src/apge
from src.apge.main import app, get_db

# Initialize TestClient
client = TestClient(app)

# Mock Neo4j record structure for convenience in tests
class MockNeo4jRecord:
    def __init__(self, data):
        self._data = data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __getitem__(self, key):
        return self._data[key]

    def data(self): # Added to mimic the .data() method used in list_protocols for direct dict conversion
        return self._data

# Test data to be returned by the mocked Neo4j session
MOCK_PROTOCOL_DATA_FULL = [
    MockNeo4jRecord({"id": "p1", "label": "Protocol Alpha", "device": "Device X", "evidence_level": "High"}),
    MockNeo4jRecord({"id": "p2", "label": "Protocol Beta", "device": "Device Y", "evidence_level": "Medium"}),
    MockNeo4jRecord({"id": "p3", "label": "Protocol Gamma", "device": "Device Z", "evidence_level": "Low"}),
]

MOCK_PROTOCOL_DATA_DEPRESSION = [
    MockNeo4jRecord({"id": "p1", "label": "Protocol Alpha MDD", "device": "Device X", "evidence_level": "High"}),
]

@pytest.fixture
def mock_db_session():
    mock_session = MagicMock()
    # The app's code iterates over the result of db.run(), so mock_session.run() should return an iterable
    mock_session.run.return_value = [] # Default to empty list
    return mock_session

def test_list_protocols_no_diagnosis(mock_db_session):
    mock_db_session.run.return_value = MOCK_PROTOCOL_DATA_FULL

    # Override the dependency
    app.dependency_overrides[get_db] = lambda: mock_db_session

    response = client.get("/api/protocol/list")

    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == len(MOCK_PROTOCOL_DATA_FULL)
    for item in response_data:
        assert "id" in item
        assert "label" in item
        assert "device" in item
        assert "evidence_level" in item

    # Check that the Cypher query was called without a diagnosis filter (simplistic check)
    call_args = mock_db_session.run.call_args[0] # Get positional arguments of the call
    query_string = call_args[0]
    params = call_args[1]

    assert "HAS_INDICATION" not in query_string.upper() # A bit fragile, but checks absence of diagnosis part
    assert "d:Diagnosis" not in query_string # More specific
    assert not params.get("diagnosis") # No diagnosis parameter passed

    # Clean up dependency override
    app.dependency_overrides = {}

def test_list_protocols_with_diagnosis(mock_db_session):
    mock_db_session.run.return_value = MOCK_PROTOCOL_DATA_DEPRESSION

    app.dependency_overrides[get_db] = lambda: mock_db_session

    diagnosis_query = "Depression"
    response = client.get(f"/api/protocol/list?diagnosis={diagnosis_query}")

    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == len(MOCK_PROTOCOL_DATA_DEPRESSION)
    assert response_data[0]["label"] == "Protocol Alpha MDD" # Check specific data if needed

    for item in response_data:
        assert "id" in item
        assert "label" in item
        assert "device" in item
        assert "evidence_level" in item

    # Check that the Cypher query was called with a diagnosis filter
    call_args = mock_db_session.run.call_args[0]
    query_string = call_args[0]
    params = call_args[1]

    assert "HAS_INDICATION" in query_string.upper() # Check for diagnosis part
    assert "d:Diagnosis" in query_string
    assert params.get("diagnosis") == diagnosis_query

    app.dependency_overrides = {}

# --- Mock data for compare_protocols endpoint ---
MOCK_PROTOCOL_DETAIL_P1 = MockNeo4jRecord({
    "protocol_id": "p1", "protocol_name": "Protocol Alpha",
    "frequency": "10 Hz", "intensity": 120.0, "pulses_per_session": 3000, "num_sessions": "20",
    "device_name": "Device X", "coil_type": "Figure-8", "manufacturer": "Mfg X",
    "evidence_level": "High", "publication_year": 2022, "reference_doi": "doi_p1"
})

MOCK_PROTOCOL_DETAIL_P2 = MockNeo4jRecord({
    "protocol_id": "p2", "protocol_name": "Protocol Beta",
    "frequency": "iTBS", "intensity": 110.0, "pulses_per_session": 1800, "num_sessions": "30",
    "device_name": "Device Y", "coil_type": "H-Coil", "manufacturer": "Mfg Y",
    "evidence_level": "Medium", "publication_year": 2021, "reference_doi": "doi_p2"
})

MOCK_PROTOCOL_DETAIL_P_INCOMPLETE = MockNeo4jRecord({ # For testing missing data
    "protocol_id": "p3_incomplete", "protocol_name": "Protocol Gamma Incomplete",
    "frequency": "1 Hz", "intensity": 100.0, "pulses_per_session": 600, "num_sessions": "10",
    "device_name": None, "coil_type": None, "manufacturer": None, # Missing device
    "evidence_level": "Low", "publication_year": 2020, "reference_doi": None # Missing ref
})

EXPECTED_COMPARE_COLUMNS = [
    "Protocol Name", "Coil Type", "Frequency", "Intensity",
    "Pulses/Session", "Sessions", "Evidence Level", "Device Name",
    "Manufacturer", "Publication Year", "Reference/DOI"
]

# --- Tests for POST /api/protocol/compare ---

def test_compare_protocols_valid_ids(mock_db_session):
    mock_db_session.run.return_value = [MOCK_PROTOCOL_DETAIL_P1, MOCK_PROTOCOL_DETAIL_P2]
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": ["p1", "p2"]}
    response = client.post("/api/protocol/compare", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "table" in data
    assert data["table"]["columns"] == EXPECTED_COMPARE_COLUMNS
    assert len(data["table"]["data"]) == 2

    # Check first row data consistency (example)
    assert data["table"]["data"][0][0] == MOCK_PROTOCOL_DETAIL_P1["protocol_name"] # Protocol Name
    assert data["table"]["data"][0][1] == MOCK_PROTOCOL_DETAIL_P1["coil_type"]     # Coil Type
    assert data["table"]["data"][0][3] == f"{MOCK_PROTOCOL_DETAIL_P1['intensity']}%" # Intensity formatting

    assert data["narrative_md"] == "LLM-generated narrative will be here in S-3."
    assert "lit_chunks" in data # Even if empty

    # Check that db.run was called with the correct parameters
    mock_db_session.run.assert_called_once_with(unittest.mock.ANY, ids=["p1", "p2"])

    app.dependency_overrides = {}

def test_compare_protocols_empty_id_list(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session # Not strictly needed as db call shouldn't happen

    payload = {"ids": []}
    response = client.post("/api/protocol/compare", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["table"]["columns"] == [] # As per current implementation for empty IDs
    assert data["table"]["data"] == []
    assert data["narrative_md"] == "No protocol IDs provided for comparison."

    mock_db_session.run.assert_not_called() # Ensure DB is not hit

    app.dependency_overrides = {}

def test_compare_protocols_non_existent_ids(mock_db_session):
    mock_db_session.run.return_value = [] # Simulate DB returning no data for these IDs
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": ["non_existent_id1", "non_existent_id2"]}
    response = client.post("/api/protocol/compare", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["table"]["columns"] == EXPECTED_COMPARE_COLUMNS
    assert len(data["table"]["data"]) == 0 # No data rows
    assert data["narrative_md"] == "LLM-generated narrative will be here in S-3."

    mock_db_session.run.assert_called_once_with(unittest.mock.ANY, ids=payload["ids"])

    app.dependency_overrides = {}

def test_compare_protocols_with_incomplete_data(mock_db_session):
    mock_db_session.run.return_value = [MOCK_PROTOCOL_DETAIL_P_INCOMPLETE]
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": ["p3_incomplete"]}
    response = client.post("/api/protocol/compare", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["table"]["columns"] == EXPECTED_COMPARE_COLUMNS
    assert len(data["table"]["data"]) == 1

    # Check that None values are handled correctly (example: device_name is index 7)
    assert data["table"]["data"][0][7] is None # Device Name should be None
    assert data["table"]["data"][0][1] is None # Coil Type
    assert data["table"]["data"][0][10] is None # Reference/DOI

    assert data["narrative_md"] == "LLM-generated narrative will be here in S-3."

    mock_db_session.run.assert_called_once_with(unittest.mock.ANY, ids=payload["ids"])

    app.dependency_overrides = {}

def test_list_protocols_empty_result(mock_db_session):
    mock_db_session.run.return_value = [] # Simulate no protocols found

    app.dependency_overrides[get_db] = lambda: mock_db_session

    response = client.get("/api/protocol/list")

    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 0

    app.dependency_overrides = {}

def test_list_protocols_with_diagnosis_no_match(mock_db_session):
    mock_db_session.run.return_value = [] # Simulate no protocols found for this diagnosis

    app.dependency_overrides[get_db] = lambda: mock_db_session

    diagnosis_query = "RareCondition"
    response = client.get(f"/api/protocol/list?diagnosis={diagnosis_query}")

    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 0

    call_args = mock_db_session.run.call_args[0]
    query_string = call_args[0]
    params = call_args[1]
    assert params.get("diagnosis") == diagnosis_query

    app.dependency_overrides = {}
