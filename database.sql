DROP TABLE IF EXISTS url_checks CASCADE;
DROP TABLE IF EXISTS urls CASCADE;

CREATE TABLE urls (
    id integer primary key generated always as identity,
    name VARCHAR(255),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE url_checks (
    id integer primary key generated always as identity,
    url_id integer,
    status_code integer,
    h1 text,
    title text,
    description text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_url
        FOREIGN KEY (url_id)
        REFERENCES urls(id)
);
