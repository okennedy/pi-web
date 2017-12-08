
from HomeBase.modules import Module
from time import time as now
from datetime import datetime
import requests
import caldav
from caldav.elements import dav, cdav


class Mirror(Module):
  def __init__(self, **kwargs):
    self.url          = kwargs["url"]
    self.method       = kwargs.get("method", "GET")
    self.cache_time   = kwargs.get("cache_time", None)
    self.cache        = None
    self.last_request = now()

  def answer_GET(self, request):
    if (self.cache == None) or (self.cache_time == None) or (now() > self.last_request + self.cache_time):
      self.cache = requests.get(self.url)
      if self.cache.status_code == 200:
        self.last_request = now()
    if self.cache.status_code == 200:
      return self.cache.json()
    else:
      return {"error" : "Request Error: {}".format(self.cache.status_code)}.update(self.cache.json)

class CalDav(Module):
  def __init__(self, **kwargs):
    self.url          = kwargs["url"]
    self.calendars    = kwargs["calendars"]
    self.user         = kwargs["user"]
    self.password     = kwargs["password"]
    self.window       = kwargs.get("window", 60*60*24*7)

  def answer_GET(self, request):
    client = caldav.DAVClient(
      self.url,
      username = self.user,
      password = self.password
    )
    principal = client.principal()
    calendars = principal.calendars()
    return [ 
      calendar.get_properties([dav.DisplayName()]) 
      for calendar in calendars
    ];
