wren
====

wren is a set of client and server application
to monitor the timestampped data.
According to the HTTP-based GET request from a client,
it picks a series of the timestampped data from the SQL or NoSQL database
and privides the data to the client in JSON.

## modules

- wrenHTTPServer.py
- wrenProvider.py
- db/wrenDB.py
- js/wrenClient.js

## requirements

- pymodbus
- dateutil

## gw

functions must return a string.

## how to run

export PYTHONPATH=<top directory>

1. copy test-sin.html to sample.html

2. modify "server_name" to point wrenProvider.py

    ~~~~
    var server_name = "http://localhost:8080/wrenProvider.py";
    ~~~~

3. in this case, you need to link wrenProvider.py into the document root.

    ~~~~
    ln -s ${deployed_directory}/wren/provider/wrenProvider.py ${document_root}/htdocs/wrenProvider.py
    ~~~~

4. load script, click "submit".

## database scheme

### key mapping table

*key* is an indentifier of data.
*key_id* is the sha1 hash value of the key
with a random number preceding 'tab_'.
it's going to be a table name for storing the time series data of the key.

    in SQLite3
    ~~~~
    create table tab_key_map (
        key_id text,
        key    text,
        unique (key_id) on conflict abort
        unique (key) on conflict abort,
    );
    ~~~~

### data table

*time* is a ISO8601 datetime string.
the recommended format is '%Y-%m-%dT%H:%M:%S%z'
    e.g. 2014-10-09T08:25:00+0900
    actually, any format supported by dateutil.parser is allowed.
note that *time* is not unique in the table.
duplication is allowed by the table scheme.
a management tool needs to maintain the consistency.
*value* is a string.

    in SQLite3
    ~~~~
    create table tab_<key_hash> (
        time  text,
        value text
    );
    ~~~~

to select data which has the data is from 
    ~~~~
    select key_hash from tab_key_hash
        where key = 'http://fiap.tanu.org/home/gw/temperature';
    select cast(value as real) from <key_hash>
        where time > "2013-06-05T18:52:49Z"
          and time < "2013-07-05T18:52:49Z";
    ~~~~

### condition table

*cond* is an identifier of the condition
to select a set of data from the data table.
*cond_hash* is also able to be an identifier
and it is a hash for users to specify the condition.

    in SQLite3
    ~~~~
    create table tab_cond {
        cond_id text,
        key_id  text,
        cond    text,
        unique (cond_id) on conflict abort,
        unique (key_id, cond) on conflict abort
    }
    ~~~~

## FAQ

Q. What is short for wren ?
A. It's "Web-based REST E... N...".


