from datetime import datetime
import json
from time import sleep
import os
import pytest
import pandas as pd
from rarian.project.project import Project

class TestProject:
  def test_load_with_proper_path(self, test_proj_path, create_initialized_project):
    create_initialized_project
    Project.load(test_proj_path)

  def test_load_with_faulty_path(self):
    false_project_path = os.path.abspath("./test/testProject" + "nowhere")
    with pytest.raises(FileNotFoundError) as err:
      Project.load(false_project_path)
      assert err.value == "Path is not a rarian project"

  def test_load_with_path_with_no_project(self, empty_proj_path, create_uninitialized_project):
    create_uninitialized_project
    with pytest.raises(FileNotFoundError) as err:
      Project.load(empty_proj_path)
      assert err.value == "Path is not a rarian project"

  def test_load_with_rarian_without_data(self, empty_proj_path, create_uninitialized_project):
    create_uninitialized_project
    os.mkdir(os.path.join(empty_proj_path, ".rarian"))
    no_project_path = os.path.abspath("./test/src")
    with pytest.raises(FileNotFoundError) as err:
      Project.load(no_project_path)
      assert err.value == f"No such file or directory: '{no_project_path}\\.rarian\\data.json'"

  def test_init(self, empty_proj_path, create_uninitialized_project):
    """should create a new project"""
    create_uninitialized_project
    proj = Project(
      [empty_proj_path],
      name="TestProj",
      proj_type="test",
      author="pytest",
    )
    assert proj.paths == [empty_proj_path]
    assert proj.name == "TestProj"
    assert proj.type == "test"
    assert proj.author == "pytest"

  def test_init_with_no_name(self, empty_proj_path, create_uninitialized_project):
    """should use the directory as the name"""
    create_uninitialized_project
    proj = Project(
      [empty_proj_path],
      proj_type="test",
      author="pytest",
    )
    assert proj.paths == [empty_proj_path]
    assert proj.name == "emptyProject"
    assert proj.type == "test"
    assert proj.author == "pytest"

  def test_path(self, empty_proj_path, create_uninitialized_project):
    create_uninitialized_project
    proj = Project(
      [empty_proj_path, empty_proj_path + "2"],
      proj_type="test",
      author="pytest",
    )
    assert proj.path() == empty_proj_path

  def test_get_files(self, create_uninitialized_project, init_new_project):
    create_uninitialized_project
    proj = init_new_project
    columns = proj.file_items
    columns.remove("FullName")
    columns.extend(["Relevance", "Open", "Type"])
    assert list(proj.files.columns) == columns
    assert proj.files["Name"][0] == "testFile.py"
    assert len(proj.files.index) == 1

  def test_file_add_columns(self, init_new_project):
    proj = init_new_project
    files = {
      "Name": ["file1.type1", "file2.type2", "directory"],
      "Extension": [".type1", ".type2", ""],
      "FullName": ["C:\\dir1\\file1", "C:\\dir1\\file2", "C:\\dir1\\directory"],
      "Directory": ["C:\\dir1", "C:\\dir1", "C:\\dir1"],
    }
    files_df = pd.DataFrame(files)
    new_df = proj.file_add_columns(files_df)
    assert list(new_df.columns) == ["Name", "Extension", "Directory", "Relevance", "Open", "Type"]
    assert list(new_df["Relevance"]) == [1, 1, 1]
    assert list(new_df["Open"]) == [False, False, False]
    assert list(new_df["Type"]) == ["type1", "type2", ""]
    assert list(new_df.index) == files["FullName"]

  def test_get_open(self, load_project):
    proj = load_project
    proj.open_files = "just some open files"
    proj.open_apps = "just some open apps"
    open_data = {
      "files": "just some open files",
      "apps": "just some open apps"
    }
    assert proj.get_open() == open_data

  def test_save(self, test_proj_path, load_project):
    proj = load_project
    old_name = proj.name
    proj.name = "new name"
    proj.save()
    with open (os.path.join(test_proj_path, ".rarian\\data.json"), 'r') as data_file:
      data_str = data_file.read()
    proj_data = json.loads(data_str)
    assert proj_data["name"] == proj.name
    proj.name = old_name
    proj.save()

  def test_remove_sub_dir(self, create_uninitialized_project, project_details, empty_proj_path, add_new_file):
    create_uninitialized_project
    new_file_path = add_new_file(empty_proj_path)
    proj = Project(**project_details)

    # make sure the tmp file is in the project
    assert new_file_path in list(proj.files.index)
    sub_dir = "temp"
    proj.remove_sub_dir(sub_dir)

    assert os.path.abspath(sub_dir) in proj.removed_dirs
    # make sure the tmp file was removed from the project
    assert os.path.join(empty_proj_path, "temp", "tmp.txt") not in proj.files

  def test_files_update_open_on_empty(self, load_project):
    proj = load_project
    proj.open_files = pd.DataFrame()
    prev_files = proj.files.copy()
    proj.files_update_open()
    assert proj.files.equals(prev_files)

  def test_files_update_open_on_file(self, load_project, test_proj_path):
    proj = load_project
    file_name = os.path.join(test_proj_path, "testFile.py")
    now = datetime.now()
    proj.open_files = pd.DataFrame({
      "FullName": [file_name],
      "Name": ["testFile.py"],
      "LastWriteTime": [now],
      "LastAccessTime": [now],
      "Extension": [".py"],
      "Directory": [test_proj_path],
      "Type": ["py"],
    })
    proj.open_files.set_index("FullName", inplace=True)
    prev_file = proj.files.loc[file_name]
    assert proj.files.at[file_name, "Open"] == False
    proj.files_update_open()
    assert proj.files.at[file_name, "Open"] == True
    assert proj.files.at[file_name, "Relevance"] == prev_file["Relevance"] * (proj.add_rate)
    assert proj.files.at[file_name, "LastAccessTime"] == now
    assert proj.files.at[file_name, "LastWriteTime"] == now

  def test_files_update_open_on_new_file(self, load_project, test_proj_path, add_new_file):
    proj = load_project
    file_name = add_new_file(test_proj_path)
    now = datetime.now()
    proj.open_files = pd.DataFrame({
      "FullName": [file_name],
      "Name": ["tmp.txt"],
      "LastWriteTime": [now],
      "LastAccessTime": [now],
      "Extension": [".txt"],
      "Directory": ["\\".join(file_name.split("\\")[:-1])],
      "Type": ["txt"],
    })
    proj.open_files.set_index("FullName", inplace=True)
    assert file_name not in proj.files.index
    proj.files_update_open()
    assert proj.files.at[file_name, "Open"] == True
    assert proj.files.at[file_name, "Relevance"] == proj.add_rate
    assert proj.files.at[file_name, "LastAccessTime"] == now
    assert proj.files.at[file_name, "LastWriteTime"] == now

  def test_files_update_open_not_on_removed_file(self, load_project, test_proj_path, add_new_file):
    proj = load_project
    proj.removed_dirs = [os.path.join(test_proj_path, "temp")]
    file_name = add_new_file(test_proj_path)
    now = datetime.now()
    proj.open_files = pd.DataFrame({
      "FullName": [file_name],
      "Name": ["tmp.txt"],
      "LastWriteTime": [now],
      "LastAccessTime": [now],
      "Extension": [".txt"],
      "Directory": ["\\".join(file_name.split("\\")[:-1])],
      "Type": ["txt"],
    })
    proj.open_files.set_index("FullName", inplace=True)
    assert file_name not in proj.files.index
    proj.files_update_open()
    assert file_name not in proj.files.index

  def test_files_update_closed_when_file_not_open(self, load_project):
    proj = load_project
    file_name = proj.files.index[-1]
    proj.files.at[file_name, "Open"] = True
    assert proj.files.at[file_name, "Open"] == True
    proj.open_files = pd.DataFrame()
    proj.files_update_closed()
    assert proj.files.at[file_name, "Open"] == False

  def test_files_update_closed_when_file_still_open(self, load_project, test_proj_path):
    proj = load_project
    file_name = os.path.join(test_proj_path, "testFile.py")
    now = datetime.now()
    proj.open_files = pd.DataFrame({
      "FullName": [file_name],
      "Name": ["testFile.py"],
      "LastWriteTime": [now],
      "LastAccessTime": [now],
      "Extension": [".py"],
      "Directory": [test_proj_path],
      "Type": ["py"],
    })
    proj.open_files.set_index("FullName", inplace=True)
    assert proj.files.at[file_name, "Open"] == False
    proj.files.at[file_name, "Open"] = True
    assert proj.files.at[file_name, "Open"] == True
    proj.files_update_closed()
    assert proj.files.at[file_name, "Open"] == True

  def test_apps_update(self):
    pytest.skip("Currently undefined method")

  def test_forget(self, load_project):
    proj = load_project
    relevance_values = proj.files["Relevance"].copy()
    proj.forget()
    assert proj.files["Relevance"].equals(relevance_values * proj.forget_rate)

  def test_turn_off(self, load_project):
    proj = load_project
    now = datetime.now()
    sleep(0.1)
    proj.turn_off()
    sleep(0.1)
    # Check that the end time did indeed occur now:
    assert proj.end_time < datetime.now()
    assert proj.end_time > now

  def test_turn_on(self, load_project):
    proj = load_project
    prev_start_time = proj.start_time
    now = datetime.now()
    assert now > prev_start_time
    sleep(0.1)
    proj.turn_on()
    sleep(0.1)
    # Check that the start time did indeed occur now:
    assert proj.start_time < datetime.now()
    assert proj.start_time > now
