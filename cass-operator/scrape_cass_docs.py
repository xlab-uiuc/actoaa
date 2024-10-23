import yaml
import re
import requests
from bs4 import BeautifulSoup

SOURCE = "https://cassandra.apache.org/doc/stable/cassandra/configuration/cass_yaml_file.html"
OUTPUT = "data/cassandra-yaml.yaml"

resp = requests.get(SOURCE)
page = resp.text
soup = BeautifulSoup(page, "html.parser")

article = soup.find("div", class_="doc")
sects = article.find_all("div", class_="sect1")

items = []

for sect in sects:
    name = sect.find("h2").text
    try:
        default_value = sect.find("em", string="Default Value:").parent.text[15:]
    except AttributeError as e:
        default_value = "<UNKNOWN>"
    try:
        description = re.sub(r"\n+", "", sect.find("div", class_="sectionbody").text)
    except AttributeError as e:
        description = "<NONE>"
    items.append({
        "name": name,
        "default_value": default_value,
        "description": description
    })

with open(OUTPUT, "w") as fp:
    yaml.dump(items, fp)
