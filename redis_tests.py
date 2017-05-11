import redis
import json

from parse_results import load_results
from parse_results import parse_procedure

def main():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    scraped_results = load_results('list-of-pages-webmd-results.json')
    for i in scraped_results:
        k = i.replace("http://www.webmd.com/first-aid/", "")
        r.set(k, json.dumps(parse_procedure(scraped_results.get(i))).encode('utf-8'))

if __name__ == '__main__':
    main()
