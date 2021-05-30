import sys

from apps.appsHandler import AppsHandler
from files.filesHandler import FilesHandler

class HandlersManager:
  def __init__(self):
    self.get_os()
    self.apps_handler = AppsHandler(self.os)
    self.files_handler = FilesHandler(self.os)

  # Get operating system:
  def get_os(self):
    if "win" in sys.platform: self.os = "windows"
    elif "linux" in sys.platform: self.os = "linux"
    else: raise TypeError("unknown system platform", sys.platform)

  def gather(self):
    self.openApps = self.apps_handler.getOpenApps()
    return self.openApps

if __name__ == '__main__':
  handlers_manager = HandlersManager()
  data = handlers_manager.gather()
  print("DATA:")
  print(data)
