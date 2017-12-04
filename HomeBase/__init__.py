import json

def error(request, msg):
  request.setResponseCode(400)
  return json.dumps({"error" : msg}).encode()
