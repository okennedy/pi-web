
import json
from sqlalchemy import create_engine, text
from sqlalchemy import Table, Column, MetaData, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.sql import select, desc, func
from HomeBase.modules import Module
from HomeBase.modules.persistence.Database import get_connection



def get_sensor_id(connection, sensors, name):
  result = connection.execute(
    select([sensors.c.id])
    .where(sensors.c.name == name)
  )
  row = result.fetchone()
  result.close()
  if row == None: 
    result = connection.execute(
      sensors.insert().values(name = name)
    )
    key = result.inserted_primary_key
    result.close()
    return key[0]
  else:
    return row[0]


class History(Module):
  is_leaf = True
  def __init__(self, **kvargs):
    super(History, self).__init__(**kvargs)
    engine = get_connection(kvargs["database"])
    self.connection = engine["connection"]
    self.metadata   = engine["metadata"]
    self.sensors    = engine["tables"]["sensors"]
    self.readings   = engine["tables"]["readings"]

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
    sensor = get_sensor_id(self.connection, self.sensors, sensor)
    result = self.connection.execute(
      self.readings.insert().values(
        sensor = sensor,
        data = data
      )
    )
    result.close()
    return {"status" : "success"}

class OneStatus(Module):
  is_leaf = True
  def __init__(self, **kvargs):
    super(OneStatus, self).__init__(**kvargs)
    if "connection" in kvargs:
      self.connection = kvargs["connection"]
      self.metadata   = kvargs["metadata"]
      self.readings   = kvargs["readings"]
      self.sensor     = kvargs["sensor"]
    else:
      engine = get_connection(kvargs["database"])
      self.connection = engine["connection"]
      self.metadata   = engine["metadata"]
      self.readings   = engine["tables"]["readings"]
      self.sensor     = kvargs["sensor"]

  def answer_GET(self, request):
    query = (
      select([self.readings.c.time, self.readings.c.data])
          .where(self.readings.c.sensor == self.sensor)
          .order_by(desc(self.readings.c.time))
          .limit(1)
    )
    result = self.connection.execute(query)
    record = result.fetchone()
    result.close()
    if record == None: 
      return {}
    data = record[1]
    data["last_update"] = record[0].timestamp()
    return data

  def answer_PUT(self, request):
    print("Writing to sensor '{}': {}".format(self.sensor, request))
    result = self.connection.execute(
      self.readings.insert().values(
        sensor = self.sensor,
        data = request
      )
    )
    result.close()
    return {"status" : "success"}

class AllStatus(Module):
  is_leaf = False
  def __init__(self, **kvargs):
    super(AllStatus, self).__init__(**kvargs)
    engine = get_connection(kvargs["database"])
    self.connection = engine["connection"]
    self.metadata   = engine["metadata"]
    self.sensors    = engine["tables"]["sensors"]
    self.readings   = engine["tables"]["readings"]

  def make_child(self, name, id):
    ret = OneStatus(
      connection = self.connection,
      metadata = self.metadata,
      readings = self.readings,
      sensor = id
    )
    self.children[name] = ret
    return ret

  def getChild(self, name, request):
    if name == b"" or name == b"/":
      return self
    if name in self.children:
      return self.children[name]
    sensor_id = get_sensor_id(self.connection, self.sensors, name.decode())
    return self.make_child(name, sensor_id)

  def answer_GET(self, request):
    result = self.connection.execute(select([self.sensors.c.name, self.sensors.c.id]))
    ret = dict([
      ( 
        sensor[0],
        ( self.children[sensor[0].encode()].answer_GET(request) 
            if sensor[0].encode() in self.children
          else self.make_child(sensor[0].encode(), sensor[1]).answer_GET(request)
        )
      )
      for sensor in result
    ])
    return ret

