DROP DATABASE page_analyzer;
CREATE DATABASE page_analyzer;

DROP TABLE urls;
CREATE TABLE urls (
    id integer primary key generated always as identity,
    name VARCHAR(255),
    created_at timestamp
);
DROP TABLE url_checks;

CREATE TABLE url_checks (
    id integer primary key generated always as identity,
    url_id integer,
    status_code integer,
    h1 text,
    title text,
    description text,
    created_at timestamp,
    CONSTRAINT fk_url
        FOREIGN KEY (url_id)
        REFERENCES urls(id)
);