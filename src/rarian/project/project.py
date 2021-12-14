from datetime import datetime
import os
import sys
import pandas as pd
import numpy as np
import json

parent = os.path.abspath('./src')
sys.path.insert(1, parent)
from rarian import powershellClient as PSClient

class Project:
  # load existing project from some path
  def load(path):
    if not os.path.isdir(os.path.join(path, ".rarian")):
      raise FileNotFoundError("Path is not a rarian project")
    data_path = os.path.join(path, ".rarian", "data.json")
    with open(data_path, 'r') as data_file:
      data_str = data_file.read()
    data = json.loads(data_str)
    files = pd.read_csv(os.path.join(path, ".rarian", "files.csv"), index_col=0, dtype={"Relevance": np.float64})
    files.fillna('', inplace=True)
    project = Project(
      data["paths"],
      data["name"],
      data["type"],
      data["author"],
      datetime.fromisoformat(data["start_time"]),
      data["dirs"],
      files,
      data["apps"],
      data["removed_dirs"]
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
    removed_dirs=[],
    add_rate=10,
    forget_rate=100
  ):
    self.paths = [os.path.normpath(path) for path in paths]
    self.rarian_path = os.path.join(self.paths[0], ".rarian")
    self.name = name
    if name == None: self.name = paths[0].split("\\")[-1]
    self.author = author
    self.type = proj_type
    self.start_time = start_time
    self.add_rate = add_rate
    self.forget_rate = forget_rate

    # files and apps:
    self.file_items = [
      "Name",
      "LastWriteTime",
      "LastAccessTime",
      "Extension",
      "Directory",
      "FullName"
    ]
    if files is None: self.get_files()
    else: self.files = files
    self.apps = apps
    self.removed_dirs = removed_dirs
    if dirs is None: self.dirs = self.paths.copy()
    else: self.dirs = dirs
    self.update_directories()
    self.open_files = []
    self.open_apps = []

  def path(self):
    return self.paths[0]

  def get_files(self):
    child_items = []
    for path in self.paths:
      cmd = "Get-ChildItem '" + path + \
            "' -Recurse -ErrorAction silentlycontinue"
      new_child_items = PSClient.get_PS_table_from_list(cmd, self.file_items)
      child_items.extend(new_child_items)
    self.files = pd.DataFrame(child_items, columns=self.file_items)
    # parse time fields:
    self.files = PSClient.parse_time(
      self.files, ["LastWriteTime", "LastAccessTime"]
    )
    # Add columns to files:
    self.files = self.file_add_columns(self.files)

  def file_add_columns(self, files):
    files["Relevance"] = 0
    files["Open"] = False
    files["Type"] = [ext.split(".")[-1] for ext in files["Extension"]]
    files["Type"].mask(files["Directory"] == "", "dir", inplace=True)
    # The directory's directory will be itself:
    if "FullName" not in files.columns: files.reset_index(inplace=True)
    files["Directory"].mask(files["Directory"] == "", \
      files["FullName"], inplace=True)
    files.set_index("FullName", inplace=True)
    return files

  # get directories:
  def update_directories(self):
    for path in self.paths:
      cmd = "Get-ChildItem '" + path + \
            "' -Directory -Recurse -ErrorAction silentlycontinue"
      new_child_items = PSClient.get_PS_table_from_list(cmd, ["FullName"])
      for child_item in new_child_items:
        child_item = child_item[0]
        if (child_item not in self.dirs) and (child_item not in self.removed_dirs):
          if "\\." in child_item:
            if "\\" in child_item.split("\\.")[1]: continue
            self.remove_sub_dir(child_item)
          elif "\\__" in child_item:
            if "\\" in child_item.split("\\__")[1]: continue
            self.remove_sub_dir(child_item)
          else: self.dirs.append(child_item)

  def get_open(self):
    open_data = {
      "files": self.open_files,
      "apps": self.open_apps
    }
    return open_data

  def save(self):
    data_dict = {
      "paths": self.paths,
      "name": self.name,
      "type": self.type,
      "author": self.author,
      "start_time": self.start_time.isoformat(),
      "dirs": self.dirs,
      "apps": self.apps,
      "removed_dirs": self.removed_dirs
    }
    if not os.path.exists(self.rarian_path):
      try:
        os.makedirs(self.rarian_path)
      except OSError as err: # Guard against race condition
        raise err

    with open(os.path.join(self.rarian_path, 'data.json'), 'w') as data_file:
      json.dump(data_dict, data_file, sort_keys=True, indent=2)
    self.files.to_csv(os.path.join(self.rarian_path, 'files.csv'))
    # self.apps.to_csv('.librarian/files.csv')

  # remove some subdirectory and all its children from files
  def remove_sub_dir(self, sub_dir):
    sub_dir = os.path.abspath(sub_dir)
    self.removed_dirs.append(sub_dir)
    self.dirs = list(filter(lambda dir: sub_dir not in dir, self.dirs))
    self.files = self.files[[sub_dir not in directory for directory in self.files["Directory"]]]
    # self.files.reset_index(drop=True, inplace=True)

  def update(self, open_files, open_apps):
    if not open_files.empty and open_files.index.name != "FullName":
      open_files.set_index("FullName", inplace=True)
    self.open_files = open_files
    self.open_apps = open_apps
    self.files_update()
    self.apps_update()
    self.update_directories()
    self.forget()

  def dirs_update(self, dirs):
    self.dirs = dirs["dirs"]
    self.removed_dirs = dirs["removed_dirs"]

  def files_update(self):
    self.files_update_open()
    self.files_update_closed()

  def files_update_open(self):
    if self.open_files.empty: pass
    # find common files in open_files and self.files:
    common_files = list((set(self.files.index) & set(self.open_files.index)))

    new_file_names = list(set(self.open_files.index) - set(common_files))
    new_files = self.open_files.loc[new_file_names]
    if len(new_files) > 0:
      for sub_dir in self.removed_dirs:
        if new_files.empty: break
        new_files = new_files[[sub_dir not in directory for directory in new_files["Directory"]]]
      new_files = self.file_add_columns(new_files)
      if not new_files.empty:
        self.files = self.files.append(new_files)
        new_file_names = list(new_files.index)
      else:
        new_file_names = []
    common_files.extend(new_file_names)
    # update relevance
    for file_name in common_files:
      self.files.at[file_name, "LastWriteTime"] = \
        self.open_files.at[file_name, "LastWriteTime"]
      self.files.at[file_name, "LastAccessTime"] = \
        self.open_files.at[file_name, "LastAccessTime"]
      self.files.at[file_name, "Relevance"] = self.update_relevance(self.update_relevance(
        self.files.at[file_name, "Relevance"], 'UP'
      ), 'UP')
      self.files.at[file_name, "Open"] = True

  def files_update_closed(self):
    open_files = self.files[self.files["Open"] == True]
    if open_files.empty: return
    still_open = list((set(open_files.index) & set(self.open_files.index)))
    closed = list(set(open_files.index) - set(still_open))
    for closed_file in closed:
      self.files.at[closed_file, "Open"] = False

  def apps_update(self):
    if self.open_apps.empty: pass
    pass

  def forget(self):
    self.files["Relevance"] = self.files["Relevance"].apply(lambda rel: self.update_relevance(rel, 'DOWN'))
    # do the same for apps

  def update_relevance(self, relevance, direction='UP'):
    assert relevance >= 0 and relevance <= 1
    if direction == 'UP':
      return 1 - self.add_rate * (1 - relevance) / (1 - relevance + self.add_rate)
    elif direction == 'DOWN':
      return self.forget_rate * relevance / (relevance + self.forget_rate)
    else: raise ValueError('up_down must be UP or DOWN')

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
