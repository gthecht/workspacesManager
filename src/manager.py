import sys
import os

from ui.cliClient import CLIent

project = os.path.abspath('./src/project')
sys.path.insert(1, project)
executor = os.path.abspath('./src/executor')
sys.path.insert(1, executor)
from projectsHandler import ProjectsHandler
from executor import Executor

gatherer = os.path.abspath('./src/gatherer')
sys.path.insert(1, gatherer)
from gatherer import Gatherer

class Manager:
  def __init__(self, paths, log_dir):
    self.get_os()
    self.log_dir = log_dir

    self.projects_handler = ProjectsHandler(paths, self.os)
    self.gatherer = Gatherer(self.log_dir,self.projects_handler, self.os)
    self.executor = Executor(self.projects_handler, self.os)
    self.client = CLIent(self.executor)

  # Get operating system:
  def get_os(self):
    if "win" in sys.platform: self.os = "windows"
    elif "linux" in sys.platform: self.os = "linux"
    else: raise TypeError("unknown system platform", sys.platform)

  def run(self):
    self.projects_handler.start()
    self.gatherer.start()
    self.client.start()
    self.projects_handler.join()
    self.gatherer.join()
    self.client.join()

  def save(self):
    self.executor.save()

  def get_apps(self):
    return self.executor.open()["apps"]

if __name__ == '__main__':
  import time
  t0 = time.perf_counter()
  log_dir = "C:/Users/GiladHecht/Workspace/workspacesManager/logs/"
  manager = Manager([os.path.abspath('.')], log_dir)
  manager.executor.set_current(name="workspacesManager")
  print("initialization took: ", time.perf_counter() - t0, "seconds")
  time.sleep(10)
  print("Gathering:")
  t1 = time.perf_counter()
  manager.run()
  print("Gathering took: ", time.perf_counter() - t1, "seconds")
  t2 = time.perf_counter()
  manager.save()
  print("Saving took: ", time.perf_counter() - t2, "seconds")
