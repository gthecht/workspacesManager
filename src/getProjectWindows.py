import json
import time
import pandas as pd
import appsHandler as AppsHandler

class Clusterizer:
  def __init__(self, dataPath):
    with open(dataPath) as jsonFile:
      self.projectData = json.load(jsonFile)

  # getCurrent gets us the current state - including the project, and the open apps. This will help us understand what app belongs to what project
  def getCurrent(self):
    currentProject = getCurrentProject()
    apps = getOpenApps()
    for app in apps:
      if app["name"] in self.projectData[currentProject].keys():
        self.projectData[currentProject][app["name"]]["weight"] += 1
      else:
        self.projectData[currentProject][app["name"]]["weight"] = 1
        # adds opening command to app:
        self.projectData[currentProject][app["name"]]["cmd"] = getCmd(app) # getCmd should be a function belonging to the AppsHandler class, the same as get OpenApps

  # getCurrentProject gets the current project name, and if it doesn't yet exist in the project data, adds it.
  def getCurrentProject(self):
    return "to be implemented"
