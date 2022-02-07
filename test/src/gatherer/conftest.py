import os
import sys
import pytest
import pandas as pd
from datetime import datetime, timedelta
from rarian.gatherer.appsGatherer import AppsGatherer
from rarian.gatherer.filesGatherer import FilesGatherer
from rarian.gatherer.gatherer import Gatherer
from rarian.gatherer.explorer import Explorer

# constants:
if "win" in sys.platform:
    OS = "windows"
elif "linux" in sys.platform:
    OS = "linux"
else:
    raise TypeError("unknown system platform", sys.platform)

test_path_str = os.path.abspath("./test")
file_path_str = os.path.join(test_path_str, "src", "gatherer", "conftest.py")
projects_handler = {
    "q": {
        "list": [],
        "put": lambda el: projects_handler["q"]["list"].append(el)
    },
    "get_proj_dirs": lambda: [test_path_str],
    "get_proj_start_time": lambda: datetime.now()
}

gatherer = Gatherer(test_path_str, projects_handler, OS)

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

# %% Apps gatherer


apps_gatherer = AppsGatherer(OS)
apps_items_list = ["Id", "Name", "Description",
                   "MainWindowTitle", "StartTime", "Path"]


@pytest.fixture
def get_apps_gatherer():
    return apps_gatherer


@pytest.fixture
def apps_items():
    return apps_items_list


@pytest.fixture
def get_old_apps():
    one_minute = timedelta(minutes=1)
    old_apps = pd.DataFrame({
        "Id": ["0123", "4567"],
        "App": ["app0", "app1"],
        "Name": ["app0", "app1"],
        "Description": ["app0 - open window", "app1 - closed app"],
        "MainWindowTitle": ["app0 - window title", "app1 - window title"],
        "StartTime": [
            (datetime.now() - 2 * one_minute).isoformat()[0:-7],
            (datetime.now() - one_minute).isoformat()[0:-7],
        ],
        "EndTime": [
            (datetime.now() - one_minute).isoformat()[0:-7],
            datetime.now().isoformat()[0:-7],
        ],
    })
    return old_apps

# %% Files gatherer


@pytest.fixture
def get_files_gatherer():
    return FilesGatherer(OS)

# %% Explorer gatherer


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
    return gatherer


@pytest.fixture
def get_projects_handler():
    return projects_handler
