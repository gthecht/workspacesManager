import sys
import pytest
from datetime import datetime
from rarian.gatherer.appsGatherer import *
from rarian.gatherer.filesGatherer import FilesGatherer

# constants:
if "win" in sys.platform: OS = "windows"
elif "linux" in sys.platform: OS = "linux"
else: raise TypeError("unknown system platform", sys.platform)

test_path_str = os.path.abspath("./test")
file_path_str = os.path.join(test_path_str, "src", "gatherer", "conftest.py")

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

