import sys
import os
import json
from time import sleep


src = os.path.abspath('./src')
from rarian.ui.cliClient import CLIent
from rarian.project.projectsHandler import ProjectsHandler
from rarian.executor.executor import Executor
from rarian.gatherer.gatherer import Gatherer

class Manager:
  def __init__(self, data_dir):
    self.get_os()
    self.data_dir = data_dir
    self.log_dir = os.path.join(data_dir, "logs")
    self.load_data()

    self.projects_handler = ProjectsHandler(self.data_file, self.os)
    self.gatherer = Gatherer(self.log_dir,self.projects_handler, self.os)
    self.executor = Executor(self.projects_handler, self.os)
    self.client = CLIent(self.executor)

  # Get operating system:
  def get_os(self):
    if "win" in sys.platform: self.os = "windows"
    elif "linux" in sys.platform: self.os = "linux"
    else: raise TypeError("unknown system platform", sys.platform)

  # Load project data:
  def load_data(self):
    self.data_file = os.path.join(self.data_dir, "data.json")
    with open(self.data_file, 'r') as data_json:
      data_str = data_json.read()
    data = json.loads(data_str)
    self.projects = data["projects"]

  def run(self):
    self.projects_handler.start()
    self.gatherer.start()
    self.client.start()
    self.projects_handler.join()
    self.gatherer.join()
    self.client.join()
    self.save()

  def save(self):
    while True:
      sleep(30)
      self.executor.save()

  def get_apps(self):
    return self.executor.open()["apps"]

if __name__ == '__main__':
  import time
  t0 = time.perf_counter()
  data_dir = "C:/Users/GiladHecht/Workspace/workspacesManager/appData"
  manager = Manager(data_dir)
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
