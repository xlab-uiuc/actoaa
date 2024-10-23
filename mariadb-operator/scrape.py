import yaml
import re
import requests
from bs4 import BeautifulSoup

SOURCE = "https://mariadb.com/kb/en/server-system-variables/#list-of-server-system-variables"
OUTPUT = "data/mariadb-schema.yaml"

resp = requests.get(SOURCE)
page = resp.text
soup = BeautifulSoup(page, "html.parser")

answer_div = soup.find('div', {'class': ['answer', 'formatted']})
target_h2 = answer_div.find('h2', string='List of Server System Variables')
for child in list(answer_div.children):
    if child == target_h2:
        child.extract()
        break
    child.extract()

items = []

def li2kv(li):
    text = li.text
    colon = text.find(":")
    key = text[:colon]
    val = text[colon+2:].rstrip("\n") # +2 to drop extra space
    return key, val

idx = 0
elements = list(filter(lambda child: child.name is not None, answer_div.children))
while idx < len(elements):
    if elements[idx].name == "h4":
        h4 = elements[idx]
        ul = elements[idx+1]
        assert ul.name == "ul"
        item = {"name": h4.text}
        item.update(dict(map(li2kv, ul.children)))
        items.append(item)
        idx += 2
    else:
        idx += 1

with open(OUTPUT, "w") as fp:
    yaml.dump(items, fp, sort_keys=False)
