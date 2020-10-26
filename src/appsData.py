import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.parser import parse as date_parse

class appsData:
  def __init__(self, last_update=None):
    self.apps = apps # list of strings of apps
    self.data = pd.DataFrame([0, 0], columns=["Time", "Duration"])
    self.last_update = date_parse(last_update).timestamp() if last_update \
      else date_parse("2020-10-01").timestamp()

  def update_apps(self, apps):
    new_apps = list(filter(lambda app: app not in self.apps, apps))
    self.apps += new_apps
    for app in new_apps:
      self.data[app] = 0

  def parse_date(self, date_value):
    if type(date_value) == int or type(date_value) == float: return date_value
    else:
      try:
        return date_parse(date_value).timestamp()
      except:
        return None

  def get_max_time_of_apps(self, apps_df):
    time_groups = apps_df.groupby(["Name", "Id", "StartTime"])
    self.max_app_times = time_groups[["EndTime"]].max()
    self.max_app_times.reset_index(inplace=True)
    # sort according to start time:
    self.max_app_times = self.max_app_times.sort_values(by="StartTime")

  def get_events(self):
    end_df = self.max_app_times[["Id", "Name", "EndTime"]]
    end_df = end_df.rename(columns={"EndTime": "Time"})
    end_df["Type"] = "end"
    start_df = self.max_app_times[["Id", "Name", "StartTime"]]
    start_df = start_df.rename(columns={"StartTime": "Time"})
    start_df["Type"] = "start"
    self.events = pd.concat([start_df, end_df], axis=0)
    self.events = self.events[self.events["Time"] > \
      self.last_update]
    self.events = self.eventssort_values(by="Time")

  def update(self, apps_df):
    # The apps_df should hold rows with the app name, and the start and
    # end time:
    key_fields = ["Name", "Id", "StartTime", "EndTime"]
    if (any([field not in apps_df.columns for field in key_fields])):
      raise TypeError("data update missing key column")
    # update apps list:
    apps = apps_df["Name"].unique()
    self.update_apps(apps)
    # change dates to numeric values:
    apps_df[["StartTime"]] = apps_df[["StartTime"]]\
      .applymap(lambda d: self.parse_date(d))
    apps_df[["EndTime"]] = apps_df[["EndTime"]]\
      .applymap(lambda d: self.parse_date(d))
    # get max times for each app instance (unique - id and start time)
    self.get_max_time_of_apps(apps_df)
    self.get_events()
    # get the first app to start or end after
    print("Updating from ", datetime(self.last_update))
    # update the graph matrix:
    self.update_data(update_time)
    # update last update time - we make sure to leave the last row for next time
    self.last_update = self.data["Time"].max() + 1

  def update_data(self):
    last_state = self.data.iloc[-1]
    for ind, event in self.events.iterrows():
      # we don't want to write down the last event, since it has no duration:
      if ind == len(self.events.index): continue
      # check how long between the previous duration and this one to see if we
      # need to reset the state:
      if (event["Time"] > last_state["Time"] + 5 * 60) and \
      (event["Type"] == "start"):
        last_state = self.data.iloc[0] # which is all zeros


