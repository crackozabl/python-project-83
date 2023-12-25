from flask import \
        Flask, render_template, request, \
        redirect, url_for, flash, abort
from dotenv import load_dotenv
from os import getenv
import page_analyzer.db as db
from page_analyzer.utils import \
        is_valid_url, normalize_url,\
        parse_page, check_url

app = Flask(__name__)

load_dotenv()

app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.config['DATABASE_URL'] = getenv('DATABASE_URL')


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/urls', methods=['GET'])
def get_urls():
    conn = db.get_connection(app.config)
    urls = db.get_urls_with_checks(conn)
    db.close(conn)

    return render_template('urls.html', urls=urls)


@app.route('/urls', methods=['POST'])
def post_urls():
    url_name = request.form['url']

    if not is_valid_url(url_name) is True:
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422

    normalized_url = normalize_url(url_name)

    conn = db.get_connection(app.config)
    url = db.get_url_by_name(conn, normalized_url)

    if url:
        flash('Страница уже существует', 'info')
        db.close(conn)
        return redirect(url_for('url', id=url.id))
    else:
        id = db.set_url(conn, normalized_url)
        db.close(conn)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('url', id=id))


@app.route('/urls/<int:id>', methods=['GET'])
def url(id):
    conn = db.get_connection(app.config)
    url = db.get_url(conn, id)
    checks = db.get_url_checks(conn, id)
    db.close(conn)
    return render_template('url.html', url=url, checks=checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check(id):
    conn = db.get_connection(app.config)
    url = db.get_url(conn, id)

    if url:
        try:
            check = check_url(url)
        except Exception:
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('url', id=id))

        if check['status_code'] == 200:
            db.set_url_check(conn, id,
                             check['status_code'],
                             check['h1'],
                             check['title'],
                             check['description'])
            flash('Страница успешно проверена', 'success')
        else:
            flash('Произошла ошибка при проверке', 'danger')

        db.close(conn)
        return redirect(url_for('url', id=id))
    else:
        db.close(conn)
        return abort(404)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500


