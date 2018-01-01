from HomeBase.Query import query, lookup
from HomeBase.modules import Module
from HomeBase.Time import format_timedelta, days_until_start
from datetime import date, datetime, timedelta
from time import time as get_now

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
    now = get_now()
    status = lookup(self.root, ["data", "status"])
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
        for event in [lookup(status, ["sump_pump"])]
        if event["depth"]["resistance"] < 1500
      ] + [
        Notification(
          body = "{} until {}".format(
            event["description"], 
            event["expires"]
          ),
          priority = 1 if event["significance"] == "Y" else 0,
          icon = "weather/storm-1",
          status = "warning" if event["significance"] == "Y" else "info"
        )
        for event in lookup(self.root, ["weather", "alerts", "alerts"])
      ] + [
        Notification(
          body = "Walk out the trash",
          priority = 0 if (now - trash["last_performed"] > 345600) else -100,
          icon = "ecology/recycling-1",
          status = "warning" if (now - trash["last_performed"] > 345600) else "faded",
          action = "http://serenity/data/chores/curb_trash?complete=yes" if (now - trash["last_performed"] > 345600) else None
        )
        for trash in [lookup(self.root, ["chores", "curb_trash"])]
        if datetime.today().weekday() == 3 # Show only on Thursday only

      ] + [
        Notification(
          body = "No updates from {} in {}".format(node, timedelta(seconds = now - lookup(status, [node, "last_update"]))),
          priority = 2,
          icon = "technology/transfer",
          status = "danger"
        )
        for node in [ i.decode() for i in status.children.keys() ]
        if now - lookup(status, [node, "last_update"]) > 3600
      ]
    )