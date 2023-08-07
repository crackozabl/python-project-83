from collections import namedtuple
from datetime import datetime
from psycopg2 import extras
import logging

Url = namedtuple('Url',
                 ['id', 'name', 'created_at', 'last_check', 'last_status'])


def stub_url(n):
    return Url(
            n,
            f'http://www.google{n}.com',
            f'2020-01-0{n} 00:00:00',
            f'2020-01-0{n} 00:00:00',
            200)


def get_urls(conn, fetch_check=False):
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
        if fetch_check:
            cur.execute(
                '''
                SELECT DISTINCT ON (urls.id)
                    urls.id,
                    name,
                    urls.created_at,
                    url_checks.created_at as last_check,
                    url_checks.status_code as last_status
                FROM urls LEFT JOIN (
                        SELECT id, url_id, created_at, status_code
                        FROM url_checks
                        ORDER BY created_at DESC) as url_checks
                ON urls.id = url_checks.url_id
                ORDER BY urls.id DESC;
                ''')

            result = cur.fetchall()

            logging.debug(f'urls result: {result}')

            return result
        else:
            cur.execute(
                '''
                SELECT id, name, created_at
                FROM urls
                ORDER BY created_at DESC;
                ''')

            result = cur.fetchall()

            logging.debug(f'urls result: {result}')

            return result


def set_url(conn, name):
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
        cur.execute(
            '''
            INSERT INTO urls (name, created_at)
            VALUES (%s, %s) RETURNING id;
            ''',
            (name, datetime.now()))
        result = cur.fetchone()
        conn.commit()

    return result.id


def get_url(conn, id):
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
        cur.execute(
            'SELECT id, name, created_at FROM urls WHERE id = %s;',
            (id,))

        result = cur.fetchone()

        return result


def get_url_by_name(conn, name):
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
        cur.execute(
            'SELECT id, name, created_at FROM urls WHERE name = %s;',
            (name,))

        result = cur.fetchone()

        return result


def set_url_check(conn, url_id, status_code):
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
        cur.execute(
            '''
            INSERT INTO url_checks (url_id, created_at, status_code)
            VALUES (%s, %s, %s);
            ''',
            (url_id, datetime.now(), status_code))

        conn.commit()


def get_url_checks(conn, url_id):
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
        cur.execute(
            '''
            SELECT id, url_id, status_code, h1,title, description, created_at
            FROM url_checks
            WHERE url_id = %s;
            ''',
            (url_id,))

        result = cur.fetchall()

        return result
