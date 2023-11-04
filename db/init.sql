CREATE DATABASE ogorod;

\c ogorod

CREATE TABLE users (
    user_id bigint NOT NULL,
    chat_id bigint NOT NULL,

    PRIMARY KEY (user_id)
);

CREATE TABLE source (
    source_id uuid PRIMARY KEY,
    conn_string varchar(128) NOT NULL,
    display_name varchar(128) NOT NULL,
    inactive boolean NOT NULL
);

CREATE TABLE user_source (
    user_id bigint NOT NULL,
    source_id uuid NOT NULL,

    PRIMARY KEY (user_id, source_id)
);


CREATE VIEW user_sources AS
SELECT us.user_id, us.source_id, s.conn_string, s.display_name, s.inactive
FROM user_source as us INNER JOIN source as s
ON us.source_id = s.source_id
