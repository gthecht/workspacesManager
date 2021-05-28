from apps.appsHandler import AppsHandler

class HandlersManager:
  def __init__(self):
    self.appsHandler = AppsHandler()

  def gather(self):
    self.openApps = self.appsHandler.getOpenApps()
    return self.openApps

if __name__ == '__main__':
  handlersManager = HandlersManager()
  data = handlersManager.gather()
  print("DATA:")
  print(data)
