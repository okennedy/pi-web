from twisted.web.resource import Resource
from HomeBase.modules import Module

class Directory(Module):
  is_leaf = False
  def answer_GET(self, query):
    return [ { i.decode() : {} } for i in self.children.keys() ]
