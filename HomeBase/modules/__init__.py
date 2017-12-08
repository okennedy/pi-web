
from twisted.web import resource
import json

def error(request, msg, **kvargs):
  request.setResponseCode(400)
  kvargs["error"] = msg
  return json.dumps(kvargs).encode()

class Module(resource.Resource):
  def invoke(self, method, request):
    request.setHeader("Content-Type", "application/json")
    op = getattr(self, "answer_"+method, None)
    if(callable(op)):
      payload = request.args.get(b"query", [request.content.read()])[0].decode()
      if payload == "":
        payload = "{}"
      try:
        payload = json.loads(payload)
      except Exception as e:
        return error(request, "Malformed JSON: "+str(e), input = payload)
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