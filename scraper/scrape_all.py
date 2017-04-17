from scraper import *
import json
import os

def scrape_all(urls_path):
    result = {}
    urls = get_urls(urls_path)
    for url in urls:
        result[url] = parse_procedure(url)
    return result

def get_urls(path):
    urls = []
    with open(path, 'r') as f:
        urls = [line.strip() for line in f]
    return urls

if __name__ == "__main__":
    result = scrape_all(raw_input('Input path to urls file: '))
    with open(raw_input('Input path to output file: '), 'w') as outfile:
        json.dump(result, outfile, indent=4, sort_keys=True)