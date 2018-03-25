from lxml import html
import requests
import re
import os
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from mutagen.id3 import ID3

import unittest


def get_filename(cd):
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]


def save_defined_file(filename, year, r):
    open(filename, 'wb').write(r.content)
    audio = ID3(filename)
    print(audio["TDRC"], filename, "\n")
    if(int(str(audio["TDRC"])) <= year):
        os.remove(filename)


def download_mp3(link, year):
    if link.endswith('.mp3'):
        r = requests.get(link, allow_redirects=True)
        filename = get_filename(r.headers.get('content-disposition'))
        if filename is None:
            filename = link.rsplit('/', 1)[1]
        save_defined_file(filename, year, r)
    elif link.endswith('.m4a'):
        r = requests.get(link, allow_redirects=True)
        filename = get_filename(r.headers.get('content-disposition'))
        if filename is None:
            filename = link.rsplit('/', 1)[1]
        save_defined_file(filename, year, r)


def get_urls(url, i, year):
    page = requests.get(url)
    webpage = html.fromstring(page.content)
    for link in webpage.xpath('//a/@href'):
        if i > 1:
            if re.match(r"https?:\/\/.*", link):
                get_urls(link, i-1)
            else:
                parsed_uri = urlparse(url[:len(url)-1])
                domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                get_urls(domain+link, i-1)
        else:
            download_mp3(link, year)
    return


tree = ET.parse('url.xml')
root = tree.getroot()
depth = int(root.find('depth').text)
year = int(root.find('year').text)
for url in tree.find('urls').findall('url'):
    get_urls(url.text.strip(), depth, year)


class TestLab1(unittest.TestCase):
    def setUp(self):
        pass
 
    def tearDown(self):
        pass
 
    def test_get_filename(self):
        self.assertEqual(get_filename("/error"), None)
        self.assertEqual(get_filename("Content-Disposition: attachment; filename=filename.mp3"), "filename.mp3")
        self.assertEqual(get_filename("Content-Disposition: attachment; filename="), None)
 
if __name__ == '__main__':
    unittest.main()