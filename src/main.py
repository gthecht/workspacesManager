import os
from manager import Manager

if __name__ == '__main__':
  log_dir = os.getenv('APPDATA') + "\\Rarian\\logs\\"
  manager = Manager([os.path.abspath('.')], log_dir)
  manager.run()