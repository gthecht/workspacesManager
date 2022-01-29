import os
import shutil
import json
import pytest
import pandas as pd
from rarian.project.project import Project
from rarian.project.projectsHandler import ProjectsHandler

# constants:
file_items = [
  "Name",
  "LastWriteTime",
  "LastAccessTime",
  "Extension",
  "Directory",
  "FullName"
]
test_proj = os.path.abspath("./test/testProject")
tmp_proj = os.path.abspath("./test/tmp Project")
empty_proj = os.path.abspath("./test/emptyProject")
proj_name = "test project"
project_dict = {
  "paths": [empty_proj],
  "name": "TestProj",
  "proj_type": "test",
  "author": "pytest",
}

def init_project():
  shutil.copytree(test_proj, empty_proj)
  shutil.rmtree(os.path.join(empty_proj, ".rarian"))
  proj_from_dict = Project(**project_dict)
  shutil.rmtree(empty_proj)
  return proj_from_dict

proj_from_dict = init_project()

open_files = pd.DataFrame()

# fixtures:
@pytest.fixture
def test_proj_path():
  return tmp_proj

@pytest.fixture
def empty_proj_path():
  return empty_proj

@pytest.fixture
def project_details():
  return project_dict

@pytest.fixture
def project_name():
  return proj_name

@pytest.fixture
def create_uninitialized_project():
  shutil.copytree(test_proj, empty_proj)
  shutil.rmtree(os.path.join(empty_proj, ".rarian"))
  yield
  shutil.rmtree(empty_proj)

@pytest.fixture
def create_initialized_project():
  shutil.copytree(test_proj, tmp_proj)
  yield
  shutil.rmtree(tmp_proj)

@pytest.fixture
def load_project():
  shutil.copytree(test_proj, tmp_proj)
  yield Project.load(tmp_proj)
  shutil.rmtree(tmp_proj)

@pytest.fixture
def init_new_project():
  return proj_from_dict

@pytest.fixture
def add_new_file():
  def _add_new_file(dir_path):
    tmp_dir = os.path.join(dir_path, "temp")
    os.mkdir(tmp_dir)
    new_file_path = os.path.join(tmp_dir, "tmp.txt")
    with open (new_file_path, 'w') as file:
      file.write("temporary file")
    return new_file_path
  return _add_new_file


#%% ProjectsHandler
app_data_dict = {
  "projects": [tmp_proj],
  "default author": "pytest",
  "current": None,
}

app_data_path = os.path.abspath("./test/appData//data.json")

@pytest.fixture
def project_handler_file():
  return app_data_path

@pytest.fixture
def create_project_handler():
  shutil.copytree(test_proj, tmp_proj)
  proj_handler = ProjectsHandler(app_data_path)
  yield proj_handler
  shutil.rmtree(tmp_proj)
  with open(app_data_path, 'w') as data_file:
      json.dump(app_data_dict, data_file, sort_keys=True, indent=2)
