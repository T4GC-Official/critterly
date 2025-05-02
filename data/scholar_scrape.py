import argparse
import json
from scholarly import scholarly

def sanitize_text(text):
    """Remove unwanted characters and symbols from text."""
    return text.encode('ascii', 'ignore').decode('utf-8')

def fetch_research_papers(query, max_results=10):
    search_query = scholarly.search_pubs(query)
    results = []
    for i in range(max_results):
        try:
            paper = next(search_query)
            results.append({
                'time': '3:27:05',
                'title': sanitize_text(paper['bib']['title']),
                'author': [sanitize_text(a) for a in paper['bib']['author']], 
                # sanitize_text(', '.join(paper['bib']['author'])),
                'year': paper['bib']['pub_year'],
                'link': paper.get('pub_url', ''),
                'abstract': sanitize_text(paper['bib'].get('abstract', '')),
            })
        except StopIteration:
            break
    return results

def write_json(data, output_file):
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Fetch research papers from Google Scholar.")
    parser.add_argument('--query', required=True, help="Search query for research papers")
    parser.add_argument('--output', default='research_data.json', help="Output JSON file")
    parser.add_argument('--max-results', type=int, default=10, help="Maximum number of results to fetch")
    
    args = parser.parse_args()
    
    papers = fetch_research_papers(args.query, args.max_results)
    write_json(papers, args.output)
    print(f"Research papers for query '{args.query}' saved to {args.output}")

if __name__ == '__main__':
    main()

