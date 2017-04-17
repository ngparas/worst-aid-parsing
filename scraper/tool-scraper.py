import requests
import json
from bs4 import BeautifulSoup

if __name__ == "__main__":
    url = 'http://www.medilexicon.com/equipment'
    req = requests.get(url)
    data = req.text
    soup = BeautifulSoup(data, 'html.parser')
    f = open('tools.txt', 'w')
    for div in soup.find_all('div', {'class': 'equipmentnames'}):
        for a in div.find_all('a'):
            # print(a.text.strip(), file='tools.txt')
            f.write(a.text.strip() + '\n')
    f.close()
