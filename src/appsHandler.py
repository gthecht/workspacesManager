import sys
import subprocess as Subprocess
import numpy as np
import pandas as pd
import powershellClient as PSClient
import dateutil.parser

def findWordsinString(wordStr, string):
  words = wordStr.split()
  appear = list(filter(lambda word: word.lower() in string.lower(), words))
  return len(appear)

def matchCandidates(list1, list2):
  if not len(list1): return list2
  elif not len(list2): return list1
  else:
    return np.multiply(np.add(list1, list2), np.multiply([weight > 0 for weight in list1], [weight > 0 for weight in list2]))

#%% AppsHandler class:
class AppsHandler:
  def __init__(self):
    if "win" in sys.platform: self.os = "windows"
    elif "linux" in sys.platform: self.os = "linux"
    else: raise TypeError("unknown system platform", sys.platform)
    if self.os == "windows": self.STARTPATH = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\"
    self.getApps()
    print("apps handler constructed")

  def getApps(self):
    print("Initializing apps with the start shortcuts")
    startApps = PSClient.getPSTable("Get-StartApps", ["Name"])
    startApps = [app[0] for app in startApps]
    appsTable = PSClient.getPSTable("Get-ChildItem \"" + self.STARTPATH + "*\" -Recurse | where { ! $_.PSIsContainer }", ["Name", "FullName"])

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
        openAppsList = PSClient.getPSTable("Get-Process | Where-Object { $_.MainWindowHandle -ne 0}", items)
      except Exception as err:
        print("Powershell client failed to get open apps with error: " + str(err))
        raise err
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
    else: return self.unknownOSWarning()

  # Checks which apps are suitable for this item
  def getAppCandidates(self, item):
    if item == "": return []
    return list(map(lambda name: findWordsinString(item, name) + findWordsinString(name, item), self.apps.index))

  def getTopApp(self):
    if self.os == "windows":
      print("need to get the top window")
    else: return self.unknownOSWarning()

  def unknownOSWarning(self):
    # need to make it work for linux
    raise TypeError("unknown system platform", sys.platform)

  def addOpenAppsCommandtoApps(self, openApps):
    for ind in range(openApps.shape[0]):
      if (openApps.App.loc[ind] == ""): continue
      if (self.apps.path.loc[openApps.App.loc[ind]] == None):
        self.apps.path.loc[openApps.App.loc[ind]] = openApps.Path.loc[ind]

if __name__ == '__main__':
  appsHandler = AppsHandler()
  openApps = appsHandler.getOpenApps()
  print("open apps:")
  print(openApps)
