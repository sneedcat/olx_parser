import json
import re
import urllib.parse
from dataclasses import dataclass
from multiprocessing import Pool
from typing import List, Optional

import urllib3
from flask import Flask, render_template, request


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


@dataclass
class Config:
    url: str
    pages: int
    sponsored: bool
    sorting: Optional[str]
    from_price: Optional[float]
    to_price: Optional[float]


class Sorting:
    ASC = "filter_float_price%3Aasc"
    DESC = "filter_float_price%3Adesc"
    DATE = "created_at%3Adesc"
    RELEVANCE = "relevance%3Adesc"


def parse(data: str) -> List[Offer]:
    list = re.findall(
        r'window.__PRERENDERED_STATE__= "((.|\s)*?)";\n        window.__TAURUS__', data
    )
    if len(list) == 0:
        return []
    to_be_parsed: str = list[0][0]
    to_be_parsed = to_be_parsed.encode("latin-1", "backslashreplace").decode(
        "unicode-escape"
    )
    to_be_parsed = urllib.parse.unquote(to_be_parsed)
    to_be_parsed = re.sub('"links":{"self":.*?},', "", to_be_parsed)
    data = json.loads(to_be_parsed)
    offers = []
    for offer in data["listing"]["listing"]["ads"]:
        parsed_offer = Offer(
            id=offer["id"],
            title=offer["title"],
            description=offer["description"],
            category=offer["category"]["type"],
            isBusiness=offer["isBusiness"],
            url=offer["url"],
            isHighlighted=offer["isHighlighted"],
            isPromoted=offer["isPromoted"],
            createdTime=offer["createdTime"],
            lastRefreshTime=offer["lastRefreshTime"],
            itemCondition=offer["itemCondition"],
            exchange=offer["price"]["exchange"],
            photos=offer["photos"],
            location=offer["location"]["pathName"],
            searchReason=offer["searchReason"],
            price=None,
            priceCurrency=None,
        )
        parsed_offer.description = parsed_offer.description.replace("<br />", "<br>")
        parsed_offer.description = re.sub(
            r"https://(.*?)\s",
            r"<a href='https://\1'>https://\1</a>",
            parsed_offer.description,
        )
        if not parsed_offer.exchange:
            parsed_offer.priceCurrency = offer["price"]["regularPrice"]["currencyCode"]
            parsed_offer.price = offer["price"]["regularPrice"]["value"]
        offers.append(parsed_offer)
    return offers


def fetch_page(config: Config, page_number: int):
    url = config.url
    if config.url.find("?"):
        url = config.url[: config.url.find("?")]
    url = f"{url}?page={page_number}"
    if config.sorting:
        url += f"&search[order]={config.sorting}"
    if config.from_price:
        url += f"&search[filter_float_price%3Afrom]={config.from_price}"
    if config.to_price:
        url += f"&search[filter_float_price%3Ato]={config.to_price}"
    print(url)
    request = urllib3.request("GET", url)
    data = request.data.decode("utf-8")
    return parse(data)  # Replace with your parsing logic


def get_multiple_pages(config: Config) -> List[Offer]:
    offers = []
    with Pool(processes=config.pages) as pool:
        # Submit tasks for fetching each page
        results = pool.starmap(
            fetch_page,
            [(config, page_number) for page_number in range(1, config.pages + 1)],
        )
        offers = [
            item for sublist in results for item in sublist
        ]  # Flatten nested list
    return offers


app = Flask(__name__)


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    url = request.form["url"]
    pages = int(request.form["pages"] or 1)
    sponsored = request.form.get("sponsored")
    # capture raw sort selection for repopulating form
    sort_raw = request.form.get("sorting")
    from_price = request.form.get("priceFrom")
    to_price = request.form.get("priceTo")
    # translate raw sort to query code
    if sort_raw == "asc":
        sort_code = Sorting.ASC
    elif sort_raw == "desc":
        sort_code = Sorting.DESC
    elif sort_raw == "date":
        sort_code = Sorting.DATE
    elif sort_raw == "relevance":
        sort_code = Sorting.RELEVANCE
    else:
        sort_code = None
    config = Config(
        url=url,
        pages=pages,
        sponsored=sponsored,
        sorting=sort_code,
        from_price=from_price,
        to_price=to_price,
    )
    offers = get_multiple_pages(config)
    if not sponsored:
        offers = [offer for offer in offers if not offer.isPromoted]
    for offer in offers:
        if len(offer.photos) > 1:
            print(offer)
    # render offers page and re-fill previous inputs
    return render_template(
        "offers.html",
        offers=offers,
        url=url,
        pages=pages,
        sponsored=sponsored,
        sorting=sort_raw,
        priceFrom=from_price,
        priceTo=to_price,
    )
