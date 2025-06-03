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

# --- Additional imports for LLM and Redis tests ---
import os
import json
import hashlib
import redis # For redis.exceptions.RedisError
from unittest.mock import ANY # For asserting some arguments generally

# --- Tests for LLM and Redis Caching in POST /api/protocol/compare ---

# Helper to generate cache key consistently
def generate_expected_cache_key(ids: list[str]) -> str:
    sorted_ids = sorted(ids)
    ids_string = ",".join(sorted_ids)
    return f"narrative:{hashlib.md5(ids_string.encode('utf-8')).hexdigest()}"

@patch('src.apge.main.redis_client', new_callable=MagicMock)
@patch('src.apge.main.OpenAI')
@patch('src.apge.main.os.getenv') # To control OPENAI_API_KEY
def test_compare_llm_prompt_generation_and_success(mock_getenv, MockOpenAI, mock_redis, mock_db_session):
    # Setup: API Key is present, Cache miss, LLM success
    mock_getenv.return_value = "fake_openai_key" # Simulate API key is present
    mock_redis.get.return_value = None # Cache miss
    mock_llm_instance = MockOpenAI.return_value
    mock_llm_instance.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Test LLM narrative"))])

    mock_db_session.run.return_value = [MOCK_PROTOCOL_DETAIL_P1] # Provide some Neo4j data
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": ["p1"]}
    response = client.post("/api/protocol/compare", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["narrative_md"] == "Test LLM narrative"

    # Assert LLM call
    MockOpenAI.assert_called_once_with(api_key="fake_openai_key")
    mock_llm_instance.chat.completions.create.assert_called_once()
    call_args = mock_llm_instance.chat.completions.create.call_args
    messages = call_args.kwargs['messages']

    # Check system prompt
    assert "You are a neuro-psychiatry protocol analyst." in messages[0]['content']

    # Check user prompt for new fields
    user_prompt_json_str_start_index = messages[1]['content'].find('```json\n') + len('```json\n')
    user_prompt_json_str_end_index = messages[1]['content'].find('\n```', user_prompt_json_str_start_index)
    user_prompt_json_str = messages[1]['content'][user_prompt_json_str_start_index:user_prompt_json_str_end_index]

    user_prompt_data = json.loads(user_prompt_json_str)
    assert len(user_prompt_data) == 1 # Based on MOCK_PROTOCOL_DETAIL_P1
    assert user_prompt_data[0]['Protocol Name'] == MOCK_PROTOCOL_DETAIL_P1['protocol_name']
    assert user_prompt_data[0]['Publication Title'] == MOCK_PROTOCOL_DETAIL_P1['publication_title']
    assert user_prompt_data[0]['DOI'] == MOCK_PROTOCOL_DETAIL_P1['publication_doi']
    assert user_prompt_data[0]['Publication Year'] == MOCK_PROTOCOL_DETAIL_P1['publication_year']
    assert "literature abstracts" in messages[1]['content']

    # Assert caching behavior
    expected_key = generate_expected_cache_key(["p1"])
    mock_redis.get.assert_called_once_with(expected_key)
    mock_redis.set.assert_called_once_with(expected_key, "Test LLM narrative", ex=3600)

    app.dependency_overrides = {}

@patch('src.apge.main.redis_client', new_callable=MagicMock)
@patch('src.apge.main.OpenAI')
@patch('src.apge.main.os.getenv')
def test_compare_llm_api_error(mock_getenv, MockOpenAI, mock_redis, mock_db_session):
    mock_getenv.return_value = "fake_openai_key"
    mock_redis.get.return_value = None # Cache miss
    mock_llm_instance = MockOpenAI.return_value
    mock_llm_instance.chat.completions.create.side_effect = Exception("LLM API Down")

    mock_db_session.run.return_value = [MOCK_PROTOCOL_DETAIL_P1]
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": ["p1"]}
    response = client.post("/api/protocol/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["narrative_md"] == "Error generating narrative. Please try again later."
    mock_redis.set.assert_not_called() # Error narrative should not be cached
    app.dependency_overrides = {}

@patch('src.apge.main.redis_client', new_callable=MagicMock)
@patch('src.apge.main.OpenAI')
@patch('src.apge.main.os.getenv')
def test_compare_missing_openai_key(mock_getenv, MockOpenAI, mock_redis, mock_db_session):
    mock_getenv.return_value = None # Simulate API key is MISSING
    mock_redis.get.return_value = None # Cache miss
    mock_llm_instance = MockOpenAI.return_value

    mock_db_session.run.return_value = [MOCK_PROTOCOL_DETAIL_P1]
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": ["p1"]}
    response = client.post("/api/protocol/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["narrative_md"] == "Narrative generation is currently unavailable (API key not configured)."
    mock_llm_instance.chat.completions.create.assert_not_called()
    mock_redis.set.assert_not_called() # This specific error narrative should not be cached
    app.dependency_overrides = {}

@patch('src.apge.main.redis_client', new_callable=MagicMock)
@patch('src.apge.main.OpenAI') # Still need to mock OpenAI though it shouldn't be called
@patch('src.apge.main.os.getenv')
def test_compare_cache_hit(mock_getenv, MockOpenAI, mock_redis, mock_db_session):
    mock_getenv.return_value = "fake_openai_key" # API key available but shouldn't be used
    cached_narrative_content = "Cached test narrative"
    mock_redis.get.return_value = cached_narrative_content # Cache HIT
    mock_llm_instance = MockOpenAI.return_value

    mock_db_session.run.return_value = [MOCK_PROTOCOL_DETAIL_P1] # Neo4j still called for table data
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": ["p1"]}
    response = client.post("/api/protocol/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["narrative_md"] == cached_narrative_content
    expected_key = generate_expected_cache_key(["p1"])
    mock_redis.get.assert_called_once_with(expected_key)
    mock_llm_instance.chat.completions.create.assert_not_called()
    mock_redis.set.assert_not_called()
    app.dependency_overrides = {}

@patch('src.apge.main.redis_client', new_callable=MagicMock)
@patch('src.apge.main.OpenAI')
@patch('src.apge.main.os.getenv')
def test_compare_redis_get_failure(mock_getenv, MockOpenAI, mock_redis, mock_db_session):
    mock_getenv.return_value = "fake_openai_key"
    mock_redis.get.side_effect = redis.exceptions.RedisError("Redis GET failed")
    mock_llm_instance = MockOpenAI.return_value
    mock_llm_instance.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Fresh narrative after Redis GET fail"))])

    mock_db_session.run.return_value = [MOCK_PROTOCOL_DETAIL_P1]
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": ["p1"]}
    response = client.post("/api/protocol/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["narrative_md"] == "Fresh narrative after Redis GET fail"
    mock_llm_instance.chat.completions.create.assert_called_once() # Fallback to LLM
    expected_key = generate_expected_cache_key(["p1"])
    mock_redis.set.assert_called_once_with(expected_key, "Fresh narrative after Redis GET fail", ex=3600) # Attempt to cache new
    app.dependency_overrides = {}

@patch('src.apge.main.redis_client', new_callable=MagicMock)
@patch('src.apge.main.OpenAI')
@patch('src.apge.main.os.getenv')
def test_compare_redis_set_failure(mock_getenv, MockOpenAI, mock_redis, mock_db_session):
    mock_getenv.return_value = "fake_openai_key"
    mock_redis.get.return_value = None # Cache miss
    mock_redis.set.side_effect = redis.exceptions.RedisError("Redis SET failed")
    mock_llm_instance = MockOpenAI.return_value
    llm_generated_narrative = "Fresh narrative, Redis SET will fail"
    mock_llm_instance.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content=llm_generated_narrative))])

    mock_db_session.run.return_value = [MOCK_PROTOCOL_DETAIL_P1]
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": ["p1"]}
    response = client.post("/api/protocol/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["narrative_md"] == llm_generated_narrative # User gets narrative despite cache SET fail
    mock_llm_instance.chat.completions.create.assert_called_once()
    expected_key = generate_expected_cache_key(["p1"])
    mock_redis.set.assert_called_once_with(expected_key, llm_generated_narrative, ex=3600)
    app.dependency_overrides = {}

@patch('src.apge.main.redis_client', new_callable=MagicMock)
@patch('src.apge.main.OpenAI')
@patch('src.apge.main.os.getenv')
def test_compare_caching_skipped_for_error_narratives(mock_getenv, MockOpenAI, mock_redis, mock_db_session):
    mock_getenv.return_value = "fake_openai_key"
    mock_redis.get.return_value = None # Cache miss

    mock_llm_instance = MockOpenAI.return_value
    error_narratives_to_test = [
        "Error generating narrative. Please try again later.",
        "Narrative generation is currently unavailable (API key not configured).",
        "No protocol data found to generate a comparison narrative."
    ]

    mock_db_session.run.return_value = [MOCK_PROTOCOL_DETAIL_P1] # Needed to reach LLM call
    app.dependency_overrides[get_db] = lambda: mock_db_session

    for error_narrative in error_narratives_to_test:
        mock_llm_instance.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content=error_narrative))])
        # Reset set mock for each iteration if it's stateful across calls (though it shouldn't be here)
        mock_redis.reset_mock() # Reset all redis mocks (get, set)
        mock_redis.get.return_value = None # Ensure cache miss for each iteration

        payload = {"ids": ["p1"]} # Use a consistent payload
        response = client.post("/api/protocol/compare", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["narrative_md"] == error_narrative

        mock_llm_instance.chat.completions.create.assert_called() # LLM was called
        mock_redis.set.assert_not_called() # Crucial: error narrative was NOT cached
        mock_llm_instance.chat.completions.create.reset_mock() # Reset for next iteration

    app.dependency_overrides = {}

@patch('src.apge.main.redis_client', new_callable=MagicMock)
@patch('src.apge.main.OpenAI')
@patch('src.apge.main.os.getenv')
def test_compare_no_protocol_data_no_llm_call_no_caching(mock_getenv, MockOpenAI, mock_redis, mock_db_session):
    mock_getenv.return_value = "fake_openai_key" # API key available
    mock_redis.get.return_value = None # Cache miss
    mock_llm_instance = MockOpenAI.return_value

    mock_db_session.run.return_value = [] # Simulate Neo4j returning NO protocol data
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": ["p1", "p2"]} # IDs that yield no data
    response = client.post("/api/protocol/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["narrative_md"] == "No protocol data found to generate a comparison narrative."
    mock_llm_instance.chat.completions.create.assert_not_called() # LLM not called if no protocol data
    mock_redis.set.assert_not_called() # Nothing to cache

    # GET should still be called to check cache first
    expected_key = generate_expected_cache_key(["p1", "p2"])
    mock_redis.get.assert_called_once_with(expected_key)

    app.dependency_overrides = {}

# --- Mock data for compare_protocols endpoint ---
MOCK_PROTOCOL_DETAIL_P1 = MockNeo4jRecord({
    "protocol_id": "p1", "protocol_name": "Protocol Alpha",
    "frequency": "10 Hz", "intensity": 120.0, "pulses_per_session": 3000, "num_sessions": "20",
    "device_name": "Device X", "coil_type": "Figure-8", "manufacturer": "Mfg X",
    "evidence_level": "High",
    "publication_title": "Efficacy of Alpha Protocol", "publication_year": 2022, "publication_doi": "10.1234/alpha.2022"
})

MOCK_PROTOCOL_DETAIL_P2 = MockNeo4jRecord({
    "protocol_id": "p2", "protocol_name": "Protocol Beta",
    "frequency": "iTBS", "intensity": 110.0, "pulses_per_session": 1800, "num_sessions": "30",
    "device_name": "Device Y", "coil_type": "H-Coil", "manufacturer": "Mfg Y",
    "evidence_level": "Medium",
    "publication_title": "Beta Protocol for TRD", "publication_year": 2021, "publication_doi": "10.5678/beta.2021"
})

MOCK_PROTOCOL_DETAIL_P_INCOMPLETE = MockNeo4jRecord({ # For testing missing data
    "protocol_id": "p3_incomplete", "protocol_name": "Protocol Gamma Incomplete",
    "frequency": "1 Hz", "intensity": 100.0, "pulses_per_session": 600, "num_sessions": "10",
    "device_name": None, "coil_type": None, "manufacturer": None, # Missing device
    "evidence_level": "Low",
    "publication_title": None, "publication_year": 2020, "publication_doi": None # Missing title and DOI
})

EXPECTED_COMPARE_COLUMNS = [
    "Protocol Name", "Coil Type", "Frequency", "Intensity",
    "Pulses/Session", "Sessions", "Evidence Level", "Device Name",
    "Manufacturer", "Publication Title", "Publication Year", "DOI"
]

# --- Tests for POST /api/protocol/compare ---

# This test now implicitly tests the old "LLM-generated narrative will be here in S-3"
# because the LLM tests are separate. We focus on table structure here.
@patch('src.apge.main.redis_client', new_callable=MagicMock) # Mock redis to prevent actual calls
@patch('src.apge.main.OpenAI') # Mock OpenAI to prevent actual calls
@patch('src.apge.main.os.getenv')
def test_compare_protocols_table_structure_valid_ids(mock_getenv, MockOpenAI, mock_redis, mock_db_session):
    # Simulate that LLM/Redis part works but returns a known placeholder for this specific test
    mock_getenv.return_value = "fake_key_for_table_test"
    mock_redis.get.return_value = None # Cache miss
    mock_llm_instance = MockOpenAI.return_value
    mock_llm_instance.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Narrative for table test"))])

    mock_db_session.run.return_value = [MOCK_PROTOCOL_DETAIL_P1, MOCK_PROTOCOL_DETAIL_P2]
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": ["p1", "p2"]}
    response = client.post("/api/protocol/compare", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "table" in data
    assert data["table"]["columns"] == EXPECTED_COMPARE_COLUMNS
    assert len(data["table"]["data"]) == 2

    # Check first row data consistency for new fields
    row1_data = dict(zip(data["table"]["columns"], data["table"]["data"][0]))
    assert row1_data["Protocol Name"] == MOCK_PROTOCOL_DETAIL_P1["protocol_name"]
    assert row1_data["Coil Type"] == MOCK_PROTOCOL_DETAIL_P1["coil_type"]
    assert row1_data["Intensity"] == f"{MOCK_PROTOCOL_DETAIL_P1['intensity']}%"
    assert row1_data["Publication Title"] == MOCK_PROTOCOL_DETAIL_P1["publication_title"]
    assert row1_data["Publication Year"] == MOCK_PROTOCOL_DETAIL_P1["publication_year"]
    assert row1_data["DOI"] == MOCK_PROTOCOL_DETAIL_P1["publication_doi"]

    # Check second row data consistency for new fields
    row2_data = dict(zip(data["table"]["columns"], data["table"]["data"][1]))
    assert row2_data["Protocol Name"] == MOCK_PROTOCOL_DETAIL_P2["protocol_name"]
    assert row2_data["Publication Title"] == MOCK_PROTOCOL_DETAIL_P2["publication_title"]
    assert row2_data["DOI"] == MOCK_PROTOCOL_DETAIL_P2["publication_doi"]

    assert data["narrative_md"] == "Narrative for table test" # From mock LLM for this test
    assert "lit_chunks" in data

    mock_db_session.run.assert_called_once_with(ANY, ids=["p1", "p2"])

    app.dependency_overrides = {}

@patch('src.apge.main.os.getenv') # Keep mocks for other tests that don't focus on table structure
@patch('src.apge.main.OpenAI')
@patch('src.apge.main.redis_client')
def test_compare_protocols_empty_id_list(mock_redis, MockOpenAI, mock_getenv, mock_db_session):
    # No need to mock getenv, OpenAI, redis_client here as the function should return early
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": []}
    response = client.post("/api/protocol/compare", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["table"]["columns"] == []
    assert data["table"]["data"] == []
    assert data["narrative_md"] == "No protocol IDs provided for comparison."

    mock_db_session.run.assert_not_called()

    app.dependency_overrides = {}

@patch('src.apge.main.os.getenv')
@patch('src.apge.main.OpenAI')
@patch('src.apge.main.redis_client')
def test_compare_protocols_non_existent_ids(mock_redis, MockOpenAI, mock_getenv, mock_db_session):
    mock_getenv.return_value = "fake_key_for_table_test"
    mock_redis.get.return_value = None
    mock_llm_instance = MockOpenAI.return_value
    # LLM will be called but with empty protocol list, so it should return "No protocol data found..."
    # Or, if the main function checks `protocols_json_list` before calling LLM, it will return that directly.
    # The current main.py logic has: `elif not protocols_json_list: narrative_to_return = "No protocol data found..."`
    # So, OpenAI().chat.completions.create won't actually be called if db.run returns empty.

    mock_db_session.run.return_value = []
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {"ids": ["non_existent_id1", "non_existent_id2"]}
    response = client.post("/api/protocol/compare", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["table"]["columns"] == EXPECTED_COMPARE_COLUMNS
    assert len(data["table"]["data"]) == 0
    assert data["narrative_md"] == "No protocol data found to generate a comparison narrative."

    mock_db_session.run.assert_called_once_with(ANY, ids=payload["ids"])
    MockOpenAI.assert_not_called() # Check that OpenAI client wasn't even instantiated if not needed or create not called
    mock_llm_instance.chat.completions.create.assert_not_called()


    app.dependency_overrides = {}

@patch('src.apge.main.os.getenv')
@patch('src.apge.main.OpenAI')
@patch('src.apge.main.redis_client')
def test_compare_protocols_with_incomplete_data(mock_redis, MockOpenAI, mock_getenv, mock_db_session):
    mock_getenv.return_value = "fake_key_for_table_test"
    mock_redis.get.return_value = None
    mock_llm_instance = MockOpenAI.return_value
    mock_llm_instance.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Narrative for incomplete data test"))])

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
