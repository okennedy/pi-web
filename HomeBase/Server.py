import re
import importlib
from twisted.web import server
from twisted.internet import reactor, endpoints

def load_module(module_path, config):
  module_path = re.split("\\.", module_path)
  module_name = module_path.pop()
  module_path = ".".join(["HomeBase","modules"]+module_path)
  Module = getattr(importlib.import_module(module_path), module_name)
  print("   {}".format(Module, config))
  return Module(**config)

def load_tree(resource, prefix = ""):
  module   = resource["module"]
  config   = resource.get("config", {})
  if len(prefix) == 0:
    print("/:")
  else:
    print(prefix+":")
  instance = load_module(module, config)
  for child in resource.get("children", []):
    name = child["name"]
    if name == None:
      name = ""
    instance.putChild(name.encode(), load_tree(child, prefix+"/"+name))
  return instance

def start(config):
  print("Initializing Server...")
  port = config.get('port', 8080)
  resources = config['resources']
  root = load_tree(resources)
  site = server.Site(root)
  endpoint = endpoints.TCP4ServerEndpoint(reactor, port)
  endpoint.listen(site)
  print("Server running at http://localhost:{}".format(port))
  reactor.run()
