import os
import sys
import shutil
import json
import pytest
import pandas as pd
import rarian.powershellClient as PSClient
from rarian.gatherer.appsGatherer import *

# constants:
if "win" in sys.platform: OS = "windows"
elif "linux" in sys.platform: OS = "linux"
else: raise TypeError("unknown system platform", sys.platform)

# fixtures:

# Apps gatherer
@pytest.fixture
def get_apps_gatherer():
  return AppsGatherer(OS)

