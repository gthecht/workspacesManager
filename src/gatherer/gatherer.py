from datetime import datetime
import pandas as pd

# from time import sleep
from asyncio import sleep
import asyncio
import os
import sys

from appsGatherer import AppsGatherer
from filesGatherer import FilesGatherer
parent = os.path.abspath('./src')
sys.path.insert(1, parent)
from project.projectsHandler import ProjectsHandler


class Gatherer:
  def __init__(self, log_dir, paths, os="windows"):
    self.log_dir = log_dir
    self.os = os
    self.apps_handler = AppsGatherer(self.os)
    self.files_handler = FilesGatherer(self.os)
    self.projects_handler = ProjectsHandler(paths, self.os)

    self.run = False
    self.log_file = self.log_dir + "log-" + datetime.now().strftime('%Y-%m-%dT%H-%M-%S') + ".csv"
    self.SLEEP_TIME = 30 # time to sleep between data collection - note that gathering the apps takes about 2 seconds

  async def init(self):
    await self.apps_handler.get_apps()

  async def gather(self):
    self.run = True
    try:
      await asyncio.gather(self.gather_files(), self.gather_apps())
      self.projects_handler.update(self.open_files, self.open_apps)
      await self.projects_handler.save()
      self.data = self.open_apps
    except Exception as err:
      print("Failed to gather data with err: " + str(err))
      print("Waiting a bit, and trying to gather again")
      await asyncio.sleep(self.SLEEP_TIME)
      return await self.gather()

    self.data.to_csv(self.log_file, index=False)
    while self.run:
      await asyncio.sleep(self.SLEEP_TIME)
      print("Gathering data")
      try:
        await asyncio.gather(self.gather_files(), self.gather_apps())
        self.projects_handler.update(self.open_files, self.open_apps)
        await self.projects_handler.save()
        data = self.open_apps
      except Exception as err:
        print("Failed to gather data with err: " + str(err))
        print("Waiting a bit, and trying to gather again")
        continue
      else:
        self.compare_data(data)
        self.data.to_csv(self.log_file, index=False)

  async def gather_files(self):
    print("  open files...")
    project_paths = self.projects_handler.get_proj_paths()
    project_time = self.projects_handler.get_proj_start_time()
    self.open_files = await self.files_handler.get_open_files(project_paths, project_time)

  async def gather_apps(self):
    print("  open apps...")
    self.open_apps = await self.apps_handler.get_open_apps()

  def compare_data(self, data):
    # find rows from the old that are duplicated in the new:
    concat_df = pd.concat([data, self.data], ignore_index=True)
    duplicated = concat_df.duplicated(keep='first')
    ended = [not dup for dup in duplicated[len(data):]] # these are the old apps that have ended
    now = datetime.now().isoformat()[:-7]
    for ind in [i for i, e in enumerate(ended) if e]:
      if concat_df.loc[ind + len(data.index)]["EndTime"] == "":
        concat_df.loc[ind + len(data.index)]["EndTime"] = now

    duplicated_start = concat_df.duplicated(keep='last')
    started = [not dup for dup in duplicated_start[:len(data)]] # these are the new apps that have started
    for ind in [i for i, e in enumerate(started) if e]:
      concat_df.loc[ind]["StartTime"] = now
    self.data = concat_df.drop_duplicates().sort_values(["App", "Name", "StartTime", "EndTime"], ignore_index=True)

  def stop(self):
    self.run = False

if __name__ == '__main__':
  gatherer = Gatherer("C:/Users/GiladHecht/Workspace/workspacesManager/logs/", [os.path.abspath('.')])
  asyncio.run(gatherer.init())
  asyncio.run(gatherer.gather())
