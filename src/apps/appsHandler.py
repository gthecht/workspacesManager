import os
import sys
import numpy as np
import pandas as pd
import dateutil.parser
import asyncio

parent = os.path.abspath('./src')
sys.path.insert(1, parent)
import powershellClient as PSClient
from unknownOSWarning import unknown_OS_Warning
from apps.explorer import Explorer

def find_words_in_string(wordStr, string):
  words = wordStr.split()
  appear = list(filter(lambda word: word.lower() in string.lower(), words))
  return len(appear) / len(words)

def match_candidates(list1, list2):
  if not len(list1): return list2
  elif not len(list2): return list1
  else:
    return np.multiply(np.add(list1, list2), np.multiply([weight > 0 for weight in list1], [weight > 0 for weight in list2]))

#%% AppsHandler class:
class AppsHandler:
  def __init__(self, os="windows"):
    self.os = os
    if self.os == "windows": self.STARTPATH = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\"
    self.explorer = Explorer()
    print("apps handler constructed")

  async def get_apps(self):
    print("Initializing apps with the start shortcuts")
    start_apps = await PSClient.get_PS_table("Get-StartApps", ["Name"])
    start_apps = [app[0] for app in start_apps]
    apps_table = await PSClient.get_PS_table("Get-ChildItem \"" + self.STARTPATH + "*\" -Recurse | where { ! $_.PSIsContainer }", ["Name", "FullName"])

    apps_list = []
    candidates = []
    path = []
    for app in start_apps:
      if app not in apps_list:
        apps_list.append(app)
        candid_list = list(filter(lambda row: app in row[0], apps_table))
        candidates.append([row[1] for row in candid_list])
        if candidates[-1] == []: path.append(None)
        else: path.append(candidates[-1][0])
    apps_dict = {
      "path": path,
      "pathCandidates": candidates
    }
    self.apps = pd.DataFrame(apps_dict, index=apps_list,columns=["path", "pathCandidates"])

  async def get_open_apps(self):
    if self.os == "windows":
      items = ["Id", "Name", "Description", "MainWindowTitle", "StartTime", "Path"]
      try:
        open_apps_list = await PSClient.get_PS_table("Get-Process | Where-Object { $_.MainWindowHandle -ne 0}", items)
      except Exception as err:
        print("Powershell client failed to get open apps with error: " + str(err))
        raise err
      open_apps_list = self.clean_list(items, open_apps_list)
      open_apps = pd.DataFrame(open_apps_list, columns=items)
      app_names = [""] * open_apps.shape[0]
      for ind in range(open_apps.shape[0]):
        desc_candidates = self.get_app_candidates(open_apps.loc[ind].Description)
        title_candidates = self.get_app_candidates(open_apps.loc[ind].MainWindowTitle)
        path_candidates = self.get_app_candidates(open_apps.loc[ind].Path)
        matches = match_candidates(match_candidates(desc_candidates, title_candidates), path_candidates)
        if (not all (matches == np.zeros(len(matches)))):
          appInd = np.argmax(matches)
          app_names[ind] = (self.apps.index[appInd])
      open_apps.insert(1, "App", app_names)
      self.add_open_apps_command_to_apps(open_apps)
      open_apps = await self.get_open_folders(open_apps)
      # change start time to date object, and add end time field:
      try:
        start_time = open_apps.assign(
          start_time = lambda dataframe: dataframe["StartTime"].map(lambda timeStr: dateutil.parser.parse(timeStr).isoformat())
        )
      except Exception as err:
        print("Apps handler failed to parse start time field, with error: " + str(err))
        raise err
      open_apps.update(start_time)
      open_apps.insert(len(items), "EndTime", [""] * open_apps.shape[0])
      return open_apps
    else: return unknown_OS_Warning()

  # cleans the list because sometimes powershell returns moved rows in the table.
  def clean_list(self, items, appsList):
    clean_list = []
    start_time_ind = items.index("StartTime")
    for row in appsList:
      if not row[start_time_ind][0].isdigit():
        first_digit = [c.isdigit() for c in row[start_time_ind]].index(True)
        for ind in np.arange(start_time_ind, len(items)):
          row[ind - 1] += row[ind][:first_digit]
          row[ind - 1] = row[ind - 1].strip()
          row[ind] = row[ind][first_digit:]
      clean_list.append(row)
    return clean_list

  # Checks which apps are suitable for this item
  def get_app_candidates(self, item):
    if item == "": return []
    return list(map(lambda name: find_words_in_string(item, name) + find_words_in_string(name, item), self.apps.index))

  def get_top_app(self):
    if self.os == "windows":
      print("need to get the top window")
      # use the cpp program using windows SDK
    else: return unknown_OS_Warning()

  def add_open_apps_command_to_apps(self, open_apps):
    for ind in range(open_apps.shape[0]):
      if (open_apps.App.loc[ind] == ""): continue
      if (self.apps.path.loc[open_apps.App.loc[ind]] == None):
        self.apps.path.loc[open_apps.App.loc[ind]] = open_apps.Path.loc[ind]

  async def get_open_folders(self, open_apps):
    explorer_row = open_apps.loc[open_apps["Name"] == "explorer"]
    open_apps = open_apps[open_apps["Name"] != "explorer"]
    open_folders = await self.explorer.get_open_explorers(explorer_row)
    open_apps = open_apps.append(open_folders)
    open_apps.reset_index(drop=True, inplace=True)
    return open_apps

if __name__ == '__main__':
  apps_handler = AppsHandler()
  asyncio.run(apps_handler.get_apps())
  open_apps = asyncio.run(apps_handler.get_open_apps())
  print("open apps:")
  print(open_apps)
