from bs4 import BeautifulSoup, Comment
from multiprocessing import Pool
import requests
import re
import json


def scrape(item):
    ref_re = re.compile(r"\[\d+\]")
    ws_re = re.compile(r"\n\t+")
    i, url = item
    print(i, url)
    if i % 100 == 0:
        print(i)
    html = requests.get(f"https://starwars.fandom.com/{url}").text
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.select_one("main")
    for tag in main.find_all("script"):
        tag.extract()
    for tag in main.find_all(string=lambda text: isinstance(text, Comment)):
        tag.extract()
    nodes = [{"tag": "h1", "text": main.select_one(
        "#firstHeading").get_text().strip()}]
    categories = [tag.get("title") for tag in main.select(
        "ul.categories > li.category.normal > span > a")]
    content = main.select_one(".mw-parser-output")
    infobox = content.select_one(".portable-infobox")
    if infobox is not None:
        infobox.parent.extract()
    for node in content.children:
        if node.name == "p":
            text = node.get_text()
            text = re.sub(ref_re, "", text)
            text = re.sub(ws_re, " ", text)
            nodes.append({"tag": "p", "text": text.strip()})
        if node.name == "h2":
            text = node.select_one("span.mw-headline").get_text().strip()
            nodes.append({"tag": "h2", "text": text})
        if node.name == "h3":
            text = node.select_one("span.mw-headline").get_text().strip()
            nodes.append({"tag": "h3", "text": text})
        if node.name == "h4":
            text = node.select_one("span.mw-headline").get_text().strip()
            nodes.append({"tag": "h4", "text": text})
        if node.name == "h5":
            text = node.select_one("span.mw-headline").get_text().strip()
            nodes.append({"tag": "h5", "text": text})
        if node.name == "h6":
            text = node.select_one("span.mw-headline").get_text().strip()
            nodes.append({"tag": "h6", "text": text})
        with open(f"articles/{i}.json", "w") as f:
            f.write(json.dumps(
                {"url": url, "categories": categories, "nodes": nodes}))


if __name__ == '__main__':
    urls = [line.strip() for line in open("urls.txt").readlines()]

    pool = Pool(20)
    pool.map(scrape, enumerate(urls))
    pool.terminate()
    pool.join()
