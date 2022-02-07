from rarian.unknownOSWarning import unknown_OS_Warning
from rarian import powershellClient as PSClient
import os
import sys
import pandas as pd
from datetime import datetime

parent = os.path.abspath('./src')
sys.path.insert(1, parent)


# %% FilesGatherer class:

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

    def get_open_files(self, paths, start_time):
        """Get the childitems of the given project"""
        if paths is None:
            return pd.DataFrame()
        if self.os == "windows":
            open_files = self.get_files_from_powershell(paths, start_time)
            return open_files
        else:
            return unknown_OS_Warning()

    def get_path_item(self, path, start_time):
        cmd = "Get-Item '" + path + \
            "' -ErrorAction silentlycontinue " + \
            "| Where-Object { $_.LastAccessTime -gt \"" + \
            start_time + "\"}"
        return PSClient.get_PS_table_from_list(cmd, self.items)

    def get_files_from_powershell(self, paths, start_time):
        if type(start_time) == datetime:
            start_time = start_time.isoformat()
        child_items = []
        for path in paths:
            child_items.extend(self.get_path_item(path, start_time))
            cmd = "Get-ChildItem '" + os.path.join(path, "*'") + \
                  " -ErrorAction silentlycontinue " + \
                  "| Where-Object { $_.LastAccessTime -gt \"" + \
                  start_time + "\"}"
            new_child_items = PSClient.get_PS_table_from_list(cmd, self.items)
            child_items.extend(new_child_items)
        open_files = pd.DataFrame(child_items, columns=self.items)
        open_files = PSClient.parse_time(
            open_files, ["LastWriteTime", "LastAccessTime"]
        )
        return open_files
