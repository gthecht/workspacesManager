import os
import shutil
import pytest
import pandas as pd
from rarian.project.project import Project
import rarian.powershellClient as PSClient

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
tmp_proj = os.path.abspath("./test/tmpProject")
empty_proj = os.path.abspath("./test/emptyProject")
project_dict = {
  "paths": [empty_proj],
  "name": "TestProj",
  "proj_type": "test",
  "author": "pytest",
}

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
def init_new_project(proj_dict=project_dict):
  return Project(**proj_dict)

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
