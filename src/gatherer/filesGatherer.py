import os
import sys
import pandas as pd
from datetime import datetime
import asyncio

parent = os.path.abspath('./src')
sys.path.insert(1, parent)
import powershellClient as PSClient
from unknownOSWarning import unknown_OS_Warning
from project.project import Project

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
    print("files handler constructed")

  # Get the childitems of the given project
  async def get_open_files(self, paths, start_time):
    if paths is None: return pd.DataFrame()
    if type(start_time) == datetime:
      start_time = start_time.isoformat()
    if self.os == "windows":
      open_files = await self.get_files_from_powershell(paths, start_time)
      return open_files
    else: return unknown_OS_Warning()

  async def get_files_from_powershell(self, paths, start_time):
    child_items = []
    for path in paths:
      cmd = "Get-ChildItem " + path + \
            " -Recurse -ErrorAction silentlycontinue " + \
            "| Where-Object { $_.LastAccessTime -gt \"" + \
            start_time + "\"}"
      new_child_items = await PSClient.get_PS_table(cmd, self.items)
      for child_item in new_child_items:
        child_items.append(child_item)
    open_files = pd.DataFrame(child_items, columns=self.items)
    # parse time fields:
    open_files = await PSClient.parse_time(
      open_files, ["LastWriteTime", "LastAccessTime"]
    )
    return open_files

if __name__ == '__main__':
  now = datetime.now().isoformat()[:10]
  files_handler = FilesGatherer()
  open_files = asyncio.run(files_handler.get_open_files([os.path.abspath('.')], now))
  print("open files:")
  print(open_files)