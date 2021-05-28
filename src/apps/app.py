from subprocess import Popen, PIPE
import pandas as pd

import powershellClient as PSClient

class App:
  def __init__(self, name, processes):
    self.name = name
    self.processes = processes

if __name__ == '__main__':
  app = App("dfgh", "hdfgj")
