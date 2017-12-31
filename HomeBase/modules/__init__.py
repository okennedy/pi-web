
from twisted.web import resource
import json

def error(request, msg, **kvargs):
  request.setResponseCode(400)
  kvargs["error"] = msg
  return json.dumps(kvargs).encode()

class Module(resource.Resource):
  def __init__(self, **kwargs):
    super(Module, self).__init__()

  def getChild(self, name, request):
    if name == b"" or name == b"/":
      return self
    else:
      return self.children.get(name, None)

  def invoke(self, method, request):
    request.setHeader("Content-Type", "application/json")
    op = getattr(self, "answer_"+method, None)
    if(callable(op)):
      payload = request.content.read().decode()
      if(payload == ""):
        payload = {}
      else:
        try:
          payload = json.loads(payload)
        except Exception as e:
          return error(request, "Malformed JSON: {}".format(e), input = payload)
      for k in request.args.keys():
        v = request.args[k][0].decode()
        # try:
        #   v = json.loads(v)
        # except Exception as e:
        #   return error(request, "Malformed GET JSON: {}={}: {}".format(k, v, e), input = payload)
        payload[k.decode()] = v
      ret = op(payload)
      if("error" in ret):
        request.setResponseCode(400)
      return json.dumps(ret).encode()
    else:
      return error("Error: Unsupported Method {}".format(method))

  def render_GET(self, request):
    return self.invoke("GET", request)

  def render_PUT(self, request):
    return self.invoke("PUT", request)

  def render_POST(self, request):
    return self.invoke("POST", request)

  def render_DELETE(self, request):
    return self.invoke("DELETE", request)