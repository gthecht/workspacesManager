import os
from rarian.manager import Manager

if __name__ == '__main__':
  data_dir = os.getenv('APPDATA') + "\\Rarian"
  manager = Manager(data_dir)
  manager.run()