# ingest/search.py

import argparse
import datetime
import json
import os
import requests
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# --- Configuration ---
CROSSREF_API_URL = "https://api.crossref.org/works"
POLITE_EMAIL = "user@example.com"

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

def validate_date_format(date_str):
    """Validates YYYY-MM-DD format and returns string or None."""
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return str(dt)
    except ValueError:
        print(f"Error: Date '{date_str}' is not in YYYY-MM-DD format.")
        return None

# --- Main Search Function ---
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.HTTPError)),
    reraise=True
)
def call_crossref_api(params, headers):
    response = requests.get(CROSSREF_API_URL, params=params, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()

def search_crossref_paginated(query_bibliographic=None, query_title=None, since_date_str=None, until_date_str=None, max_results=100, results_per_page=100):
    """
    Searches CrossRef API for literature with pagination, title search, and date range.
    """

    headers = {
        'User-Agent': f"NeuroStream Ingest Agent/1.2 ({POLITE_EMAIL})", # Updated agent version
        'mailto': POLITE_EMAIL
    }

    base_params = {
        'rows': min(results_per_page, max_results),
    }

    # Query construction
    if query_title:
        base_params['query.title'] = query_title
        active_query_field = "title"
        active_query_value = query_title
    elif query_bibliographic:
        base_params['query.bibliographic'] = query_bibliographic
        active_query_field = "bibliographic"
        active_query_value = query_bibliographic
    else:
        print("Error: No query provided (neither --query nor --query-title).")
        return [], 0, 0

    # Date filter construction
    filter_parts = []
    valid_since_date = None
    if since_date_str:
        valid_since_date = validate_date_format(since_date_str)
        if not valid_since_date: return [], 0, 0
        filter_parts.append(f"from-pub-date:{valid_since_date}")

    valid_until_date = None
    if until_date_str:
        valid_until_date = validate_date_format(until_date_str)
        if not valid_until_date: return [], 0, 0
        filter_parts.append(f"until-pub-date:{valid_until_date}")

    if filter_parts:
        base_params['filter'] = ",".join(filter_parts)

    collected_items = []
    current_offset = 0
    total_hits_api = 0
    initial_call_done = False

    print(f"Info: Querying CrossRef API for '{active_query_value}' (in {active_query_field})")
    if valid_since_date or valid_until_date:
        date_range_str = ""
        if valid_since_date: date_range_str += f"Since: {valid_since_date} "
        if valid_until_date: date_range_str += f"Until: {valid_until_date}"
        print(f"Info: Date Filter: {date_range_str.strip()}")
    print(f"Info: Max results: {max_results}")


    while len(collected_items) < max_results:
        paginated_params = base_params.copy()
        paginated_params['offset'] = current_offset
        paginated_params['rows'] = min(results_per_page, max_results - len(collected_items))

        if paginated_params['rows'] <= 0: break

        print(f"Info: Fetching page: offset {current_offset}, rows {paginated_params['rows']}")

        try:
            data = call_crossref_api(paginated_params, headers)
            items = data.get('message', {}).get('items', [])

            if not initial_call_done:
                total_hits_api = data.get('message', {}).get('total-results', 0)
                initial_call_done = True

            if not items:
                print("Info: No more results found on this page or query exhausted.")
                break

            for item in items:
                if len(collected_items) >= max_results: break

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

                collected_items.append({
                    'title': title, 'authors': authors_list, 'doi': doi,
                    'year': year, 'abstract': abstract_cleaned
                })

            current_offset += len(items)
            if len(items) < paginated_params['rows']:
                 print("Info: API returned fewer results than requested, assuming end of query.")
                 break
        except requests.exceptions.RequestException as e:
            print(f"Error: API request failed after retries: {e}")
            break
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON response from API.")
            break
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")
            break

    total_hits_after_filter = len(collected_items)
    return collected_items, total_hits_api, total_hits_after_filter

# --- Script Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search CrossRef for scientific literature with pagination, title search, and date range filters. Saves results to JSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--query", type=str, help="General bibliographic search query (e.g., 'rTMS Major Depressive Disorder').")
    parser.add_argument("--query-title", type=str, help="Title-specific search query (e.g., 'TMS PTSD'). If provided, this takes precedence over --query for the main search term.")
    parser.add_argument("--since", type=str, help="Optional start date for search (YYYY-MM-DD). Filters articles published from this date.")
    parser.add_argument("--until", type=str, help="Optional end date for search (YYYY-MM-DD). Filters articles published up to this date.")
    parser.add_argument("--out", type=str, help="Output JSON file path. Defaults to 'data/literature/{yyyymmdd}_{query_slug}_{filters}_results.json'.")
    parser.add_argument("--max-results", type=int, default=100, help="Maximum number of results to fetch.")
    parser.add_argument("--results-per-page", type=int, default=100, help="Number of results to fetch per API call (page). Max 1000 for CrossRef.")

    args = parser.parse_args()

    if not args.query and not args.query_title:
        parser.error("At least one of --query or --query-title must be specified.")
    if args.results_per_page > 1000:
        print("Warning: --results-per-page exceeds CrossRef maximum of 1000, setting to 100.")
        args.results_per_page = 1000
    if args.max_results <= 0:
        parser.error("--max-results must be a positive integer.")

    output_dir = os.path.join("data", "literature")
    ensure_dir_exists(output_dir)

    query_for_filename = args.query_title if args.query_title else args.query
    query_slug = slugify(query_for_filename)
    date_filter_str = ""
    if args.since: date_filter_str += f"_from{args.since}"
    if args.until: date_filter_str += f"_until{args.until}"

    if args.out:
        output_file_path = args.out
        custom_output_dir = os.path.dirname(output_file_path)
        if custom_output_dir: ensure_dir_exists(custom_output_dir)
    else:
        today_str = datetime.date.today().strftime("%Y%m%d")
        output_filename = f"{today_str}_{query_slug}{date_filter_str}_{args.max_results}max.json"
        output_file_path = os.path.join(output_dir, output_filename)

    results, total_api_hits, final_kept_hits = search_crossref_paginated(
        query_bibliographic=args.query,
        query_title=args.query_title,
        since_date_str=args.since,
        until_date_str=args.until,
        max_results=args.max_results,
        results_per_page=args.results_per_page
    )

    print("\n--- Search Summary ---")
    if args.query_title:
        print(f"Query (Title): '{args.query_title}'")
    elif args.query:
        print(f"Query (Bibliographic): '{args.query}'")

    date_range_log = []
    if args.since: date_range_log.append(f"Since: {args.since}")
    if args.until: date_range_log.append(f"Until: {args.until}")
    if date_range_log: print(f"Date Filter: {' '.join(date_range_log)}")
    else: print("Date Filter: Any date")

    print(f"CrossRef API reported approximately {total_api_hits} total results for the query (before pagination limits and date filters).")
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
