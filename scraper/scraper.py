import requests
import json
from bs4 import BeautifulSoup

def parse_procedure(proc_url):
    result = {}
    req = requests.get(proc_url)
    data = req.text
    soup = BeautifulSoup(data, 'html.parser')

    result = parse_title(soup, result)
    result = parse_steps(soup, result)

    return result

def parse_title(soup, result):
    title = soup.find('article', {'class': 'article'}).find('header')
    result['title'] = title.text.strip()
    return result

def parse_steps(soup, result):
    result['steps'] = {}
    result['order'] = []
    unordered_lists = soup.find('div', {'class': 'article-page'}).find_all('ul')
    for ul in unordered_lists:
        prev_sibling = ul.previous_sibling
        while prev_sibling_not_valid(prev_sibling):
            prev_sibling = prev_sibling.previous_sibling
        result['steps'][prev_sibling.text.strip()] = [li.text.strip() for li in ul.find_all('li')]
        result['order'].append(prev_sibling.text.strip())
    return result

def prev_sibling_not_valid(prev_sibling):
    return prev_sibling == '\n' or prev_sibling.name == 'ul' or any(x in prev_sibling.get('class',[]) for x in ['ad', 'native_ad'])

if __name__ == "__main__":
    url = raw_input('Enter webmd URL: ')
    result = parse_procedure(url)
    # JSON payload, TODO: save to db
    print json.dumps(result, indent=4, sort_keys=True)

# Example payload for http://www.webmd.com/first-aid/stroke-treatment
# {
#     "order": [
#         "Call 911 if the person has:",
#         "1. Note Time When Symptoms First Appeared",
#         "2. Follow Up"
#     ],
#     "steps": {
#         "1. Note Time When Symptoms First Appeared": [
#             "Tell emergency personnel the exact time when you first noticed symptoms.",
#             "Depending on the type of stroke, there is a medicine that may reduce long-term effects if given within four and a half hours of the first symptom appearing. Sooner is better.",
#             "If the person is diabetic, check the blood glucose (sugar) level. Treat low glucose with a glucose tablet, glass of orange juice or other sugary drink or food, or a glucagon injection (if the person is not able to swallow)."
#         ],
#         "2. Follow Up": [
#             "At the hospital, a doctor will examine the person and run tests to confirm the diagnosis and to see if the stroke was caused by clots or from bleeding in the brain. Tests may include an MRI or a CT scan.",
#             "Treatment may include medication, lifestyle changes, and possibly surgery."
#         ],
#         "Call 911 if the person has:": [
#             "Numbness or weakness of the face, arm, or legs -- especially on just one side of the body",
#             "Slurred or unusual speech",
#             "Trouble seeing in one or both eyes",
#             "Trouble walking, dizziness, or balance problems",
#             "Sudden confusion",
#             "Severe headache"
#         ]
#     },
#     "title": "Stroke Treatment"
# }
