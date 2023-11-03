CREATE DATABASE ogorod;

\c ogorod

CREATE TABLE user_conn (
    user_id bigint NOT NULL,
    conn_string varchar(128) NOT NULL

    PRIMARY KEY (user_id, conn_string)
)
