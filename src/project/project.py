from datetime import date, datetime
import os
import sys
import pandas as pd
import numpy as np
import json

parent = os.path.abspath('./src')
sys.path.insert(1, parent)
import powershellClient as PSClient

class Project:

  # load existing project from some path
  def load(path):
    if not os.path.isdir(os.path.join(path, ".rarian")):
      raise FileNotFoundError("Path != a rarian project")
    data_path = os.path.join(path, ".rarian", "data.json")
    with open(data_path, 'r') as files_csv:
      files_str = files_csv.read()
    data = json.loads(files_str)
    files = pd.read_csv(os.path.join(path, ".rarian", "files.csv"), index_col=0)
    files.fillna('', inplace=True)
    project = Project(
      data["paths"],
      data["name"],
      data["type"],
      data["author"],
      datetime.fromisoformat(data["start_time"]),
      data["dirs"],
      files,
      data["apps"]
    )
    return project

  def __init__(
    self,
    paths,
    name=None,
    proj_type=None,
    author=None,
    start_time=datetime.now(),
    dirs=None,
    files=None,
    apps=[],
    forget_rate=0.99,
    add_rate=1.1
  ):
    self.paths = paths
    self.name = name
    if name == None: self.name = paths[0] # change later to just the directory
    self.author = author
    self.type = proj_type
    self.start_time = start_time
    self.forget_rate = forget_rate
    self.add_rate = add_rate

    # files and apps:
    self.file_items = [
      "Name",
      "LastWriteTime",
      "LastAccessTime",
      "Extension",
      "Directory",
      "FullName"
    ]
    if dirs is None: self.get_directories()
    else: self.dirs = dirs
    if files is None: self.get_files()
    else: self.files = files
    self.apps = apps
    self.open_files = []
    self.open_apps = []

  def path(self):
    return self.paths[0]

  def get_files(self):
    child_items = []
    for path in self.paths:
      cmd = "Get-ChildItem " + path + \
            " -Recurse -ErrorAction silentlycontinue"
      new_child_items = PSClient.get_PS_table(cmd, self.file_items)
      for child_item in new_child_items:
        child_items.append(child_item)
    self.files = pd.DataFrame(child_items, columns=self.file_items)
    # parse time fields:
    self.files = PSClient.parse_time(
      self.files, ["LastWriteTime", "LastAccessTime"]
    )
    # Add columns to files:
    self.files["Relevance"] = 1
    self.files["Open"] = False
    self.files["Type"] = [ext.split(".")[-1] for ext in self.files["Extension"]]
    self.files["Type"].mask(self.files["Directory"] == "", "dir", inplace=True)
    # The directory's directory will be itself:
    self.files["Directory"].mask(self.files["Directory"] == "", \
      self.files["FullName"], inplace=True)
    self.files.set_index("FullName", inplace=True)

  # get directories:
  def get_directories(self):
    self.dirs = self.paths.copy()
    for path in self.paths:
      cmd = "Get-ChildItem " + path + \
            " -Directory -Recurse -ErrorAction silentlycontinue"
      new_child_items = PSClient.get_PS_table(cmd, ["FullName"])
      for child_item in new_child_items:
        if child_item not in self.paths:
          self.dirs.append(child_item[0])

  def save(self):
    data_dict = {
      "paths": self.paths,
      "name": self.name,
      "type": self.type,
      "author": self.author,
      "start_time": self.start_time.isoformat(),
      "dirs": self.dirs,
      "apps": self.apps
    }
    if not os.path.exists(os.path.abspath('.rarian')):
      try:
        os.makedirs(os.path.abspath('.rarian'))
      except OSError as err: # Guard against race condition
        raise err

    with open('.rarian/data.json', 'w') as data_file:
      json.dump(data_dict, data_file, sort_keys=True, indent=2)
    self.files.to_csv('.rarian/files.csv')
    # self.apps.to_csv('.librarian/files.csv')

  # remove some subdirectory and all its children from files
  def remove_sub_directory(self, sub_dir):
    self.dirs = list(filter(lambda dir: sub_dir not in dir, self.dirs))
    self.files = self.files[[sub_dir not in directory for directory in self.files["Directory"]]]
    # self.files.reset_index(drop=True, inplace=True)

  def update(self, open_files, open_apps):
    if open_files.index.name != "FullName":
      open_files.set_index("FullName", inplace=True)
    # if "FullName" not in open_files.index.names:
      # open_files.set_index("FullName", inplace=True)
    self.open_files = open_files
    self.open_apps = open_apps
    self.files_update()
    self.apps_update()
    self.forget()

  def files_update(self):
    # find common files in open_files and self.files:
    common_files = list((set(self.files.index) & set(self.open_files.index)))
    # update relevance
    for fileName in common_files:
      self.files.loc[fileName]["LastWriteTime"] = \
        self.open_files[fileName]["LastWriteTime"]
      self.files.loc[fileName]["LastAccessTime"] = \
        self.open_files[fileName]["LastAccessTime"]
      self.files.loc[fileName]["Relevance"] *= self.add_rate
      self.files.loc[fileName]["Open"] = True

  def apps_update(self):
    pass

  def forget(self):
    self.files["Relevance"] *= self.forget_rate
    # self.apps["Relevance"] *= self.forget_rate

  def turn_off(self):
    # MAKE ALL FILES CLOSED - we may want to write them as open so that next time we can open them immediately
    # self.files["Open"] = False

    # CLOSE APPS - this is more complicated, may return project apps, and all
    # apps not used by the next project should be closed

    # SAVE FILES:
    self.save()
    self.end_time = datetime.now() # Not sure if I need this

  def turn_on(self):
    # We may want to save the previous information somewhere, but that's not
    # important
    self.start_time = datetime.now()


if __name__ == '__main__':
  project = Project([os.path.abspath('.')], "workspacesManager", "test", "giladH")
  project.remove_sub_directory("C:/Users/GiladHecht/Workspace/workspacesManager/src")
  project.save()
  load_project = Project.load(os.path.abspath('.'))
  print("files:", project.files.equals(load_project.files))
  print("paths:", project.paths == load_project.paths)
  print("name:", project.name == load_project.name)
  print("type:", project.type == load_project.type)
  print("author:", project.author == load_project.author)
  print("start_time:", project.start_time == load_project.start_time)
  print("dirs:", project.dirs == load_project.dirs)
  print("apps:", project.apps == load_project.apps)

  try:
    load_project = Project.load("C:/Users/GiladHecht")
  except FileNotFoundError as err:
    print("Test succeeded:", err)
  print("tests complete")
