import os
import sys
import pandas as pd
parent = os.path.abspath('./src')
sys.path.insert(1, parent)
import powershellClient as PSClient
import unknownOSWarning

class Explorer:
  def __init__(self) -> None:
    if "win" in sys.platform: self.os = "windows"
    elif "linux" in sys.platform: self.os = "linux"
    else: raise TypeError("unknown system platform", sys.platform)
    if self.os == "windows": self.STARTPATH = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\"

  def get_open_directories(self):
    if self.os == "windows":
      cmd = '$a = New-Object -com "Shell.Application"; ' + \
            '$b = $a.windows() | select-object LocationURL, LocationName; ' + \
            '$b'
      items = ["LocationName", "LocationURL"]
      open_dirs_list = PSClient.getPSTable(cmd, items)
      return open_dirs_list
    else: return unknownOSWarning()

  def get_open_explorers(self, explorerRow):
      openDirs = pd.DataFrame([], columns=list(explorerRow.columns))
      open_dirs_list = self.get_open_directories()
      if len(open_dirs_list) == 0: return openDirs
      for dir in open_dirs_list:
        row = explorerRow.copy()
        row["Name"] = dir[0]
        row["MainWindowTitle"] = dir[0]
        row["Path"] = dir[1]
        openDirs = openDirs.append(row, ignore_index=True)
      return openDirs
