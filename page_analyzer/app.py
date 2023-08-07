from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from os import getenv
import psycopg2
import logging
import page_analyzer.db as db
import requests

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')

CONNECTION_STRING = getenv('DATABASE_URL')


def get_connection():
    conn = psycopg2.connect(CONNECTION_STRING)
    return conn


@app.route('/', methods=['GET', 'POST'])
def get():
    return render_template('index.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls():
    if request.method == 'POST':
        logging.debug('POST request received')
        conn = get_connection()
        url = db.get_url_by_name(conn, request.form['url'])

        if url:
            flash('Страница уже существует')
            return redirect(url_for('url', id=url.id))
        else:
            id = db.set_url(conn, request.form['url'])
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
        check = check_url(url)
        db.set_url_check(conn, id, check)
        return redirect(url_for('url', id=id))
    else:
        return 'Not found', 404


def check_url(url):
    resp = requests.get(url.name)
    return resp.status_code
