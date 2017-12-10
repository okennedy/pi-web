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
    # print("Connecting to {}".format(url))
    engine = create_engine(url)#, echo = True)
    metadata = MetaData()
    EngineCache[url] = {
      "connection" : engine.connect(),
      "engine" : engine,
      "metadata" : metadata,
      "tables" : {
        "sensors" : Table('sensors', metadata,
          Column('id', Integer, primary_key=True),
          Column('name', String(50))
        ),
        "readings" : Table('readings', metadata,
          Column('sensor', None, ForeignKey('sensors.id')),
          Column('time', DateTime()),
          Column('data', JSON)
        )
      }
    }
  return EngineCache[url]

