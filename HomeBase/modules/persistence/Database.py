import json
from twisted.web import resource
from sqlalchemy import create_engine, text
from sqlalchemy import Table, Column, MetaData, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.sql import select, desc, func
from HomeBase import error

EngineCache = {}

def get_connection(url):
  if not url in EngineCache:
    engine = create_engine(url, echo = True)
    EngineCache[url] = {
      "connection" : engine.connect(),
      "engine" : engine
    }
  return EngineCache[url]

class History(resource.Resource):
  isLeaf = True
  def __init__(self, **kwargs):
    self.connection = get_connection(kwargs["database"])["connection"]
    self.metadata = MetaData()
    self.sensors = Table(
      kwargs.get("sensors", 'SENSORS'), self.metadata,
      Column('id', Integer, primary_key=True),
      Column('name', String(50))
    )
    self.readings = Table(
      kwargs.get("readings", 'READINGS'), self.metadata,
      Column('sensor', None, ForeignKey('sensors.id')),
      Column('time', DateTime()),
      Column('data', JSON)
    )

  def sensor_id(self, name):
    result = self.connection.execute(
      select([self.sensors.c.id])
      .where(self.sensors.c.name == name)
    )
    row = result.fetchone()
    result.close()
    if row == None: 
      result = self.connection.execute(
        self.sensors.insert().values(name = name)
      )
      key = result.inserted_primary_key
      result.close()
      return key
    else:
      return row[0]

  def render_GET(self, request):
    query = (
      select([
        self.sensors.c.name.label("sensor"), 
        self.readings.c.time,
        self.readings.c.data
      ])
      .where(self.sensors.c.id == self.readings.c.sensor)
      .order_by(desc(self.readings.c.time))
    )

    # Add Interval
    period = request.args.get(b"period", [b"week"])[0]
    if period == b"week":
      query = query.where(
        self.readings.c.time >= func.now() - text("INTERVAL '1 week'")
      )
    else:
      return error(request, "Invalid period parameter ({})".format(period))

    sensor = request.args.get(b"sensor", [None])[0]
    if sensor != None:
      query = query.where(
        self.sensors.c.name == (sensor.decode())
      )

    result = self.connection.execute(query)
    sep = b"\n  "
    request.write(b"[")
    for r in result:
      request.write(sep)
      request.write(json.dumps( { 
        "sensor" : r[0], 
        "time" : r[1].timestamp(), 
        "data" : r[2]
      } ).encode())
      sep = b",\n  "
    result.close()
    return b"\n]"
  
  def render_PUT(self, request):
    sensor = request.args.get(b"sensor", [None])[0]
    data = request.args.get(b"data", [None])[0]
    if sensor == None:
      return error(request, "Missing sensor name")
    if data == None:
      return error(request, "Missing data value")
    sensor = self.sensor_id(sensor.decode())
    result = self.connection.execute(
      self.readings.insert().values(
        sensor = sensor,
        data = data.decode()
      )
    )
    result.close()
    return json.dumps({"status" : "success"}).encode()

    return "{}".format().encode()

