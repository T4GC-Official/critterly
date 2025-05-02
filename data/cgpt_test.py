import requests
from bs4 import BeautifulSoup
import json
import time
import re

def fetch_google_scholar_results(query, max_results=10):
    # Prepare the Google Scholar URL
    url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"
    
    # Send a GET request to Google Scholar
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return []

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all the result blocks (Google Scholar's result structure may change)
    results = []
    for i, result in enumerate(soup.select('.gs_ri')):
        if i >= max_results:
            break
        
        # Extract the title, link, authors, and publication year (if available)
        title_tag = result.select_one('.gs_rt')
        if title_tag:
            title = title_tag.text
            link = title_tag.a['href'] if title_tag.a else None
        
        author_tag = result.select_one('.gs_a')
        if author_tag:
            author_info = author_tag.text
        
        year = None
        # Sometimes the year is embedded in the author tag, so extract it with a regex
        if author_tag:
            year_match = re.search(r'\b(19|20)\d{2}\b', author_info)
            if year_match:
                year = year_match.group(0)
        
        snippet_tag = result.select_one('.gs_rs')
        snippet = snippet_tag.text if snippet_tag else ""

        # Append the scraped data to results
        results.append({
            'title': title,
            'link': link,
            'authors': author_info,
            'year': year,
            'snippet': snippet
        })
        
    return results

def save_results_to_json(results, output_file='google_scholar_results.json'):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    search_query = "sloth bear"
    max_results = 15
    
    # Fetch results
    results = fetch_google_scholar_results(search_query, max_results)
    
    # Save results to JSON
    save_results_to_json(results)

    print(f"Saved {len(results)} results to JSON file.")

