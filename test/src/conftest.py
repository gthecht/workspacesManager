import os
import json
import pytest
from rarian.manager import Manager

data_dir = os.path.abspath("./test/testDataDir")

manager = Manager(data_dir)
projects = [
  {
    "name": "first_proj",
    "path": "path/to/project"
  },
  {
    "name": "second_proj",
    "path": "path/to/another/project"
  }
]

@pytest.fixture
def get_data_dir():
  return data_dir

@pytest.fixture
def get_manager():
  return manager

@pytest.fixture
def new_data_json():
  data_file_path = os.path.join(data_dir, 'data.json')
  with open(data_file_path, 'r') as data_json:
    data_str = data_json.read()
  old_data = json.loads(data_str)
  new_data = old_data.copy()
  new_data['projects'] = projects
  with open(data_file_path, 'w') as data_json:
    data_json.write(json.dumps(new_data))
  yield
  with open(data_file_path, 'w') as data_json:
    data_json.write(json.dumps(old_data, indent=2))
