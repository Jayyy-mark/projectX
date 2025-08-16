import os
import time
from serpapi.google_search import GoogleSearch
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

class WebSearch:

    #constructor
    def __init__(self, api_key=None,cache_ttl=300):
        self.api_key = os.getenv['SERPAPI_KEY']
        self.cache_ttl = cache_ttl
        self.cache = {}
    
    def _is_cache_valid(self,query):
        entry = self.cache.get(query)
        if not entry:
            return False
        timestamp, _ = entry
        return (time.time() - timestamp) < self.cache_ttl
    
    def search(self, query, maxresult = 10):
        if self._is_cache_valid(query):
            return self.cache[query][1]

        params = {
            "q": query,
            "api_key": self.api_key,
            "num": maxresult,
            "engine": "google",
            "gl": "us",      # Country: US
            "hl": "en"       # Language: English
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            organic = results.get("organic_results", [])
            output = []
            for r in organic[:maxresult]:
                output.append({
                    "title": r.get("title", ""),
                    "link": r.get("link", ""),
                    "snippet": r.get("snippet", ""),
                })
            # Cache the results with timestamp
            self.cache[query] = (time.time(), output)
            return output

        except Exception as e:
            # You can add more detailed error handling/logging here
            print(f"WebSearch error: {e}")
            return []
        
    #formatting results
    def format_results(sef,results):

        if not results:
            return "No results found."

        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"{i}. {r['title']}\n{r['link']}\n{r['snippet']}\n")
        return "\n".join(formatted)


def browse_and_extract(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        content = page.content()
        browser.close()
    soup = BeautifulSoup(content, "html.parser")
    text = ' '.join(soup.stripped_strings)
    return text[:100000]
    


    



