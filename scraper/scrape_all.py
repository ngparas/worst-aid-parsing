"""Scrape all WebMD First Aid pages in inputted list
"""

import json
from scraper import parse_procedure

def scrape_all(urls_path):
    """Scrape all WebMD pages in file with given path

    Keyword arguments:
    urls_path -- path to file listing WebMD pages
    """
    result = {}
    urls = get_urls(urls_path)
    for url in urls:
        result[url] = parse_procedure(url)
    return result

def get_urls(path):
    """Get a list of the urls contained in the file with the given path

    Keyword arguments:
    path -- path to file listing WebMD pages
    """
    urls = []
    with open(path, 'r') as f:
        urls = [line.strip() for line in f]
    return urls

if __name__ == "__main__":
    result = scrape_all(input('Input path to urls file: '))
    with open(input('Input path to output file: '), 'w') as outfile:
        json.dump(result, outfile, indent=4, sort_keys=True)
