import json
import io 
import base64
from HomeBase.modules import Module
from HomeBase.Query import query, lookup
import matplotlib.pyplot as plt

class Graph(Module):
  is_leaf = True
  def __init__(self, **kvargs):
    super(Graph, self).__init__(**kvargs)
    self.lines = kvargs["lines"]
    self.root = kvargs["root"]


  def extract_line(self, data, x, y):
    return [
      { 
        "x" : lookup(record, x), 
        "y" : lookup(record, y) 
      } 
      for record in data 
    ]

  def get_data(self):
    print(self.root)
    return [
      { 
        "key"  : line["name"], 
        "color" : line["color"],
        "strokeWidth" : 3,
        "values"  : self.extract_line(query(self.root, line["data"]), line["x_points"], line["y_points"])
      }
      for line in self.lines
    ]

  def render_plot(self):
    for line in self.get_data():
      plt.plot(line["data"]["x"], line["data"]["y"])
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    ret = base64.b64encode(buf.read()).decode()
    buf.close()
    return ret

  def answer_GET(self, request):
    fmt = request.get("format", "json")
    if fmt == "json":
      return self.get_data()
    elif fmt == "png":
      return self.render_plot()
    else:
      return error(request, "Invalid format ({})".format(fmt))