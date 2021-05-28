import os
import sys
import pandas as pd
from datetime import datetime

parent = os.path.abspath('./src')
sys.path.insert(1, parent)
import powershellClient as PSClient
import unknownOSWarning
from project.project import Project
from apps.explorer import Explorer

#%% FilesHandler class:
class FilesHandler:
  def __init__(self):
    self.get_os()
    self.items = [
      "Name",
      "LastWriteTime",
      "LastAccessTime",
      "Extension",
      "Directory",
      "FullName"
    ]
    print("files handler constructed")

  # Get operating system:
  def get_os(self):
    if "win" in sys.platform: self.os = "windows"
    elif "linux" in sys.platform: self.os = "linux"
    else: raise TypeError("unknown system platform", sys.platform)

  # Get the childitems of the given project
  def get_open_files(self, paths, start_time):
    if paths is None: return pd.DataFrame()
    if type(start_time) == datetime:
      start_time = start_time.isoformat()
    if self.os == "windows":
      open_files = self.get_files_from_powershell(paths, start_time)
      return open_files
    else: return unknownOSWarning()

  def get_files_from_powershell(self, paths, start_time):
    child_items = []
    for path in paths:
      cmd = "Get-ChildItem " + path + \
            " -Recurse -ErrorAction silentlycontinue " + \
            "| Where-Object { $_.LastAccessTime -gt \"" + \
            start_time + "\"}"
      new_child_items = PSClient.getPSTable(cmd, self.items)
      for child_item in new_child_items:
        child_items.append(child_item)
    open_files = pd.DataFrame(child_items, columns=self.items)
    # parse time fields:
    open_files = PSClient.parseTime(
      open_files, ["LastWriteTime", "LastAccessTime"]
    )
    return open_files

if __name__ == '__main__':
  now = datetime.now().isoformat()[:10]
  proj = Project([os.path.abspath('.')], now)
  files_handler = FilesHandler()
  open_files = files_handler.get_files(proj)
  print("open files:")
  print(open_files)