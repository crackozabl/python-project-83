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


def get_urls(conn):
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
        cur.execute('SELECT id, name, created_at FROM urls ORDER BY created_at DESC;')
        result = cur.fetchall()

        logging.debug(f'urls result: {result}')

        return result

    return [stub_url(i) for i in range(10)]


def set_url(conn, name):
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as cur:
        cur.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;',
                    (name, datetime.now()))
        id = cur.fetchone()
        conn.commit()

    return id


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
