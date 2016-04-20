import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BOOK_BASE_URL = 'http://gameprogrammingpatterns.com'
BOOK_TOC_URL = urljoin(BOOK_BASE_URL, '/contents.html')


def get_toc_links():
    req = requests.get(BOOK_TOC_URL)
    soup = BeautifulSoup(req.text, 'lxml', from_encoding='UTF-8')
    sections = soup.select('ol[type=I] > li')

    links = []

    for section in sections:
        section_anchors = section.select('a[href]')
        section_links = []
        for anchor in section_anchors:
            section_links.append({
                'title': anchor.get_text(),
                'url': urljoin(BOOK_BASE_URL, anchor['href'])
            })
        links.append(section_links)

    return links


if __name__ == '__main__':
    toc_links = get_toc_links()
    from pprint import pprint
    pprint(toc_links)
