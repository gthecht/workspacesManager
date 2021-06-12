import os
import sys
import numpy as np
import pandas as pd
import dateutil.parser

parent = os.path.abspath('./src')
sys.path.insert(1, parent)
import powershellClient as PSClient
from unknownOSWarning import unknown_OS_Warning
from apps.explorer import Explorer

def findWordsinString(wordStr, string):
  words = wordStr.split()
  appear = list(filter(lambda word: word.lower() in string.lower(), words))
  return len(appear) / len(words)

def matchCandidates(list1, list2):
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
    self.getApps()
    print("apps handler constructed")

  def getApps(self):
    print("Initializing apps with the start shortcuts")
    startApps = PSClient.get_PS_table("Get-StartApps", ["Name"])
    startApps = [app[0] for app in startApps]
    appsTable = PSClient.get_PS_table("Get-ChildItem \"" + self.STARTPATH + "*\" -Recurse | where { ! $_.PSIsContainer }", ["Name", "FullName"])

    appsList = []
    candidates = []
    path = []
    for app in startApps:
      if app not in appsList:
        appsList.append(app)
        candidList = list(filter(lambda row: app in row[0], appsTable))
        candidates.append([row[1] for row in candidList])
        if candidates[-1] == []: path.append(None)
        else: path.append(candidates[-1][0])
    appsDict = {
      "path": path,
      "pathCandidates": candidates
    }
    self.apps = pd.DataFrame(appsDict, index=appsList,columns=["path", "pathCandidates"])

  def getOpenApps(self):
    if self.os == "windows":
      items = ["Id", "Name", "Description", "MainWindowTitle", "StartTime", "Path"]
      try:
        openAppsList = PSClient.get_PS_table("Get-Process | Where-Object { $_.MainWindowHandle -ne 0}", items)
      except Exception as err:
        print("Powershell client failed to get open apps with error: " + str(err))
        raise err
      openAppsList = self.cleanList(items, openAppsList)
      openApps = pd.DataFrame(openAppsList, columns=items)
      appNames = [""] * openApps.shape[0]
      for ind in range(openApps.shape[0]):
        descCandidates = self.getAppCandidates(openApps.loc[ind].Description)
        titleCandidates = self.getAppCandidates(openApps.loc[ind].MainWindowTitle)
        pathCandidates = self.getAppCandidates(openApps.loc[ind].Path)
        matches = matchCandidates(matchCandidates(descCandidates, titleCandidates), pathCandidates)
        if (not all (matches == np.zeros(len(matches)))):
          appInd = np.argmax(matches)
          appNames[ind] = (self.apps.index[appInd])
      openApps.insert(1, "App", appNames)
      self.addOpenAppsCommandtoApps(openApps)
      openApps = self.getOpenFolders(openApps)
      # change start time to date object, and add end time field:
      try:
        StartTime = openApps.assign(
          StartTime = lambda dataframe: dataframe["StartTime"].map(lambda timeStr: dateutil.parser.parse(timeStr).isoformat())
        )
      except Exception as err:
        print("Apps handler failed to parse start time field, with error: " + str(err))
        raise err
      openApps.update(StartTime)
      openApps.insert(len(items), "EndTime", [""] * openApps.shape[0])
      return openApps
    else: return unknown_OS_Warning()

  # cleans the list because sometimes powershell returns moved rows in the table.
  def cleanList(self, items, appsList):
    cleanList = []
    startTimeInd = items.index("StartTime")
    for row in appsList:
      if not row[startTimeInd][0].isdigit():
        firstDigit = [c.isdigit() for c in row[startTimeInd]].index(True)
        for ind in np.arange(startTimeInd, len(items)):
          row[ind - 1] += row[ind][:firstDigit]
          row[ind - 1] = row[ind - 1].strip()
          row[ind] = row[ind][firstDigit:]
      cleanList.append(row)
    return cleanList

  # Checks which apps are suitable for this item
  def getAppCandidates(self, item):
    if item == "": return []
    return list(map(lambda name: findWordsinString(item, name) + findWordsinString(name, item), self.apps.index))

  def getTopApp(self):
    if self.os == "windows":
      print("need to get the top window")
      # use the cpp program using windows SDK
    else: return unknown_OS_Warning()

  def addOpenAppsCommandtoApps(self, openApps):
    for ind in range(openApps.shape[0]):
      if (openApps.App.loc[ind] == ""): continue
      if (self.apps.path.loc[openApps.App.loc[ind]] == None):
        self.apps.path.loc[openApps.App.loc[ind]] = openApps.Path.loc[ind]

  def getOpenFolders(self, openApps):
    explorerRow = openApps.loc[openApps["Name"] == "explorer"]
    openApps = openApps[openApps["Name"] != "explorer"]
    openFolders = self.explorer.get_open_explorers(explorerRow)
    openApps = openApps.append(openFolders)
    openApps.reset_index(drop=True, inplace=True)
    return openApps

if __name__ == '__main__':
  appsHandler = AppsHandler()
  openApps = appsHandler.getOpenApps()
  print("open apps:")
  print(openApps)
