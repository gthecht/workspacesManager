from rarian.unknownOSWarning import unknown_OS_Warning
from rarian import powershellClient as PSClient
import os
import sys
import pandas as pd
parent = os.path.abspath('./src')
sys.path.insert(1, parent)


class Explorer:
    def __init__(self, os="windows") -> None:
        self.os = os
        if self.os == "windows":
            self.STARTPATH = \
                "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\"

    def get_open_directories(self):
        if self.os == "windows":
            cmd = '$a = New-Object -com "Shell.Application"; ' + \
                  '$b = $a.windows() | select-object LocationURL, ' + \
                  'LocationName; $b'
            items = ["LocationName", "LocationURL"]
            open_dirs_list = PSClient.get_PS_table_from_list(cmd, items)
            return open_dirs_list
        else:
            return unknown_OS_Warning()

    def get_open_explorers(self, explorer_row):
        open_dirs = pd.DataFrame([], columns=list(explorer_row.columns))
        open_dirs_list = self.get_open_directories()
        if len(open_dirs_list) == 0:
            return open_dirs
        for dir in open_dirs_list:
            if dir[0] in list(explorer_row.MainWindowTitle):
                ind = [ind for ind in explorer_row.index if dir[0]
                       == explorer_row.loc[ind].MainWindowTitle][0]
            else:
                ind = [ind for ind in explorer_row.index if '' ==
                       explorer_row.loc[ind].MainWindowTitle][0]
            row = explorer_row.loc[ind].copy()
            row.Name = 'File Explorer'
            row.MainWindowTitle = f'{dir[0]} - File Explorer'
            row.Path = dir[1][8:]
            row.App = 'File Explorer'
            open_dirs = pd.concat([open_dirs, row], ignore_index=True)
        return open_dirs
