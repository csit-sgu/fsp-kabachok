CREATE DATABASE ogorod;

\c ogorod

CREATE TABLE source (
    source_id uuid PRIMARY KEY,
    conn_string varchar(128) NOT NULL
    inactive boolean NOT NULL
)

CREATE TABLE user_conn (
    user_id bigint NOT NULL,
    source_id uuid NOT NULL

    PRIMARY KEY (user_id, conn_string)
)
