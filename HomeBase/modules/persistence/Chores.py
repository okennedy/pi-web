import json
from sqlalchemy import create_engine, text
from sqlalchemy import Table, Column, MetaData, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.sql import select, desc, func, update
from sqlalchemy.dialects.postgresql import insert
from HomeBase.modules import Module
from HomeBase.modules.persistence.Database import get_connection


class OneChore(Module):
  is_leaf = True
  def __init__(self, **kvargs):
    super(OneChore, self).__init__(**kvargs)
    if "connection" in kvargs:
      self.connection = kvargs["connection"]
      self.metadata   = kvargs["metadata"]
      self.chores     = kvargs["chores"]
      self.chore      = kvargs["chore"]
    else:
      engine = get_connection(kvargs["database"])
      self.connection = engine["connection"]
      self.metadata   = engine["metadata"]
      self.chores     = engine["tables"]["chores"]
      self.chore      = kvargs["chore"]

  def answer_GET(self, request):
    if "complete" in request:
      self.answer_PUT(request)
    query = (
      select([self.chores.c.last_performed, self.chores.c.description])
          .where(self.chores.c.name == self.chore)
    )
    result = self.connection.execute(query)
    record = result.fetchone()
    result.close()
    data = {}
    if record == None: 
      return {
        "description" : "No such chore registered",
        "last_performed" : 0
      }
    else:
      return {
        "description" : record[1],
        "last_performed" : record[0].timestamp()
      }
    return data

  def answer_PUT(self, request):
    print("Writing to chore '{}': {}".format(self.chore, request))
    if "description" in request:
      stmt = insert(self.chores).values(
        name = self.chore,
        description = request["description"], 
        last_performed = func.now()
      )
      stmt.on_conflict_do_update(
        index_elements=[self.chores.c.name],
        set_=dict(description= request["description"])
      )
      result = self.connection.execute(stmt)
      result.close()
    else:
      result = self.connection.execute(
        update(self.chores, values=dict(last_performed = func.now()))
      )
      result.close()
    return {"status" : "success"}

class AllChores(Module):
  is_leaf = False
  def __init__(self, **kvargs):
    super(AllChores, self).__init__(**kvargs)
    engine = get_connection(kvargs["database"])
    self.connection = engine["connection"]
    self.metadata   = engine["metadata"]
    self.chores     = engine["tables"]["chores"]

  def make_child(self, name):
    ret = OneChore(
      connection = self.connection,
      metadata = self.metadata,
      chores = self.chores,
      chore = name.decode()
    )
    self.children[name] = ret
    return ret

  def getChild(self, name, request):
    if name == b"" or name == b"/":
      return self
    if name in self.children:
      return self.children[name]
    return self.make_child(name)

  def answer_GET(self, request):
    result = self.connection.execute(select([self.chores.c.name, self.chores.c.description, self.chores.c.last_performed]))
    ret = dict([
      ( 
        chore[0],
        { 
          "description" : result[1],
          "last_performed" : result[2].timestamp()
        }
      )
      for chore in result
    ])
    result.close()
    return ret