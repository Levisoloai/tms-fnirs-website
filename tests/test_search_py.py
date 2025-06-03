import os
import sys
import json
import tempfile
import pytest
import requests # For requests.exceptions.RequestException
from unittest import mock

# Add ingest directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ingest')))
try:
    import search as search_script
except ImportError:
    pytest.fail("Failed to import search from ingest directory. Check sys.path setup.")

@pytest.fixture
def temp_output_file():
    """Create a temporary file path for JSON output."""
    # Using NamedTemporaryFile to ensure it's a file that search_script can write to
    # and we can read from. delete=False is important for Windows compatibility
    # where a file cannot be opened by another process if it's already open.
    tf = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    filepath = tf.name
    tf.close() # Close it so search_script can open and write to it
    yield filepath
    os.remove(filepath) # Clean up the file afterwards


# Mock data for API responses
MOCK_API_ITEM_1 = {'title': ['Test Title 1'], 'DOI': '10.123/test1', 'author': [{'given': 'J', 'family': 'Doe'}],
                   'issued': {'date-parts': [[2023]]}, 'abstract': 'Abstract 1'}
MOCK_API_ITEM_2 = {'title': ['Test Title 2'], 'DOI': '10.123/test2', 'author': [{'given': 'A', 'family': 'Smith'}],
                   'issued': {'date-parts': [[2024]]}, 'abstract': 'Abstract 2'}

MOCK_API_RESPONSE_PAGE1 = {'message': {'total-results': 2, 'items': [MOCK_API_ITEM_1, MOCK_API_ITEM_2]}}
MOCK_API_RESPONSE_EMPTY = {'message': {'total-results': 0, 'items': []}}


@mock.patch('search.call_crossref_api') # Target the function in the imported search_script module
def test_search_bibliographic_query(mock_call_api, temp_output_file):
    """Test with general bibliographic query."""
    mock_call_api.return_value = MOCK_API_RESPONSE_PAGE1

    # Call the main function that search.py's __main__ block would call,
    # or simulate argparse if necessary. Here, directly calling the core logic.
    # Note: search_crossref_paginated is the core logic function.
    # The __main__ block in search.py parses args and then calls this.
    # We are testing the core logic, not argparse parsing here.

    search_script.search_crossref_paginated(
        query_bibliographic="test query",
        max_results=2,
        # out_filepath=temp_output_file # search_crossref_paginated doesn't handle file writing
    )

    # Check that call_crossref_api was called with 'query.bibliographic'
    args, kwargs = mock_call_api.call_args
    assert 'query.bibliographic' in args[0]
    assert args[0]['query.bibliographic'] == "test query"
    assert 'query.title' not in args[0]


@mock.patch('search.call_crossref_api')
def test_search_title_query(mock_call_api, temp_output_file):
    """Test with title-specific query."""
    mock_call_api.return_value = MOCK_API_RESPONSE_PAGE1

    search_script.search_crossref_paginated(
        query_title="test title query",
        max_results=2
    )

    args, kwargs = mock_call_api.call_args
    assert 'query.title' in args[0]
    assert args[0]['query.title'] == "test title query"
    assert 'query.bibliographic' not in args[0]


@mock.patch('search.call_crossref_api')
def test_search_date_filters(mock_call_api, temp_output_file):
    """Test with since and until date filters."""
    mock_call_api.return_value = MOCK_API_RESPONSE_EMPTY # Content doesn't matter, just params

    search_script.search_crossref_paginated(
        query_bibliographic="date test",
        since_date_str="2021-01-01",
        until_date_str="2022-12-31",
        max_results=10
    )

    args, kwargs = mock_call_api.call_args
    assert 'filter' in args[0]
    assert "from-pub-date:2021-01-01" in args[0]['filter']
    assert "until-pub-date:2022-12-31" in args[0]['filter']

@mock.patch('search.call_crossref_api')
def test_search_since_only_filter(mock_call_api, temp_output_file):
    """Test with only since date filter."""
    mock_call_api.return_value = MOCK_API_RESPONSE_EMPTY

    search_script.search_crossref_paginated(
        query_bibliographic="since test",
        since_date_str="2023-03-15",
        max_results=5
    )

    args, kwargs = mock_call_api.call_args
    assert 'filter' in args[0]
    assert "from-pub-date:2023-03-15" in args[0]['filter']
    assert "until-pub-date" not in args[0]['filter']


@mock.patch('search.call_crossref_api')
def test_search_until_only_filter(mock_call_api, temp_output_file):
    """Test with only until date filter."""
    mock_call_api.return_value = MOCK_API_RESPONSE_EMPTY

    search_script.search_crossref_paginated(
        query_bibliographic="until test",
        until_date_str="2020-06-30",
        max_results=5
    )

    args, kwargs = mock_call_api.call_args
    assert 'filter' in args[0]
    assert "until-pub-date:2020-06-30" in args[0]['filter']
    assert "from-pub-date" not in args[0]['filter']


@mock.patch('search.call_crossref_api')
def test_search_script_api_error_still_works(mock_call_api, temp_output_file): # Renamed from previous plan
    """Test search.py handling of API errors (ensure this existing test logic is sound)."""
    mock_call_api.side_effect = requests.exceptions.RequestException("Simulated API error")

    results, total_api_hits, final_kept_hits = search_script.search_crossref_paginated(
        query_bibliographic="error query", # Must provide a query
        max_results=10
    )
    assert results == []
    assert total_api_hits == 0
    assert final_kept_hits == 0


# It's harder to test the full __main__ block of search.py without more complex subprocess mocking.
# These tests focus on the core `search_crossref_paginated` function which contains the main logic.
# The test_search_script_success from previous version was trying to test the main block,
# which is less direct. Testing the core function is more standard for unit tests.

# To test file output, we'd need to call the __main__ part or replicate its file writing.
# For simplicity, these tests confirm the correct parameters are passed to the API call,
# which is the most critical part of the new functionality.
# The actual parsing of results and structure of collected_items was implicitly tested before.
