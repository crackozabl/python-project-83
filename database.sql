DROP DATABASE page_analyzer;
CREATE DATABASE page_analyzer;
DROP TABLE urls;

CREATE TABLE urls (
    id integer primary key generated always as identity,
    name VARCHAR(255),
    created_at timestamp
);