from twisted.web.resource import Resource

class HelloWorld(Resource):
  isLeaf = True

  def render_GET(self, request):
    return "<html>Hello, world!<br/>{}</html>".format(request).encode()

  def render_SHOOP(self, request):
    return "<html>Hello, SHOOP!</html>".encode()

class Directory(Resource):
  def render_GET(self, request):
    return "<html>{}</html>".format("<br/>".join(children.keys())).encode()
