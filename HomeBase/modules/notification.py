from HomeBase.Query import query, lookup
from HomeBase.modules import Module
from HomeBase.Time import format_timedelta, days_until_start

def Notification(**kvargs):
  return { 
    "body" : kvargs.get("body", "Unknown Notification"),
    "status" : kvargs.get("status", "info"),
    "priority" : kvargs.get("priority", 0),
    "action" : kvargs.get("action", None),
    "icon" : kvargs.get("icon", "office/artboard")
  }

class Notifications(Module):
  def __init__(self, **kvargs):
    super(Notifications, self).__init__(**kvargs)
    self.root = kvargs["root"];

  def answer_GET(self, request):
    return (
      [
        Notification(
          body = "{}: {}".format(
            format_timedelta(event["start"]),
            event["summary"]
          ),
          priority = -days_until_start(event["start"]),
          icon = "office/calendar-1",
        )
        for event in lookup(self.root, ["data", "calendar"])
      ] + [
        Notification(
          body = "The sump pump might be down",
          status = "danger",
          icon = "ecology/water-tap",
          priority = 2
        )
        for event in [lookup(self.root, ["data", "status", "sump_pump"])]
        if event["depth"]["resistance"] < 500
      ]
    )