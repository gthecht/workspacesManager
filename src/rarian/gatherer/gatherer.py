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
    self.SLEEP_TIME = 10 # time to sleep between data collection - note that gathering the apps takes about 2 seconds
    super().__init__(name="gatherer", daemon=True)

  def add_job(self, job):
    self.projects_handler.q.put(job)
    if "reply_q" not in job.keys(): return
    else:
      reply = None
      while self.reply_q.empty():
        if not self.running: return False
        continue
      reply = self.reply_q.get()
      return reply

  def run(self):
    self.running = True
    try:
      self.gather_files()
      self.gather_apps()
      job = {
        "method": "update",
        "args": {
          "open_files": self.open_files,
          "open_apps": self.open_apps
        },
      }
      self.add_job(job)

      self.apps = self.open_apps
    except Exception as err:
      print("Failed to gather data with err: " + str(err))
      print("Waiting a bit, and trying to gather again")
      sleep(self.SLEEP_TIME)
      return self.run()

    self.apps.to_csv(self.apps_log_file, index=False)
    while self.running:
      sleep(self.SLEEP_TIME)
      if not self.running: break
      try:
        self.gather_files()
        self.gather_apps()
        self.cross_files_apps()
        job = {
          "method": "update",
          "args": {
            "open_files": self.open_files,
            "open_apps": self.open_apps          },
        }
        self.add_job(job)

      except Exception as err:
        print("Failed to gather data with err: " + str(err))
        print("Waiting a bit, and trying to gather again")
        continue
      else:
        self.apps = self.apps_handler.compare_apps(self.open_apps, self.apps)
        self.apps.to_csv(self.apps_log_file, index=False)

  def gather_files(self):
    project_paths = self.projects_handler.get_proj_dirs()
    proj_paths_job = {
      "method": "get_proj_dirs",
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
    self.open_apps = self.apps_handler.get_open_apps()

  def cross_files_apps(self):
    cross_correlation = []
    for file_ind in self.open_files.index:
      file = self.open_files.loc[file_ind]
      for app_ind in self.open_apps.index:
        app = self.open_apps.loc[app_ind]
        if len(file.Name) == 0: continue
        if file.Name.lower() in app.MainWindowTitle.lower():
          cross_correlation.append({
            "FullName": file.FullName,
            "OpenTime": datetime.now(),
            "AppName": app.Path,
            "value": len(file.Name) / len(app.MainWindowTitle),
          })
    cross_correlation = pd.DataFrame(cross_correlation)
    # Take only the single file with the maximum value: - may want to change this to multiple later on
    cross_correlation = cross_correlation.loc[cross_correlation.groupby(['AppName'])['value'].idxmax()]
    self.open_files = self.open_files[self.open_files['FullName'].isin(cross_correlation.FullName)]

  def stop(self):
    self.running = False
    job = {
      "method": "stop",
      "args": {},
    }
    self.add_job(job)
