import json
from sqlalchemy import create_engine, text
from sqlalchemy import Table, Column, MetaData, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.sql import select, desc, func
from HomeBase.modules import Module

EngineCache = {}

def get_connection(url):
  if not url in EngineCache:
    engine = create_engine(url)#, echo = True)
    EngineCache[url] = {
      "connection" : engine.connect(),
      "engine" : engine
    }
  return EngineCache[url]

class History(Module):
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

  def answer_GET(self, request):
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
    period = request.get("period", "week")
    if period == "week":
      query = query.where(
        self.readings.c.time >= func.now() - text("INTERVAL '1 week'")
      )
    else:
      return error(request, "Invalid period parameter ({})".format(period))

    if "sensor" in request:
      query = query.where(
        self.sensors.c.name == request["sensor"]
      )

    result = self.connection.execute(query)
    ret = [ { 
        "sensor" : r[0], 
        "time" : r[1].timestamp(), 
        "data" : r[2]
      } for r in result]
    result.close()
    return ret 
  
  def answer_PUT(self, request):
    sensor = request.get("sensor", None)
    data = request.get("data", None)
    if sensor == None:
      return { "error" : "Missing sensor name" }
    if data == None:
      return { "error" : "Missing data value" }
    sensor = self.sensor_id(sensor)
    result = self.connection.execute(
      self.readings.insert().values(
        sensor = sensor,
        data = data
      )
    )
    result.close()
    return {"status" : "success"}

