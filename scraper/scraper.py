"""Scrape WebMD page and generate JSON representation
"""

import json
import requests
from bs4 import BeautifulSoup

def parse_procedure(proc_url):
    """Parse and return the result of a procedure url.

    Keyword arguments:
    proc_url -- the procedure url
    """
    result = {}
    req = requests.get(proc_url)
    data = req.text
    soup = BeautifulSoup(data, 'html.parser')

    result = parse_title(soup, result)
    result = parse_steps(soup, result)

    return result

def parse_title(soup, result):
    """Parse and return the result with the title parsed and added.

    Keyword arguments:
    soup -- the BeautifulSoup object
    result -- the result dictionary that is also returned
    """
    title = soup.find('article', {'class': 'article'}).find('header')
    result['title'] = format_text(title.text)
    return result

def parse_steps(soup, result):
    """Parse and return the result with the steps parsed and added.

    Keyword arguments:
    soup -- the BeautifulSoup object
    result -- the result dictionary that is also returned
    """
    result['steps'] = {}
    result['order'] = []
    unordered_lists = soup.find('div', {'class': 'article-page'}).find_all('ul')
    for ul_item in unordered_lists:
        prev_sibling = ul_item.previous_sibling
        while prev_sibling_not_valid(prev_sibling):
            prev_sibling = prev_sibling.previous_sibling
        if format_text(prev_sibling.text) not in result['steps']:
            result['steps'][format_text(prev_sibling.text)] = []
            result['order'].append(format_text(prev_sibling.text))
        for li_item in ul_item.find_all('li'):
            result['steps'][format_text(prev_sibling.text)].append({
                'text': format_text(li_item.text),
                'links': [{format_text(a.text).lower(): a['href']} for a in li_item.find_all('a')]
            })
    return result

def format_text(text):
    """Return formatted text (used for text parsed from the webpage).

    Keyword arguments:
    text -- a string to be modified and returned
    """
    return (text.strip()
            .replace(u"\u2019", "'")
            .replace(u"\u00a0", " ")
            .replace(u"\u201c", '"')
            .replace(u"\u201d", '"')
            .replace(u"\u00b0", " degrees ")
            .replace(u"\u00ba", " degrees")
            .replace(u"\u00bd", "1/2"))

def prev_sibling_not_valid(prev_sibling):
    """Return a bool determining if the previous sibling is not a valid header.

    Keyword arguments:
    prev_sibling -- the previous sibling in the DOM to test
    """
    return (prev_sibling == '\n' or
            prev_sibling.name == 'ul' or
            any(x in prev_sibling.get('class', []) for x in ['ad', 'native_ad']))

if __name__ == "__main__":
    url = input('Enter webmd URL: ')
    result = parse_procedure(url)
    print (json.dumps(result, indent=4, sort_keys=True))
