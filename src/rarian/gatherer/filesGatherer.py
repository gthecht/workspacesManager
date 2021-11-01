import os
import sys
import pandas as pd
from datetime import datetime

parent = os.path.abspath('./src')
sys.path.insert(1, parent)

from rarian import powershellClient as PSClient
from rarian.unknownOSWarning import unknown_OS_Warning

#%% FilesGatherer class:
class FilesGatherer:
  def __init__(self, os="windows"):
    self.os = os
    self.items = [
      "Name",
      "LastWriteTime",
      "LastAccessTime",
      "Extension",
      "Directory",
      "FullName"
    ]
    # print("files handler constructed")

  def get_open_files(self, paths, start_time):
    """Get the childitems of the given project"""
    if paths is None: return pd.DataFrame()
    if self.os == "windows":
      open_files = self.get_files_from_powershell(paths, start_time)
      return open_files
    else: return unknown_OS_Warning()

  def get_files_from_powershell(self, paths, start_time):
    if type(start_time) == datetime:
      start_time = start_time.isoformat()
    child_items = []
    for path in paths:
      cmd = "Get-ChildItem " + path + \
            " -Recurse -ErrorAction silentlycontinue " + \
            "| Where-Object { $_.LastAccessTime -gt \"" + \
            start_time + "\"}"
      new_child_items = PSClient.get_PS_table_from_list(cmd, self.items)
      for child_item in new_child_items:
        child_items.append(child_item)
    open_files = pd.DataFrame(child_items, columns=self.items)
    # parse time fields:
    open_files = PSClient.parse_time(
      open_files, ["LastWriteTime", "LastAccessTime"]
    )
    return open_files
