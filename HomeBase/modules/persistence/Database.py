from twisted.web import resource
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, MetaData, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.types import DateTime, JSON

EngineCache = {}

def get_engine(url):
  if not url in EngineCache:
    EngineCache[url] = create_engine(url)
  return EngineCache[url]

class ReadingsTable(resource.Resource):
  isLeaf = True
  def __init__(self, **kwargs):
    self.engine = get_engine(kwargs["database"])
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

  def render_GET(self, request):
    return "{}".format(request).encode()