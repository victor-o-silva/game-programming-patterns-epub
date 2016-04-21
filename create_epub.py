# std lib
import os
from urllib.parse import urljoin

# third party
import requests
from bs4 import BeautifulSoup
from ebooklib import epub


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
EPUB_PATH = os.path.join(BASE_PATH, 'epubs')

BOOK_BASE_URL = 'http://gameprogrammingpatterns.com'
BOOK_TOC_URL = urljoin(BOOK_BASE_URL, '/contents.html')


def get_index_links():
    """Fetch links from the index of the book.

    Return a list of sections, where each section contains a
    list of its links::

        [
            [
                {'title': '<chapter title>', 'url': '<chapter url>'},
                {'title': '<chapter title>', 'url': '<chapter url>'},
                (...)
            ],
            [
                {'title': '<chapter title>', 'url': '<chapter url>'},
                {'title': '<chapter title>', 'url': '<chapter url>'},
                (...)
            ],
            (...)
        ]
    """
    req = requests.get(BOOK_TOC_URL)
    soup = BeautifulSoup(req.text, 'lxml', from_encoding='UTF-8')
    sections = []

    for section in soup.select('ol[type=I] > li'):
        section_anchors = section.select('a[href]')
        section_links = []
        for anchor in section_anchors:
            section_links.append({
                'title': anchor.get_text(),
                'url': urljoin(BOOK_BASE_URL, anchor['href'])
            })
        sections.append(section_links)

    return sections


def fetch_links_contents(sections):
    """Update the links in the sections with their HTML contents."""
    for section_idx, section in enumerate(sections):
        for link_index, link in enumerate(section):
            print('Fetching chapter "{}"'.format(link['title']))

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

            # Update link with content and file name
            content = '<html><head><meta charset="UTF-8"></head><body>' \
                      '{}</body></html>'.format(content.prettify())
            file_name = 's{}_c{}.htmlx'.format(str(section_idx).zfill(2),
                                               str(link_index).zfill(2))
            link.update({
                'content': content,
                'file_name': file_name
            })


def create_book(sections):
    """Receive the sections list and create the epub file."""
    book = epub.EpubBook()

    # set metadata
    book.set_identifier('gpp')
    book.set_title('Game Programming Patterns')
    book.set_language('en')
    book.add_author('Robert Nystrom')

    # create chapters
    chapters = []
    for section in sections:
        for link_index, link in enumerate(section):
            title = link['title']
            if link_index > 0:
                title = ' - {}'.format(title)
            chapter = epub.EpubHtml(title=title,
                                    file_name=link['file_name'],
                                    content=link['content'])
            book.add_item(chapter)
            chapters.append(chapter)

    # book's Table of contents
    book.toc = chapters

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # book's spine
    book.spine = chapters

    if not os.path.isdir(EPUB_PATH):
        os.mkdir(EPUB_PATH)

    file_path = os.path.join(EPUB_PATH, 'game-programming-patterns.epub')
    epub.write_epub(file_path, book, {})
    print('Book created: {}'.format(file_path))


def generate():
    sections = get_index_links()
    fetch_links_contents(sections)
    create_book(sections)


if __name__ == '__main__':
    generate()
