from collections import namedtuple
from datetime import datetime
from psycopg2 import extras
import psycopg2
import logging

Url = namedtuple('Url',
                 ['id', 'name', 'created_at'])

def get_connection(config):
    conn = psycopg2.connect(config['DATABASE_URL'])
    return conn

def close(conn):
    conn.close()

def get_urls_with_checks(conn):
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
        urls = get_urls(conn)
        cur.execute('''
            SELECT DISTINCT ON (url_id) 
                url_id,
                created_at as last_check,
                status_code as last_status
            FROM url_checks
            ORDER BY url_id DESC, id DESC''')
        checks = cur.fetchall()

        last_checks = { check.url_id: check for check in checks }

        result = []

        for url in urls:
            check = last_checks.get(url.id)
            url_with_check = {
                        'id': url.id,
                        'name': url.name,
                        'created_at': url.created_at,
                        'last_check': check.last_check if check else '',
                        'last_status': check.last_status if check else ''
                    }
            result.append(url_with_check)

        return result

def get_urls(conn):
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
        cur.execute(
            '''
            SELECT id, name, created_at
            FROM urls
            ORDER BY created_at DESC;
            ''')

        return cur.fetchall()

def set_url(conn, name):
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
        cur.execute(
            '''
            INSERT INTO urls (name)
            VALUES (%s) RETURNING id;
            ''',
            (name,))
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


def set_url_check(conn, url_id, status_code, h1, title, description):
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
        cur.execute(
            '''
            INSERT INTO url_checks
            (url_id, status_code, h1, title, description)
            VALUES (%s, %s, %s, %s, %s);
            ''',
            (url_id, status_code, h1, title, description))

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
