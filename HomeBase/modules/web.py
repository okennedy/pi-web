
from HomeBase.modules import Module
from time import time as now
from datetime import date, datetime, timedelta
import requests
import caldav
from caldav.elements import dav, cdav

###### WEB MIRROR ######
class Mirror(Module):
  is_leaf = True

  def __init__(self, **kwargs):
    super(Mirror, self).__init__(**kwargs)
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

###### CALDAV-JSON Adaptor ######

def extract_events_from_event_set(event_set):
  if hasattr(event_set.instance, 'vcalendar'):
      return event_set.instance.components()
  elif hasattr(event_set.instance, 'vevent'):
      return [ event_set.instance.vevent ]

def extract_summary_from_event(event):
  for summary_attr in ('summary', 'location', 'description'):
    if hasattr(event, summary_attr):
      return getattr(event, summary_attr).value
    return "No Description"

def caldav_time_to_struct(t):
  if isinstance(t.value, date):
    return {
      "allday": True,
      "year":   t.value.year, 
      "month":  t.value.month, 
      "day":    t.value.day
    }
  elif isinstance(t.value, datetime):
    return {
      "allday": False,
      "year":   t.value.year, 
      "month":  t.value.month, 
      "day":    t.value.day,
      "hour":   t.value.hour,
      "minute": t.value.minute
    }
  else:
    raise Exception("Unknown type of {}".format(t.value)) 

class CalDav(Module):
  is_leaf = True
  def __init__(self, **kwargs):
    super(CalDav, self).__init__(**kwargs)
    self.window       = kwargs.get("window", 60*60*24*7)
    self.client       = caldav.DAVClient(
      kwargs["url"],
      username = kwargs["user"],
      password = kwargs["password"]
    )
    self.principal = self.client.principal()
    self.all_calendars = dict([
      (calendar.get_properties([dav.DisplayName()])["{DAV:}displayname"], calendar)
      for calendar in self.principal.calendars()
    ])
    self.calendars = [ 
      self.all_calendars[name] 
      for name in kwargs["calendars"] 
    ]

  def answer_GET(self, request):
    return [
      {
        "start" :   caldav_time_to_struct(event.dtstart),
        "end" :     caldav_time_to_struct(event.dtend),
        "summary" : extract_summary_from_event(event)
      }
      for calendar in self.calendars
      for event_set in calendar.date_search(
            datetime.now(),
            datetime.now() + timedelta(seconds = self.window)
          )
      for event in extract_events_from_event_set(event_set)
    ]
