import sys
import pytest
import pandas as pd
from datetime import datetime
from rarian.gatherer.appsGatherer import *
from rarian.gatherer.filesGatherer import FilesGatherer
from rarian.gatherer.gatherer import Gatherer

# constants:
if "win" in sys.platform: OS = "windows"
elif "linux" in sys.platform: OS = "linux"
else: raise TypeError("unknown system platform", sys.platform)

test_path_str = os.path.abspath("./test")
file_path_str = os.path.join(test_path_str, "src", "gatherer", "conftest.py")
projects_handler = {
  "q": {"list": [], "put": lambda el: projects_handler["q"]["list"].append(el)},
  "get_proj_paths": lambda : [test_path_str],
  "get_proj_start_time": lambda : datetime.now()
}

# fixtures:
@pytest.fixture
def test_path():
  return test_path_str

@pytest.fixture
def file_path():
  return file_path_str

@pytest.fixture
def start_time():
  return datetime.now()

# Apps gatherer
@pytest.fixture
def get_apps_gatherer():
  return AppsGatherer(OS)

# Files gatherer
@pytest.fixture
def get_files_gatherer():
  return FilesGatherer(OS)

# Explorer gatherer
@pytest.fixture
def get_items():
  return ["LocationName", "LocationURL"]

@pytest.fixture
def get_open_dirs_cmd():
  return '$a = New-Object -com "Shell.Application"; ' + \
    '$b = $a.windows() | select-object LocationURL, LocationName; ' + \
    '$b'

@pytest.fixture
def get_explorer():
  return Explorer(OS)

@pytest.fixture
def start_explorer():
  import os
  import subprocess
  from time import sleep
  path = "C:/Users"
  os.startfile(os.path.realpath(path))
  sleep(1)
  return path

@pytest.fixture
def get_explorer_row():
  return pd.DataFrame({
    "Name": [""],
    "MainWindowTitle": [""],
    "Path": ["C:/Users/"],
    })

@pytest.fixture
def get_gatherer():
  return Gatherer(test_path_str, projects_handler, OS)

@pytest.fixture
def get_projects_handler():
  return projects_handler