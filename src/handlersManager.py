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
    project_paths = self.projects_handler.get_proj_paths()
    project_time = self.projects_handler.get_proj_start_time()
    self.open_files = self.files_handler.get_open_files(project_paths, project_time)
    self.open_apps = self.apps_handler.getOpenApps()
    return self.open_apps, self.open_files

if __name__ == '__main__':
  import os
  handlers_manager = HandlersManager([os.path.abspath('.')])
  data = handlers_manager.gather()
  print("DATA:")
  print(data)
