# ingest/search.py

import argparse
import datetime
import json
import os
import requests # For making HTTP requests
import re

# --- Configuration ---
# CrossRef API endpoint
CROSSREF_API_URL = "https://api.crossref.org/works"
# Email for polite API usage (replace with a real one if available, or a generic one)
POLITE_EMAIL = "user@example.com"

# --- Helper Functions ---
def slugify(text):
    """Convert text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'\s+', '_', text)      # Replace whitespace with underscores
    text = re.sub(r'[^\w-]', '', text)   # Remove non-alphanumeric characters (except underscore/hyphen)
    return text

def ensure_dir_exists(directory_path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")

def format_date_for_crossref(date_str):
    """
    Validates and formats a date string (YYYY-MM-DD) for CrossRef API.
    CrossRef uses separate from-pub-date and until-pub-date.
    If 'since' is provided, it means from this date up to today.
    Returns a tuple (from_date, until_date) or None if invalid.
    """
    try:
        # Attempt to parse YYYY-MM-DD
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return str(dt) # Returns YYYY-MM-DD string
    except ValueError:
        # Could add relative date parsing like '7d' here in the future
        print(f"Error: Date '{date_str}' is not in YYYY-MM-DD format. Relative dates not yet supported by this script version.")
        return None

# --- Main Search Function ---
def search_crossref(query, since_date_str=None, results_per_page=20):
    """
    Searches CrossRef API for literature.

    Args:
        query (str): The search query.
        since_date_str (str, optional): Start date for filtering (YYYY-MM-DD).
        results_per_page (int): Number of results per API request page. Max is usually 1000 for CrossRef.
                                Using a smaller number like 20-100 for initial requests is common.

    Returns:
        list: A list of dictionaries, each representing a found article.
    """
    params = {
        'query.bibliographic': query,
        'rows': results_per_page,
        'mailto': POLITE_EMAIL # Important for polite API usage
    }

    if since_date_str:
        # CrossRef uses 'from-pub-date' for filtering from a specific date
        # For a simple 'since', we effectively filter from 'since_date' to today.
        # More complex date ranges would use 'until-pub-date' as well.
        formatted_date = format_date_for_crossref(since_date_str)
        if not formatted_date:
            return [] # Invalid date format
        params['filter'] = f"from-pub-date:{formatted_date}"
        # To get results *up to* today, we don't strictly need an until-pub-date
        # unless we want to cap it at a specific past date.

    headers = {
        'User-Agent': f"NeuroStream Ingest Agent/1.0 ({POLITE_EMAIL})"
    }

    print(f"Querying CrossRef API with: {query}, Since: {since_date_str or 'Any date'}")

    collected_items = []
    try:
        response = requests.get(CROSSREF_API_URL, params=params, headers=headers, timeout=20)
        response.raise_for_status()  # Raises an exception for bad status codes (4XX or 5XX)

        data = response.json()
        items = data.get('message', {}).get('items', [])

        if not items:
            print("No results found for the query.")
            return []

        for item in items:
            title = item.get('title', [""])[0] # Title is often a list
            doi = item.get('DOI', '')

            authors_list = []
            if 'author' in item:
                for author in item.get('author', []):
                    name_parts = []
                    if 'given' in author:
                        name_parts.append(author['given'])
                    if 'family' in author:
                        name_parts.append(author['family'])
                    if name_parts:
                        authors_list.append(" ".join(name_parts))

            # Get publication year
            pub_date_parts = item.get('issued', {}).get('date-parts', [[None]])[0]
            year = pub_date_parts[0] if pub_date_parts[0] else "N/A"

            # Abstract (often not directly available or truncated in CrossRef general search)
            # For full abstracts, individual DOI lookups or other APIs (like PubMed) might be needed.
            # CrossRef's REST API documentation notes that abstracts are not consistently available.
            abstract = item.get('abstract', 'N/A')
            # Sometimes abstracts are nested, e.g. under 'container-title' or via specific relations.
            # This MVP will take what's directly available.

            collected_items.append({
                'title': title,
                'authors': authors_list,
                'doi': doi,
                'year': year,
                'abstract': abstract.strip().lstrip("<jats:p>").rstrip("</jats:p>") if abstract != "N/A" else "N/A" # Basic cleanup
            })

        print(f"Successfully retrieved {len(collected_items)} articles.")

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []
    except json.JSONDecodeError:
        print("Failed to decode JSON response from API.")
        return []

    return collected_items

# --- Script Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search CrossRef for scientific literature.")
    parser.add_argument("--query", type=str, required=True, help="The search query (e.g., 'rTMS Major Depressive Disorder').")
    parser.add_argument("--since", type=str, help="Optional start date for search (YYYY-MM-DD). Filters articles published from this date onwards.")
    parser.add_argument("--out", type=str, help="Output JSON file path. If not provided, defaults to 'data/literature/{yyyymmdd}_{query_slug}_results.json'.")
    parser.add_argument("--results", type=int, default=20, help="Number of results to fetch (max typically 1000 for CrossRef, default 20).")

    args = parser.parse_args()

    # Determine output path
    output_dir = os.path.join("data", "literature")
    ensure_dir_exists(output_dir)

    if args.out:
        output_file_path = args.out
        # Ensure directory for custom output path also exists
        custom_output_dir = os.path.dirname(output_file_path)
        if custom_output_dir: # If output_file_path includes a directory
             ensure_dir_exists(custom_output_dir)
    else:
        today_str = datetime.date.today().strftime("%Y%m%d")
        query_slug = slugify(args.query)
        output_filename = f"{today_str}_{query_slug}_results.json"
        output_file_path = os.path.join(output_dir, output_filename)

    # Perform search
    results = search_crossref(args.query, args.since, results_per_page=args.results)

    # Save results
    if results:
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            print(f"Results saved to: {output_file_path}")
        except IOError as e:
            print(f"Error writing to output file {output_file_path}: {e}")
    else:
        print("No results to save.")
