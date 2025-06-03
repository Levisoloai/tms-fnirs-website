# ingest/search.py

import argparse
import datetime
import json
import os
import requests
import re
import time # For simple backoff if tenacity is not used, or by tenacity
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type # For retry logic

# --- Configuration ---
CROSSREF_API_URL = "https://api.crossref.org/works"
POLITE_EMAIL = "user@example.com" # Replace with a real or generic email

# --- Helper Functions ---
def slugify(text):
    text = text.lower()
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[^\w-]', '', text)
    return text

def ensure_dir_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Info: Created directory: {directory_path}")

def format_date_for_crossref(date_str):
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return str(dt)
    except ValueError:
        print(f"Error: Date '{date_str}' is not in YYYY-MM-DD format.")
        return None

# --- Main Search Function ---
@retry(
    stop=stop_after_attempt(3), # Retry up to 3 times
    wait=wait_exponential(multiplier=1, min=2, max=10), # Exponential backoff: 2s, 4s, 8s
    retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.HTTPError)), # Retry on network errors or HTTP 5xx/4xx
    reraise=True # Reraise the exception if all retries fail
)
def call_crossref_api(params, headers):
    """Makes a single, retriable call to the CrossRef API."""
    response = requests.get(CROSSREF_API_URL, params=params, headers=headers, timeout=20)
    response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)
    return response.json()

def search_crossref_paginated(query, since_date_str=None, max_results=100, results_per_page=100):
    """
    Searches CrossRef API for literature with pagination.

    Args:
        query (str): The search query.
        since_date_str (str, optional): Start date for filtering (YYYY-MM-DD).
        max_results (int): Maximum number of results to fetch.
        results_per_page (int): Number of results per API request page (CrossRef max is 1000, typically use 20-100).

    Returns:
        list: A list of dictionaries, each representing a found article.
        (int, int): total_hits_api, total_hits_after_filter
    """

    headers = {
        'User-Agent': f"NeuroStream Ingest Agent/1.1 ({POLITE_EMAIL})", # Updated agent version
        'mailto': POLITE_EMAIL
    }

    base_params = {
        'query.bibliographic': query,
        'rows': min(results_per_page, max_results), # Request per page, up to max_results
    }

    filter_parts = []
    if since_date_str:
        formatted_date = format_date_for_crossref(since_date_str)
        if not formatted_date:
            return [], 0, 0 # Invalid date format
        filter_parts.append(f"from-pub-date:{formatted_date}")

    if filter_parts:
        base_params['filter'] = ",".join(filter_parts)

    collected_items = []
    current_offset = 0
    total_hits_api = 0 # Total results reported by API for the query (can be very large)
    initial_call_done = False

    print(f"Info: Querying CrossRef API for '{query}', Since: {since_date_str or 'Any date'}, Max results: {max_results}")

    while len(collected_items) < max_results:
        paginated_params = base_params.copy()
        paginated_params['offset'] = current_offset
        # Adjust 'rows' for the last page if max_results is not a multiple of results_per_page
        paginated_params['rows'] = min(results_per_page, max_results - len(collected_items))

        if paginated_params['rows'] <= 0: # Should not happen if logic is correct
            break

        print(f"Info: Fetching page: offset {current_offset}, rows {paginated_params['rows']}")

        try:
            data = call_crossref_api(paginated_params, headers)
            items = data.get('message', {}).get('items', [])

            if not initial_call_done:
                total_hits_api = data.get('message', {}).get('total-results', 0)
                initial_call_done = True

            if not items:
                print("Info: No more results found on this page or query exhausted.")
                break # No more items to fetch

            for item in items:
                if len(collected_items) >= max_results:
                    break # Reached max_results limit

                title = item.get('title', [""])[0]
                doi = item.get('DOI', '')

                authors_list = []
                if 'author' in item:
                    for author in item.get('author', []):
                        name_parts = [part for part in [author.get('given'), author.get('family')] if part]
                        if name_parts: authors_list.append(" ".join(name_parts))

                pub_date_parts = item.get('issued', {}).get('date-parts', [[None]])[0]
                year = pub_date_parts[0] if pub_date_parts[0] else "N/A"

                abstract = item.get('abstract', 'N/A')
                abstract_cleaned = abstract.strip().lstrip("<jats:p>").rstrip("</jats:p>") if abstract != "N/A" else "N/A"

                # Date filtering (if 'since_date_str' is applied by CrossRef, this is mostly redundant but good for strictness)
                # CrossRef's 'from-pub-date' filter is usually sufficient.
                # If we needed finer grain client-side filtering (e.g. if API filter was broad):
                # if since_date_str and year != "N/A" and int(year) < int(since_date_str[:4]):
                #    continue # Skip if before the year of the 'since' date

                collected_items.append({
                    'title': title,
                    'authors': authors_list,
                    'doi': doi,
                    'year': year,
                    'abstract': abstract_cleaned
                })

            current_offset += len(items) # Advance offset by number of items *returned by API for this page*
            if len(items) < paginated_params['rows']: # API returned fewer than requested, means end of results
                 print("Info: API returned fewer results than requested, assuming end of query.")
                 break


        except requests.exceptions.RequestException as e:
            print(f"Error: API request failed after retries: {e}")
            break # Stop pagination on critical error
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON response from API.")
            break
        except Exception as e: # Catch any other unexpected error during processing a page
            print(f"Error: An unexpected error occurred during API call or processing: {e}")
            break

    # The date filter is applied by CrossRef via 'from-pub-date'.
    # So, collected_items should already respect this.
    # If we were doing client-side filtering, we'd count 'total_hits_after_filter' differently.
    # For now, all collected_items are considered "kept" as CrossRef does the date filtering.
    total_hits_after_filter = len(collected_items)

    return collected_items, total_hits_api, total_hits_after_filter


