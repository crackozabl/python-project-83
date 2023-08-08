from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from os import getenv
import psycopg2
import logging
import page_analyzer.db as db
import requests
from urllib.parse import urlparse
import validators
from bs4 import BeautifulSoup

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')

CONNECTION_STRING = getenv('DATABASE_URL')


def get_connection():
    conn = psycopg2.connect(CONNECTION_STRING)
    return conn


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls():
    if request.method == 'POST':
        logging.debug('POST request received')
        conn = get_connection()
        url_name = request.form['url']

        if not is_valid_url(url_name) is True:

            flash('Некорректный URL')
            return render_template('index.html'), 422

        normalized_url = normalize_url(url_name)
        url = db.get_url_by_name(conn, normalized_url)

        if url:
            flash('Страница уже существует')
            return redirect(url_for('url', id=url.id))
        else:
            id = db.set_url(conn, normalized_url)
            flash('Страница успешно добавлена')
            return redirect(url_for('url', id=id))

    elif request.method == 'GET':
        conn = get_connection()
        urls = db.get_urls(conn, fetch_check=True)

        logging.debug('GET request received')
        return render_template('urls.html', urls=urls)
    else:
        return 'Not implemented', 404


@app.route('/urls/<int:id>', methods=['GET'])
def url(id):
    conn = get_connection()
    url = db.get_url(conn, id)
    checks = db.get_url_checks(conn, id)
    return render_template('url.html', url=url, checks=checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check(id):
    conn = get_connection()
    url = db.get_url(conn, id)

    if url:
        try:
            check = check_url(url)
        except requests.exceptions.RequestException:
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('url', id=id))

        if check['status_code'] == 200:
            db.set_url_check(conn, id,
                             check['status_code'],
                             check['h1'],
                             check['title'],
                             check['description'])
            flash('Страница успешно проверена')
        else:
            flash('Произошла ошибка при проверке')

        return redirect(url_for('url', id=id))
    else:
        return 'Not found', 404


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
