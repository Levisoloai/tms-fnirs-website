import os
import sys
import json
import tempfile
import pytest
import requests # <--- ADD THIS
from unittest import mock

# Add ingest directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ingest')))
try:
    import search as search_script # search is a common module name, alias to avoid conflict
except ImportError:
    pytest.fail("Failed to import search from ingest directory. Check sys.path setup.")

@pytest.fixture
def temp_output_file():
    """Create a temporary file path for JSON output."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmpfile:
        filepath = tmpfile.name
    yield filepath
    os.remove(filepath) # Clean up the file afterwards

@mock.patch('search.call_crossref_api') # Target the function making the actual HTTP call
def test_search_script_success(mock_call_api, temp_output_file):
    """Test search.py successful execution with mocked API data."""

    # Mock API response for multiple pages if pagination is tested, or single page
    mock_page1_items = [
        {'title': ['Test Title 1'], 'DOI': '10.123/test1', 'author': [{'given': 'J', 'family': 'Doe'}],
         'issued': {'date-parts': [[2023]]}, 'abstract': 'Abstract 1'},
        {'title': ['Test Title 2'], 'DOI': '10.123/test2', 'author': [{'given': 'A', 'family': 'Smith'}],
         'issued': {'date-parts': [[2024]]}, 'abstract': 'Abstract 2'},
    ]
    mock_api_response_page1 = {'message': {'total-results': 2, 'items': mock_page1_items}}

    # For this test, assume only one page is fetched or pagination works as expected
    mock_call_api.return_value = mock_api_response_page1

    # Simulate command-line arguments for search_script's main execution
    test_args = [
        'ingest/search.py', # Script name, usually first arg
        '--query', 'test query',
        '--max-results', '2',
        '--out', temp_output_file
    ]

    with mock.patch.object(sys, 'argv', test_args):
        try:
            # search_script.main() # If main is defined and callable
            # Or more directly, if __name__ == "__main__": block calls a main function:
            # For this structure, we might need to refactor search.py to have a main()
            # or call its core logic if __name__ == '__main__' is complex to invoke directly.
            # Let's assume search.py can be run by simulating sys.argv and then exec-ing its content
            # or by calling a defined main function.
            # For now, let's test the core paginated search function directly as it's easier.

            results, total_api_hits, final_kept_hits = search_script.search_crossref_paginated(
                query="test query",
                max_results=2
            )
            # Save results manually for this direct test
            with open(temp_output_file, 'w') as f:
                json.dump(results, f, indent=4)

        except SystemExit as e:
            # If argparse calls sys.exit(), catch it.
            assert e.code == 0, "Search script exited with an error code."
        except Exception as e:
            pytest.fail(f"search_script main logic raised an exception: {e}")

    assert mock_call_api.called # Check if the API call function was actually called

    # Verify the content of the output JSON file
    assert os.path.exists(temp_output_file)
    with open(temp_output_file, 'r') as f:
        output_data = json.load(f)

    assert len(output_data) == 2
    assert output_data[0]['title'] == 'Test Title 1'
    assert output_data[0]['doi'] == '10.123/test1'
    assert output_data[0]['authors'] == ['J Doe']
    assert output_data[0]['year'] == 2023
    assert output_data[0]['abstract'] == 'Abstract 1'

    assert output_data[1]['title'] == 'Test Title 2'

@mock.patch('search.call_crossref_api')
def test_search_script_api_error(mock_call_api, temp_output_file):
    """Test search.py handling of API errors."""
    mock_call_api.side_effect = requests.exceptions.RequestException("Simulated API error")

    results, total_api_hits, final_kept_hits = search_script.search_crossref_paginated(
        query="error query",
        max_results=10
    )
    # In case of error, search_crossref_paginated should return empty list
    assert results == []
    assert total_api_hits == 0
    assert final_kept_hits == 0
    # (Further checks could be on stderr logs if the script prints errors there)

# (Add more tests for search.py, e.g., date filtering, pagination details, no results)
