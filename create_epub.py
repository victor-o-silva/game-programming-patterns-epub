import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_PATH = os.path.join(BASE_PATH, 'chapters')

BOOK_BASE_URL = 'http://gameprogrammingpatterns.com'
BOOK_TOC_URL = urljoin(BOOK_BASE_URL, '/contents.html')


def get_toc_links():
    """Fetch chapters' links from the index of the book.

    Return a list of sections, where each section contains a
    list of its links::

        [
            [
                {'title': '<chapter title>', 'url': '<chapter url>'},
                {'title': '<chapter title>', 'url': '<chapter url>'},
                {'title': '<chapter title>', 'url': '<chapter url>'},
                (...)
            ],
            [
                {'title': '<chapter title>', 'url': '<chapter url>'},
                {'title': '<chapter title>', 'url': '<chapter url>'},
                {'title': '<chapter title>', 'url': '<chapter url>'},
                (...)
            ],
            (...)
        ]
    """
    req = requests.get(BOOK_TOC_URL)
    soup = BeautifulSoup(req.text, 'lxml', from_encoding='UTF-8')
    links = []

    for section in soup.select('ol[type=I] > li'):
        section_anchors = section.select('a[href]')
        section_links = []
        for anchor in section_anchors:
            section_links.append({
                'title': anchor.get_text(),
                'url': urljoin(BOOK_BASE_URL, anchor['href'])
            })
        links.append(section_links)

    return links


def create_chapters_htmls(toc_links):
    """Download the chapters's htmls to the file system.

    Each chapter will be saved in a different file, and the corresponding
    file path will be inserted in each dict that is inside each section that
    is inside the ``toc_links`` received parameter.

    So, if the parameter came like this::

        [
            [
                {'title': '<chapter title>', 'url': '<chapter url>'},
                {'title': '<chapter title>', 'url': '<chapter url>'},
                (...)
            ]
            (...)
        ]

    It will end up like this::

        [
            [
                {'title': '<chapter title>', 'url': '<chapter url>',
                 'file_path': '<path_to_the_file>'},
                {'title': '<chapter title>', 'url': '<chapter url>',
                 'file_path': '<path_to_the_file>'},
                (...)
            ]
            (...)
        ]
    """
    if not os.path.isdir(CHAPTERS_PATH):
        os.mkdir(CHAPTERS_PATH)

    for section_idx, section in enumerate(toc_links):
        for link_index, link in enumerate(section):
            file_path = os.path.join(
                CHAPTERS_PATH,
                's{}_c{}.html'.format(str(section_idx).zfill(2),
                                      str(link_index).zfill(2))
            )
            print('Fetching chapter "{}" -> {} '.format(link['title'],
                                                        file_path))
            # Fetch content
            req = requests.get(link['url'])
            soup = BeautifulSoup(req.text, 'lxml', from_encoding='UTF-8')
            content = soup.select('div.content')[0]

            # Remove <nav>s
            while(content.select('nav')):
                content.select('nav')[0].extract()

            # Replace <a>s with their content
            for anchor in content.select('a'):
                anchor.replaceWith(anchor.text)

            # Fix images' src attributes
            for img_tag in content.select('img[src]'):
                if not img_tag['src'].startswith('http'):
                    img_tag['src'] = urljoin(BOOK_BASE_URL, img_tag['src'])

            # Save file
            with open(file_path, 'w') as chapter_file:
                chapter_file.write('<html><head><meta charset="UTF-8">'
                                   '</head><body>')
                chapter_file.write(content.prettify())
                chapter_file.write('</body></html>')

            # Create a key for the file path in the link dict
            link['file_path'] = file_path


def generate():
    toc_links = get_toc_links()
    create_chapters_htmls(toc_links)
    from pprint import pprint
    pprint(toc_links)


if __name__ == '__main__':
    generate()
