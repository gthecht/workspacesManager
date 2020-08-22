from time import sleep
from datetime import datetime
from handlersManager import HandlersManager
import pandas as pd
import numpy as np

class Gatherer:
  def __init__(self, logDir):
    self.logDir = logDir
    self.handlersManager = HandlersManager()
    self.run = False
    self.logFile = self.logDir + "log-" + datetime.now().strftime('%Y-%m-%dT%H-%M-%S') + ".csv"
    self.SLEEP_TIME = 30 # time to sleep between data collection - note that gathering the apps takes about 2 seconds

  def gather(self):
    self.run = True
    try:
      self.data = self.handlersManager.gather()
    except Exception as err:
      print("Failed to gather data with err: " + str(err))
      print("Waiting a bit, and trying to gather again")
      sleep(self.SLEEP_TIME)
      return self.gather()

    self.data.to_csv(self.logFile, index=False)
    while self.run:
      sleep(self.SLEEP_TIME)
      print("Gathering data")
      try:
        data = self.handlersManager.gather()
      except Exception as err:
        print("Failed to gather data with err: " + str(err))
        print("Waiting a bit, and trying to gather again")
        continue
      else:
        self.compareData(data)
        self.data.to_csv(self.logFile, index=False)

  def compareData(self, data):
    # find rows from the old that are duplicated in the new:
    concatDf = pd.concat([data, self.data], ignore_index=True)
    duplicated = concatDf.duplicated()
    ended = [not dup for dup in duplicated[len(data):]] # these are the old apps that have ended
    now = datetime.now().isoformat()
    for ind in [i for i, e in enumerate(ended) if e]:
      if concatDf.loc[ind + len(data.index)]["EndTime"] == "":
        concatDf.loc[ind + len(data.index)]["EndTime"] = now
    self.data = concatDf.drop_duplicates().sort_values(["App", "Name", "StartTime", "EndTime"], ignore_index=True)

  def stop(self):
    self.run = False

if __name__ == '__main__':
  gatherer = Gatherer("D:/Workspace/workspacesManager/logs/")
  gatherer.gather()
