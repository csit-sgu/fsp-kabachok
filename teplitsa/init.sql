CREATE DATABASE teplitsa;

\c teplitsa

CREATE TABLE ovowi (
    ovow_id uuid PRIMARY KEY,
    ovow_name varchar(128) NOT NULL,
    ovow_description varchar(512) NOT NULL
);
