import urllib2
import json
from bs4 import BeautifulSoup

result = {}
page = urllib2.urlopen('http://www.webmd.com/first-aid/stroke-treatment').read()
soup = BeautifulSoup(page, 'html.parser')

instructions = soup.find(id='textArea')
# print(instructions.prettify())

# Parse the title of the first-aid instructions
title = instructions.h2
result['title'] = title.text

# Parse the table of contents for the article
table_of_contents = instructions.find(class_='article-subsection')
result['table_of_contents'] = [li.a.text for li in table_of_contents.find_all('li')]

# Parse each list of sub-steps associated with main steps
steps = instructions.find_all('h3')
for step in steps:
    substeps = instructions.find('h3', string=step.text).find_next_sibling('ul')
    result[step.text] = [li.text for li in substeps.find_all('li')]

# JSON payload, TODO: save to db
print json.dumps(result, indent=4, sort_keys=True)

# Example payload for http://www.webmd.com/first-aid/stroke-treatment
# {
#     "1. Note Time When Symptoms First Appeared": [
#         "Tell emergency personnel the exact time when you first noticed symptoms.",
#         "Depending on the type of stroke, there is a medicine that may reduce long-term effects if given within four and a half hours of the first symptom appearing. Sooner is better.",
#         "If the person is diabetic, check the blood glucose (sugar) level. Treat low glucose with a glucose tablet, glass of orange juice or other sugary drink or food, or a glucagon injection (if the person is not able to swallow)."
#     ],
#     "2. Follow Up": [
#         "At the hospital, a doctor will examine the person and run tests to confirm the diagnosis and to see if the stroke was caused by clots or from bleeding in the brain. Tests may include an MRI or a CT scan.",
#         "Treatment may include medication, lifestyle changes, and possibly surgery."
#     ],
#     "Call 911 if the person has:": [
#         "Numbness or weakness of the face, arm, or legs -- especially on just one side of the body",
#         "Slurred or unusual speech",
#         "Trouble seeing in one or both eyes",
#         "Trouble walking, dizziness, or balance problems",
#         "Sudden confusion",
#         "Severe headache"
#     ],
#     "table_of_contents": [
#         "Call 911 if the person has:",
#         "1. Note Time When Symptoms First Appeared",
#         "2. Follow Up"
#     ],
#     "title": "Stroke Treatment"
# }
