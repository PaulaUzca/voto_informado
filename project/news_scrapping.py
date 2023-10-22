from urllib.parse import urljoin
from collections import deque
import requests
import json
import time
import json
from bs4 import BeautifulSoup

# Your Google API Key and Search Engine ID
API_KEY = 'AIzaSyB1zDMB5Qqoiqdv1aaeUfOnmha8aaCiGZA'
SEARCH_ENGINE_ID = '712aa8d8095714211'
def google_search_to_queue(query, additional_keywords=[], language="es", country="CO", num_results=10):
    compound_query = query + ' + ' + ' OR '.join(additional_keywords)
    language_param = f"&lr=lang_{language}" if language else ''
    country_param = f"&gl={country}" if country else ''

    url_queue = deque()

    for start_index in range(1, num_results + 1, 10):
        search_url = f"https://www.googleapis.com/customsearch/v1?q={compound_query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}{language_param}{country_param}&start={start_index}"
        search_response = requests.get(search_url).json()
        search_results = search_response.get('items', [])

        for result in search_results:
            url_queue.append(result['link'])

    return url_queue

def recursive_scrape(url, query, visited_urls, scraped_data, url_queue):
    if url in visited_urls:
        return
    visited_urls.add(url)

    try:
        page_response = requests.get(url, timeout=10)
    except requests.Timeout:
        print(f"Timeout occurred for URL: {url}")
        return
    except requests.RequestException as e:
        print(f"Request error for URL {url}: {e}")
        return

    content_type = page_response.headers.get('Content-Type', '')
    if 'text/html' not in content_type:
        print(f"Skipping non-HTML content at URL: {url}")
        return

    soup = BeautifulSoup(page_response.text, 'html.parser')
    main_content_tags = soup.find_all(['article', 'main'])
    if not main_content_tags:
        main_content_tags = soup.find_all('p')

    h1_tag = soup.find('h1')
    page_title = h1_tag.string if h1_tag else None

    if page_title is None:
        title_tag = soup.find('title')
        page_title = title_tag.string if title_tag else "No title found"

    page_title = page_title.replace("\r", "").replace("\n", "").replace("\t", "").strip()
    page_body = ' '.join([tag.text for tag in main_content_tags])
    cleaned_body = page_body.replace('\n', '').replace("\r", "").replace("\t", "").strip()

    scraped_data.append({
        'url': url,
        'title': page_title,
        'body': cleaned_body[:1000],
    })

    for tag in main_content_tags:
        for a_tag in tag.find_all('a', href=True):
            if query.lower() in a_tag.text.lower():
                full_url = urljoin(url, a_tag.get('href'))
                if full_url not in visited_urls:
                    url_queue.append(full_url)


def search_person_news(person_name):
    # Initialize scraped_data and visited_urls
    scraped_data = []
    visited_urls = set()

    # Additional keywords or topics to focus the search
    additional_keywords = ['noticias', 'propuestas', 'biografia', 'escandalo', 'presuntamente', 'corrupcion', 'alianza', 'politica', 'delito', 'justicia']

    # Test the function with compound query
    search_query = person_name
    N=16
    url_queue = google_search_to_queue(search_query, additional_keywords=additional_keywords, language='es', country='CO', num_results=int(N/2))
    count = 0
    #print(url_queue)
    start_time = time.time()
    
    # Then recursively scrape the URLs
    while url_queue and count <=N:
        url_to_scrape = url_queue.popleft()
        recursive_scrape(url_to_scrape, search_query, visited_urls, scraped_data, url_queue)
        count += 1
        # Check if one minute has passed
        elapsed_time = time.time() - start_time
        if elapsed_time >= 35:
            break

    #dump_json = (json.dumps(scraped_data, indent=4, ensure_ascii=False))
    return scraped_data