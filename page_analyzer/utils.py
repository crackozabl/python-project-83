import requests
from urllib.parse import urlparse
import validators
from bs4 import BeautifulSoup


def normalize_url(url):
    parse_result = urlparse(url)
    return f'{parse_result.scheme}://{parse_result.netloc}'


def is_valid_url(url):
    return validators.url(url)


def parse_page(response):
    status_code = response.status_code
    page = response.text
    soup = BeautifulSoup(page, 'html.parser')
    title = soup.find('title').text if soup.find('title') else ''
    h1 = soup.find('h1').text if soup.find('h1') else ''
    description = soup.find('meta', attrs={'name': 'description'})
    if description:
        description = description['content']
    else:
        description = ''
    return {
        'status_code': status_code,
        'title': title[:255],
        'h1': h1[:255],
        'description': description[:255],
    }


def check_url(url):
    response = requests.get(url.name)
    response.raise_for_status()
    return parse_page(response)
