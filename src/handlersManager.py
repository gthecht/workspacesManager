from datetime import datetime
import sys
import asyncio

from gatherer.appsGatherer import AppsGatherer
from gatherer.filesGatherer import FilesGatherer
from project.projectsHandler import ProjectsHandler

class HandlersManager:
  def __init__(self, paths):
    self.get_os()
    self.apps_handler = AppsGatherer(self.os)
    self.files_handler = FilesGatherer(self.os)
    self.projects_handler = ProjectsHandler(paths, self.os)

  # Get operating system:
  def get_os(self):
    if "win" in sys.platform: self.os = "windows"
    elif "linux" in sys.platform: self.os = "linux"
    else: raise TypeError("unknown system platform", sys.platform)

  async def init(self):
    await self.apps_handler.get_apps()

  async def gather(self):
    await asyncio.gather(self.gather_files(), self.gather_apps())
    self.projects_handler.update(self.open_files, self.open_apps)
    return

  async def gather_files(self):
    print("  open files...")
    project_paths = self.projects_handler.get_proj_paths()
    project_time = self.projects_handler.get_proj_start_time()
    self.open_files = await self.files_handler.get_open_files(project_paths, project_time)

  async def gather_apps(self):
    print("  open apps...")
    self.open_apps = await self.apps_handler.get_open_apps()

  async def save(self):
    await self.projects_handler.save()

  def get_apps(self):
    return self.open_apps

if __name__ == '__main__':
  import os
  import time
  t0 = time.perf_counter()
  manager = HandlersManager([os.path.abspath('.')])
  asyncio.run(manager.init())
  manager.projects_handler.set_current(name="workspacesManager")
  print("initialization took: ", time.perf_counter() - t0, "seconds")
  time.sleep(10)
  print("Gathering:")
  t1 = time.perf_counter()
  asyncio.run(manager.gather())
  print("Gathering took: ", time.perf_counter() - t1, "seconds")
  t2 = time.perf_counter()
  asyncio.run(manager.save())
  print("Saving took: ", time.perf_counter() - t2, "seconds")