# --- Script Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search CrossRef for scientific literature with pagination and save results to JSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Shows default values in help
    )
    parser.add_argument("--query", type=str, required=True, help="The search query (e.g., 'rTMS Major Depressive Disorder').")
    parser.add_argument("--since", type=str, help="Optional start date for search (YYYY-MM-DD). Filters articles published from this date onwards.")
    parser.add_argument("--out", type=str, help="Output JSON file path. Defaults to 'data/literature/{yyyymmdd}_{query_slug}_results.json'.")
    parser.add_argument("--max-results", type=int, default=100, help="Maximum number of results to fetch.")
    parser.add_argument("--results-per-page", type=int, default=100, help="Number of results to fetch per API call (page). Max 1000 for CrossRef.")


    args = parser.parse_args()

    if args.results_per_page > 1000:
        print("Warning: --results-per-page exceeds CrossRef maximum of 1000, setting to 100.")
        args.results_per_page = 1000
    if args.max_results <= 0:
        print("Error: --max-results must be a positive integer.")
        exit(1)


    output_dir = os.path.join("data", "literature")
    ensure_dir_exists(output_dir)

    if args.out:
        output_file_path = args.out
        custom_output_dir = os.path.dirname(output_file_path)
        if custom_output_dir: ensure_dir_exists(custom_output_dir)
    else:
        today_str = datetime.date.today().strftime("%Y%m%d")
        query_slug = slugify(args.query)
        output_filename = f"{today_str}_{query_slug}_{args.max_results}max_results.json" # Added max_results to filename
        output_file_path = os.path.join(output_dir, output_filename)

    results, total_api_hits, final_kept_hits = search_crossref_paginated(
        args.query,
        args.since,
        max_results=args.max_results,
        results_per_page=args.results_per_page
    )

    # Logging Summary
    print("\n--- Search Summary ---")
    print(f"Query: '{args.query}'")
    if args.since:
        print(f"Date Filter: Published since {args.since}")
    print(f"CrossRef API reported approximately {total_api_hits} total results for the query (before pagination limits and date filter).")
    print(f"Fetched and kept {final_kept_hits} articles (up to --max-results limit of {args.max_results}).")

    if results:
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            print(f"Results saved to: {output_file_path}")
        except IOError as e:
            print(f"Error: Could not write to output file {output_file_path}: {e}")
    else:
        print("No results to save.")
    print("--------------------\n")
