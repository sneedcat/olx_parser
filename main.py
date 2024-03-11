from dataclasses import dataclass
from typing import List, Optional
import urllib3
import re
import json
import urllib.parse
from flask import Flask, render_template, request
from multiprocessing import Pool

@dataclass
class Offer:
    id: int
    title: str
    description: str
    category: str
    isBusiness: bool
    url: str
    isHighlighted: bool
    isPromoted: bool
    createdTime: str
    lastRefreshTime: str
    itemCondition: str
    exchange: bool
    price: Optional[float]
    priceCurrency: Optional[str]
    photos: List[str]
    location: str
    searchReason: str

def parse(data: str) -> List[Offer]:
    list = re.findall(r'window.__PRERENDERED_STATE__= "((.|\s)*?)";\n        window.__TAURUS__', data)
    if len(list) == 0:
        return []
    to_be_parsed: str = list[0][0]
    to_be_parsed = to_be_parsed.encode('latin-1', 'backslashreplace').decode('unicode-escape')
    to_be_parsed = urllib.parse.unquote(to_be_parsed)
    to_be_parsed = re.sub('"links":{"self":.*?},', "", to_be_parsed)
    data = json.loads(to_be_parsed)
    offers = []
    for offer in data['listing']['listing']['ads']:
        parsed_offer = Offer(
            id=offer['id'],
            title=offer['title'],
            description=offer['description'],
            category=offer['category']['type'],
            isBusiness=offer['isBusiness'],
            url=offer['url'],
            isHighlighted=offer['isHighlighted'],
            isPromoted=offer['isPromoted'],
            createdTime=offer['createdTime'],
            lastRefreshTime=offer['lastRefreshTime'],
            itemCondition=offer['itemCondition'],
            exchange=offer['price']['exchange'],
            photos=offer['photos'],
            location=offer['location']['pathName'],
            searchReason=offer['searchReason'],
            price=None,
            priceCurrency=None
        )
        parsed_offer.description = parsed_offer.description.replace('<br />', '<br>')
        parsed_offer.description = re.sub(r"https://(.*?)\s", r"<a href='https://\1'>https://\1</a>", parsed_offer.description)
        if not parsed_offer.exchange:
            parsed_offer.priceCurrency = offer['price']['regularPrice']['currencyCode']
            parsed_offer.price = offer['price']['regularPrice']['value']
        offers.append(parsed_offer)
    return offers

def fetch_page(url, page_number):
  request = urllib3.request("GET", f"{url}?page={page_number}")
  data = request.data.decode('utf-8')
  return parse(data)  # Replace with your parsing logic

def get_multiple_pages(url: str, pages: int) -> List[Offer]:
  offers = []
  with Pool(processes=pages) as pool:
    # Submit tasks for fetching each page
    results = pool.starmap(fetch_page, [(url, page_number) for page_number in range(1, pages + 1)])
    offers = [item for sublist in results for item in sublist]  # Flatten nested list
  return offers

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/search", methods=['POST'])
def search():
    url = request.form['url']
    pages = int(request.form['pages'])
    sponsored = request.form.get('sponsored')
    offers = get_multiple_pages(url, pages)
    if not sponsored:
        offers = [offer for offer in offers if not offer.isPromoted]
    return render_template("offers.html", offers=offers)
