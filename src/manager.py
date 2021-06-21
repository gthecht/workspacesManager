import sys
import os

project = os.path.abspath('./src/project')
sys.path.insert(1, project)
from projectsHandler import ProjectsHandler

gatherer = os.path.abspath('./src/gatherer')
sys.path.insert(1, gatherer)
from gatherer import Gatherer

class Manager:
  def __init__(self, paths, log_dir):
    self.get_os()
    self.log_dir = log_dir

    self.projects_handler = ProjectsHandler(paths, self.os)
    self.gatherer = Gatherer(self.log_dir,self.projects_handler, self.os)

  # Get operating system:
  def get_os(self):
    if "win" in sys.platform: self.os = "windows"
    elif "linux" in sys.platform: self.os = "linux"
    else: raise TypeError("unknown system platform", sys.platform)

  def gather(self):
    self.gatherer.gather()
    return

  def save(self):
    self.gatherer.save()

  def get_apps(self):
    return self.gatherer.open_apps

if __name__ == '__main__':
  import time
  t0 = time.perf_counter()
  log_dir = "C:/Users/GiladHecht/Workspace/workspacesManager/logs/"
  manager = Manager([os.path.abspath('.')], log_dir)
  manager.projects_handler.set_current(name="workspacesManager")
  print("initialization took: ", time.perf_counter() - t0, "seconds")
  time.sleep(10)
  print("Gathering:")
  t1 = time.perf_counter()
  manager.gather()
  print("Gathering took: ", time.perf_counter() - t1, "seconds")
  t2 = time.perf_counter()
  manager.save()
  print("Saving took: ", time.perf_counter() - t2, "seconds")

