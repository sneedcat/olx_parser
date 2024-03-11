from dataclasses import dataclass
from typing import List, Optional
import urllib3
import re
import json
import urllib.parse

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
    with open('data.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(data, indent=4))
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
        if not parsed_offer.exchange:
            parsed_offer.priceCurrency = offer['price']['regularPrice']['currencyCode']
            parsed_offer.price = offer['price']['regularPrice']['value']
        offers.append(parsed_offer)
    return offers

def get_multiple_pages(url: str, pages: int) -> List[Offer]:
    offers = []
    for i in range(1, pages + 1):
        request = urllib3.request("GET", url + f'?page={i}')
        data = request.data.decode('utf-8')
        offers += parse(data)
    return offers

def main():
    url = 'https://www.olx.ro/electronice-si-electrocasnice/laptop-calculator-gaming/console-portabile/'
    pages = 2
    offers = get_multiple_pages(url, pages)
    for offer in offers:
        print(offer)

if __name__ == '__main__':
    main()