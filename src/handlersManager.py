from datetime import datetime
import sys

from apps.appsHandler import AppsHandler
from files.filesHandler import FilesHandler
from project.projectsHandler import ProjectsHandler

class HandlersManager:
  def __init__(self, paths):
    self.get_os()
    self.apps_handler = AppsHandler(self.os)
    self.files_handler = FilesHandler(self.os)
    self.projects_handler = ProjectsHandler(paths, self.os)

  # Get operating system:
  def get_os(self):
    if "win" in sys.platform: self.os = "windows"
    elif "linux" in sys.platform: self.os = "linux"
    else: raise TypeError("unknown system platform", sys.platform)

  def gather(self):
    print("  open files...")
    project_paths = self.projects_handler.get_proj_paths()
    project_time = self.projects_handler.get_proj_start_time()
    self.open_files = self.files_handler.get_open_files(project_paths, project_time)
    print("  open apps...")
    self.open_apps = self.apps_handler.get_open_apps()
    self.projects_handler.update(self.open_files, self.open_apps)
    return

  def save(self):
    self.projects_handler.save()

  def get_apps(self):
    return self.open_apps

if __name__ == '__main__':
  import os
  import time
  t0 = time.perf_counter()
  manager = HandlersManager([os.path.abspath('.')])
  manager.projects_handler.set_current(name="workspacesManager")
  print("initialization took: ", time.perf_counter() - t0, "seconds")
  time.sleep(10)
  print("Gathering:")
  t1 = time.perf_counter()
  manager.gather()
  print("Gathering took: ", time.perf_counter() - t1, "seconds")
  t2 = time.perf_counter()
  manager.save()
  print("Gathering took: ", time.perf_counter() - t2, "seconds")

