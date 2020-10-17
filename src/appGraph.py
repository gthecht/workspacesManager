import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.parser import parse as date_parse

class appsGraph:
  def __init__(self, last_update=None, apps = []):
    self.apps = apps # list of strings of apps
    self.graph_matrix = np.zeros([len(self.apps), len(self.apps)])
    self.last_update = date_parse(last_update).timestamp() if last_update \
      else date_parse("2020-10-01").timestamp()

  def update_apps(self, apps):
    new_apps = list(filter(lambda app: app not in self.apps, apps))
    self.graph_matrix = np.concatenate((self.graph_matrix,
      np.zeros([len(new_apps), len(self.apps)])), axis=0)
    self.apps += new_apps
    self.graph_matrix = np.concatenate((self.graph_matrix,
      np.zeros([len(self.apps), len(new_apps)])), axis=1)

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

  def update(self, apps_df):
    # The apps_df should hold rows with the app name, and the start and
    # end time:
    key_fields = ["Name", "Id", "StartTime", "EndTime"]
    if (any([field not in apps_df.columns for field in key_fields])):
      raise TypeError("graph update missing key column")
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
    # get only the rows that end after the last update
    apps_to_update = self.max_app_times[self.max_app_times["EndTime"] > \
      self.last_update]
    earliest_start = apps_to_update["StartTime"].min()
    apps_to_check = self.max_app_times[self.max_app_times["EndTime"] > \
      earliest_start]
    print("Updating", len(apps_to_update), "apps")
    print("Checking against", len(apps_to_check), "apps")
    # update the graph matrix:
    self.update_graph(apps_to_update, apps_to_check)
    # update last update time:
    self.last_update = datetime.now().timestamp()

  def update_graph(self, apps_to_update, apps_to_check):
    for ind1, app1 in apps_to_update.iterrows():
      for ind2, app2 in apps_to_check.iterrows():
        x_ind = self.apps.index(app1["Name"])
        y_ind = self.apps.index(app2["Name"])
        print(app1["Name"], "-", x_ind)
        concurrency = self.get_apps_concurrency(app1, app2)
        self.graph_matrix[x_ind, y_ind] += concurrency
        # If app2 is in apps_to_update and of course, app1 is in apps_to_check
        # We don't need to add to [y_ind, x_ind]:
        if app2["Name"] in apps_to_update["Name"]: continue
        self.graph_matrix[y_ind, x_ind] = self.graph_matrix[x_ind, y_ind]

  def get_apps_concurrency(self, app1, app2):
    # the concurrency is equal to the end time of one app, minus the start time
    # of the other and of course the minimum on both options.
    # a:  |-------|
    # b:      |------------|
    # as we can see, the value is indeed: min(end_a - start_b, end_b - start_a)
    # If there is now concurrency, the minimum value will be negative, so we
    # will max this with 0.
    # a:  |-------|
    # b:              |------------|
    diff1 = app1["EndTime"] - app2["StartTime"]
    diff2 = app2["EndTime"] - app1["StartTime"]
    diff3 = app1["EndTime"] - app1["StartTime"]
    diff4 = app2["EndTime"] - app2["StartTime"]
    concurrency = max(0, min(diff1, diff2, diff3, diff4))
    return concurrency

  def get_graph(self):
    # We need to normalize the matrix. We will do so by dividing each ROW by the
    # time the app of the row was open - this is exactly the diagonal of the
    # matrix.
    diag = self.graph_matrix.diagonal()
    diag = np.where(diag == 0, 1, diag)
    current_graph = self.graph_matrix / diag[:, None]
    return current_graph
