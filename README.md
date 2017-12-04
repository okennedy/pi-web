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
```

##### Standard Deployment

```
$> psql -d ...

psql> CREATE TABLE SENSORS(name varchar(50), id int);
psql> CREATE TABLE READINGS(sensor int, time timestamp, data json);
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