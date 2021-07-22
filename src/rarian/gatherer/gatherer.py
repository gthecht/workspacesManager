from time import sleep
from os import path
from datetime import datetime
import pandas as pd
import threading
import queue

from rarian.gatherer.appsGatherer import AppsGatherer
from rarian.gatherer.filesGatherer import FilesGatherer

class Gatherer(threading.Thread):
  def __init__(self, log_dir, projects_handler, os="windows"):
    self.log_dir = log_dir
    self.os = os
    self.apps_handler = AppsGatherer(self.os)
    self.files_handler = FilesGatherer(self.os)
    self.projects_handler = projects_handler
    self.reply_q = queue.Queue()

    self.running = False
    self.apps_log_file = path.join(self.log_dir, "log-" + datetime.now().strftime('%Y-%m-%dT%H-%M-%S') + ".csv")
    self.SLEEP_TIME = 30 # time to sleep between data collection - note that gathering the apps takes about 2 seconds
    super().__init__(name="gatherer", daemon=True)

  def add_job(self, job):
    self.projects_handler.q.put(job)
    if "reply_q" not in job.keys(): return
    else:
      reply = None
      while self.reply_q.empty():
        continue
      reply = self.reply_q.get()
      return reply

  def run(self):
    self.running = True
    try:
      self.gather_files()
      self.gather_apps()
      # self.projects_handler.update(self.open_files, self.open_apps)
      job = {
        "method": "update",
        "args": {
          "open_files": self.open_files,
          "open_apps": self.open_apps
        },
      }
      self.add_job(job)

      self.data = self.open_apps
    except Exception as err:
      print("Failed to gather data with err: " + str(err))
      print("Waiting a bit, and trying to gather again")
      sleep(self.SLEEP_TIME)
      return self.run()

    self.data.to_csv(self.apps_log_file, index=False)
    while self.running:
      sleep(self.SLEEP_TIME)
      # print("Gathering data")
      try:
        self.gather_files()
        self.gather_apps()
        # self.projects_handler.update(self.open_files, self.open_apps)
        job = {
          "method": "update",
          "args": {
            "open_files": self.open_files,
            "open_apps": self.open_apps
          },
        }
        self.add_job(job)

        data = self.open_apps
      except Exception as err:
        print("Failed to gather data with err: " + str(err))
        print("Waiting a bit, and trying to gather again")
        continue
      else:
        self.compare_data(data)
        self.data.to_csv(self.apps_log_file, index=False)

  def gather_files(self):
    # print("  open files...")
    project_paths = self.projects_handler.get_proj_paths()
    proj_paths_job = {
      "method": "get_proj_paths",
      "args": {},
      "reply_q": self.reply_q
    }
    self.add_job(proj_paths_job)
    project_time = self.projects_handler.get_proj_start_time()
    proj_time_job = {
      "method": "get_proj_start_time",
      "args": {},
      "reply_q": self.reply_q
    }
    self.add_job(proj_time_job)
    self.open_files = self.files_handler.get_open_files(project_paths, project_time)

  def gather_apps(self):
    # print("  open apps...")
    self.open_apps = self.apps_handler.get_open_apps()

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
    self.running = False

if __name__ == '__main__':
  import os
  import sys
  project = os.path.abspath('./src/project')
  sys.path.insert(1, project)
  from projectsHandler import ProjectsHandler

  projects_handler = ProjectsHandler([os.path.abspath('.')], "windows")
  gatherer = Gatherer("C:/Users/GiladHecht/Workspace/workspacesManager/logs/", projects_handler)
  projects_handler.start()
  gatherer.start()
  gatherer.join()
