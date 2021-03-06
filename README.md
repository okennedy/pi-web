# pi-web

### Prereqs

* Python 3.x (below written assuming 3.6)
* Postgresql (for Database integration)

### Set Up 

```
$> pip3.6 install twisted     # Twisted Python -- Server Framework
$> pip3.6 install PyGreSQL    # PostgreSQL integration
$> pip3.6 install sqlalchemy  # SQL ORM
$> pip3.6 install PyYAML      # YAML Parsing
$> pip3.6 install requests    # HTTP client
$> pip3.6 install caldav      # CalDav client
$> pip3.6 install matplotlib  # Graphing
$> apt install python3-tk     # Support for matplotlib
```

##### Standard Deployment

```
$> psql -d ...

psql> CREATE TABLE sensors(name varchar(50), id SERIAL, PRIMARY KEY(id));
psql> CREATE TABLE readings(sensor integer NOT NULL, time timestamp NOT NULL DEFAULT LOCALTIMESTAMP, data json, FOREIGN KEY (sensor) REFERENCES sensors(id));
psql> CREATE INDEX ON readings USING BTREE (time);
psql> CREATE INDEX ON readings USING BTREE (sensor, time);
psql> CREATE TABLE chores(name varchar(50), description text, last_performed timestamp, PRIMARY KEY(name));
```

### Go Time

```
python3.6 run.py
```

# Documentation and Notes

### Twisted Python

* [Home Page](http://twistedmatrix.com)
* [Twisted-Web](http://twistedmatrix.com/documents/current/web/howto/using-twistedweb.html)

### SQL

* [PyGreSQL](http://www.pygresql.org/)
* [SQLAlchemy](http://www.sqlalchemy.org/)
   * [Tutorial](http://docs.sqlalchemy.org/en/rel_1_1/core/tutorial.html)

### PyYAML

* [GitHub](https://github.com/yaml/pyyaml)