# PostgreSQL RabbitMQ Foreign Data Wrapper

[![Build Status](https://travis-ci.com/20minutes/pg-rabbitmq-fdw.svg?token=WLCcDeVWNcj6cS73wonE&branch=master)](https://travis-ci.com/20minutes/pg-rabbitmq-fdw)

The general idea is to push any inserted / updated / deleted document in PostgreSQL to RabbitMQ so it can (for example) be indexed in an other system.

## Before starting

- We only want to push a message in a queue for each action. So we assume the FDW will only perform `insert` action (see functions below).
- We also assume the virtual host for RabbitMQ is `/`.

## Requirements

- [Multicorn](http://multicorn.org/) 1.3.x and up
- Python 2.7 (don't know if Python 3 works)
- A RabbitMQ server (with exchange and queue configured)
- A PostgreSQL server (tested under 9.5, should be fine with 9.3, 9.4 & 9.6 too)
- Be sure to have these packages installed (at least on Ubuntu): `make gcc git postgresql-server-dev-9.5 python-dev python-setuptools python-pip`

## Installation

```bash
git clone https://github.com/Kozea/Multicorn /tmp/multicorn
cd /tmp/multicorn
git checkout v1.3.2
make install

git clone https://github.com/20minutes/pg-rabbitmq-fdw /tmp/pg-rabbitmq-fdw
cd /tmp/pg-rabbitmq-fdw
pip install -r requirements.txt
python setup.py install
```

## Usage

In that example we only send minimal information about the tag (only the PK). We could imagine more fields in the foreign table, like a `data` json field. Then in the function where we index the tag, we could image a more complex SQL query that will retrieve a bunch of information and store them in the `data` field as json.

```sql
-- Load extension
CREATE EXTENSION multicorn;

CREATE SERVER multicorn_rabbitmq FOREIGN DATA WRAPPER multicorn
OPTIONS (
  wrapper 'pg_rabbitmq.RabbitmqFDW'
);

-- Create test table
CREATE TABLE tag (
    tag_id uuid NOT NULL,
    label text,
    slug text,
    created_at timestamp with time zone,
    CONSTRAINT tag_pkey PRIMARY KEY (tag_id)
);

-- Create the the foreign table (with option for RabbitMQ)
CREATE FOREIGN TABLE tag_rabbitmq (
    "table" text,
    "id" uuid,
    "action" text
)
SERVER multicorn_rabbitmq
OPTIONS (
    host 'rabbitmq',
    port '5672',
    user 'guest',
    password 'guest',
    exchange 'indexing'
);

-- Create a function for each action
-- The only difference is the "action" value
CREATE OR REPLACE FUNCTION index_tag() RETURNS trigger AS $def$
    BEGIN
        INSERT INTO tag_rabbitmq ("table", "id", "action")
        VALUES ('tag', NEW.tag_id, 'insert');
        RETURN NEW;
    END;
$def$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION reindex_tag() RETURNS trigger AS $def$
    BEGIN
        INSERT INTO tag_rabbitmq ("table", "id", "action")
        VALUES ('tag', NEW.tag_id, 'update');
        RETURN NEW;
    END;
$def$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_tag() RETURNS trigger AS $def$
    BEGIN
        INSERT INTO tag_rabbitmq ("table", "id", "action")
        VALUES ('tag', OLD.tag_id, 'delete');
        RETURN OLD;
    END;
$def$ LANGUAGE plpgsql;

-- Create triggers for each action
CREATE TRIGGER rabbitmq_insert_tag
    AFTER INSERT ON tag
    FOR EACH ROW EXECUTE PROCEDURE index_tag();

CREATE TRIGGER rabbitmq_update_tag
    AFTER UPDATE OF label, slug ON tag
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE PROCEDURE reindex_tag();

CREATE TRIGGER rabbitmq_delete_tag
    BEFORE DELETE ON tag
    FOR EACH ROW EXECUTE PROCEDURE delete_tag();
```

## Message in RabbitMQ

Here are some sample of message pushed in RabbitMQ.

For an insert:

```json
{
    "action": "insert",
    "table": "tag",
    "id": "c9cd5011-400a-4b06-bcc4-2e4eb62e6d87"
}
```

For an update:

```json
{
    "action": "update",
    "table": "tag",
    "id": "c9cd5011-400a-4b06-bcc4-2e4eb62e6d87"
}
```

For a delete:

```json
{
    "action": "delete",
    "table": "tag",
    "id": "c9cd5011-400a-4b06-bcc4-2e4eb62e6d87"
}
```
