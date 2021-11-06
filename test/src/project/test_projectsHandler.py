import json
import pytest
import pandas as pd
from rarian.project.project import Project

class TestProjectsHandler:
  def test_load_data(
    self,
    create_project_handler,
  ):
    """Should load the data from the data path"""
    proj_handler = create_project_handler
    data_dict = {
      "projects": ["projects"],
      "current": "current",
      "default author": "defaultAuthor",
    }
    with open(proj_handler.data_path, 'w') as data_file:
      json.dump(data_dict, data_file, sort_keys=True, indent=2)

    proj_handler.load_data()
    assert proj_handler.projects_paths == ["projects"]
    assert proj_handler.current == None
    assert proj_handler.default_author == "defaultAuthor"

  def test_init_projects_for_non_project(
    self,
    empty_proj_path,
    create_uninitialized_project,
    create_project_handler,
    project_name,
  ):
    """Should not add project if there is no .rarian folder there"""
    create_uninitialized_project
    proj_handler = create_project_handler
    # clear projects:
    proj_handler.projects = {}
    proj_handler.projects_paths = [empty_proj_path]
    proj_handler.init_projects()
    assert project_name not in proj_handler.projects.keys()

  def test_init_projects_for_project(
    self,
    test_proj_path,
    create_project_handler,
    project_name,
  ):
    """Should add project if there is a .rarian folder there"""
    proj_handler = create_project_handler
    # clear projects:
    proj_handler.projects = {}
    proj_handler.projects_paths = [test_proj_path]
    proj_handler.init_projects()
    assert project_name in proj_handler.projects.keys()

  def test_set_current_should_set_for_name(
    self,
    mocker,
    create_project_handler,
    project_name,
  ):
    """Should make current, inserted project"""
    proj_handler = create_project_handler
    spy_on = mocker.spy(Project, "turn_on")
    proj_handler.set_current(project_name)
    assert proj_handler.current == project_name
    assert spy_on.call_count == 1

  def test_set_current_should_set_for_path(
    self,
    mocker,
    create_project_handler,
    test_proj_path,
    project_name,
  ):
    """Should make current, when given project path"""
    proj_handler = create_project_handler
    spy_on = mocker.spy(Project, "turn_on")
    proj_handler.set_current(path=test_proj_path)
    assert proj_handler.current == project_name
    assert spy_on.call_count == 1

  def test_set_current_should_turn_off_prev(
    self,
    mocker,
    create_project_handler,
    project_name,
  ):
    """Should turn off the previous project if its a different project"""
    proj_handler = create_project_handler
    new_proj = "new project"
    proj_handler.projects[new_proj] = proj_handler.projects[project_name]
    spy_on = mocker.spy(Project, "turn_on")
    spy_off = mocker.spy(Project, "turn_off")

    proj_handler.set_current(project_name)
    assert proj_handler.current == project_name
    assert spy_on.call_count == 1
    assert spy_off.call_count == 0

    proj_handler.set_current(new_proj)
    assert proj_handler.current == new_proj
    assert spy_on.call_count == 2
    assert spy_off.call_count == 1

  def test_set_current_should_do_nothing(
    self,
    mocker,
    create_project_handler,
    test_proj_path,
  ):
    """Should do nothing if its the same project"""
    proj_handler = create_project_handler
    spy_on = mocker.spy(Project, "turn_on")
    spy_off = mocker.spy(Project, "turn_off")
    proj_handler.set_current(path=test_proj_path)
    assert spy_on.call_count == 1
    proj_handler.set_current(path=test_proj_path)
    assert spy_on.call_count == 1
    assert spy_off.call_count == 0

  def test_set_current_return_not_exist(
    self,
    create_project_handler,
  ):
    """If project name isn't in handler, should return error"""
    proj_handler = create_project_handler
    with pytest.raises(ValueError) as err:
      proj_handler.set_current("no such project")
      assert err.value == "Project doesn't exist"

  def test_get_current(self, create_project_handler):
    proj_handler = create_project_handler
    proj_handler.current = "current"
    assert proj_handler.get_current() == "current"

  def test_save_to_file(
    self,
    create_project_handler,
    mocker,
  ):
    """Should save the data to the data path"""
    proj_handler = create_project_handler
    proj_handler.projects_paths = ["projects"]
    proj_handler.current = None
    proj_handler.default_author = "defaultAuthor"

    spy = mocker.spy(Project, "save")
    proj_handler.save()
    with open(proj_handler.data_path, 'r') as data_file:
      data_str = data_file.read()
    data = json.loads(data_str)
    assert data["projects"] == ["projects"]
    assert data["current"] == None
    assert data["default author"] == "defaultAuthor"
    assert spy.call_count == 0

  def test_save_current(
    self,
    create_project_handler,
    project_name,
    mocker,
  ):
    """Should save the data to the data path"""
    proj_handler = create_project_handler
    proj_handler.current = project_name

    spy = mocker.spy(Project, "save")
    proj_handler.save()
    with open(proj_handler.data_path, 'r') as data_file:
      data_str = data_file.read()
    data = json.loads(data_str)
    assert spy.call_count == 1
    assert data["current"] == project_name

  def test_close_project_should_turn_off(
    self,
    mocker,
    create_project_handler,
    project_name,
  ):
    """Shouldn turn off the current project, and update current to None"""
    proj_handler = create_project_handler
    proj_handler.current = project_name
    spy_off = mocker.spy(Project, "turn_off")
    proj_handler.close_project()
    assert proj_handler.current == None
    assert spy_off.call_count == 1

  def test_close_project_should_do_nothing(
    self,
    mocker,
    create_project_handler,
  ):
    """Should do nothing if there is no current project"""
    proj_handler = create_project_handler
    spy_off = mocker.spy(Project, "turn_off")
    assert proj_handler.current == None
    proj_handler.close_project()
    assert proj_handler.current == None
    assert spy_off.call_count == 0

  def test_new_project_name_already_exists(
    self,
    create_project_handler,
    ):
    """Should raise an error that the name of the project is already taken"""
    proj_handler = create_project_handler
    proj_name = list(proj_handler.projects.keys())[0]
    with pytest.raises(ValueError) as err:
      proj_handler.new_project([], name=proj_name)
    assert str(err.value) == f"project of name {proj_name} already exists"

  def test_new_project(
    self,
    create_project_handler,
    mocker,
    test_proj_path,
  ):
    """Should create a new project"""
    proj_handler = create_project_handler
    proj_name = "new name"
    proj_path = test_proj_path + "/somewhere"
    proj_handler.new_project([proj_path], name=proj_name)
    assert proj_handler.projects[proj_name].name == proj_name
    assert proj_path in proj_handler.projects_paths

  def test_remove_sub_dir_for_current(
    self,
    create_project_handler,
    mocker,
  ):
    """Should call remove_sub_dir for current project"""
    proj_handler = create_project_handler
    proj_handler.current = list(proj_handler.projects.keys())[0]
    mock = mocker.patch("rarian.Project.remove_sub_dir")
    proj_handler.remove_sub_dir(".rarian")
    assert mock.call_count == 1
    assert mock.called_once_with(".rarian")

  def test_remove_sub_dir_for_no_current(
    self,
    create_project_handler,
    mocker,
  ):
    """Shouldn't call remove_sub_dir if there is no current project"""
    proj_handler = create_project_handler
    mock = mocker.patch("rarian.Project.remove_sub_dir")
    proj_handler.remove_sub_dir(".rarian")
    assert mock.call_count == 0

  def test_add_sub_dir(self):
    pytest.skip("Not implemented yet")

  def test_update_for_current(
    self,
    create_project_handler,
    mocker,
  ):
    """Should call update for current project"""
    proj_handler = create_project_handler
    proj_handler.current = list(proj_handler.projects.keys())[0]
    open_files = pd.DataFrame()
    open_apps = pd.DataFrame()
    mock = mocker.patch("rarian.Project.save")
    proj_handler.update(open_files, open_apps)
    assert mock.call_count == 1

  def test_update_for_no_current(
    self,
    create_project_handler,
    mocker,
  ):
    """Shouldn't call update if there is no current project"""
    proj_handler = create_project_handler
    open_files = pd.DataFrame()
    open_apps = pd.DataFrame()
    mock = mocker.patch("rarian.Project.save")
    proj_handler.update(open_files, open_apps)
    assert mock.call_count == 0

  def test_get_open_for_current(
    self,
    create_project_handler,
    mocker,
  ):
    """Should call get_open for current project"""
    proj_handler = create_project_handler
    proj_handler.current = list(proj_handler.projects.keys())[0]
    mock = mocker.patch("rarian.Project.get_open")
    proj_handler.get_open()
    assert mock.call_count == 1

  def test_get_open_for_no_current(
    self,
    create_project_handler,
    mocker,
  ):
    """Shouldn't call get_open if there is no current project"""
    proj_handler = create_project_handler
    mock = mocker.patch("rarian.Project.get_open")
    proj_handler.get_open()
    assert mock.call_count == 0

  def test_get_proj_dirs_for_current(
    self,
    create_project_handler,
  ):
    """Should return project paths for current project"""
    proj_handler = create_project_handler
    proj_handler.current = list(proj_handler.projects.keys())[0]
    paths = proj_handler.get_proj_dirs()
    assert paths == proj_handler.projects[proj_handler.current].paths

  def test_get_proj_dirs_for_no_current(
    self,
    create_project_handler,
  ):
    """Shouldn't return project paths if there is no current project"""
    proj_handler = create_project_handler
    paths = proj_handler.get_proj_dirs()
    assert paths == None

  def test_get_proj_start_time_for_current(
    self,
    create_project_handler,
  ):
    """Should return project paths for current project"""
    proj_handler = create_project_handler
    proj_handler.current = list(proj_handler.projects.keys())[0]
    paths = proj_handler.get_proj_start_time()
    assert paths == proj_handler.projects[proj_handler.current].start_time

  def test_get_proj_start_time_for_no_current(
    self,
    create_project_handler,
  ):
    """Shouldn't return project paths if there is no current project"""
    proj_handler = create_project_handler
    paths = proj_handler.get_proj_start_time()
    assert paths == None

  def test_get_project_data_projects(
    self,
    create_project_handler,
  ):
    """Should return all projects in handler"""
    proj_handler = create_project_handler
    projects = proj_handler.get_project_data("projects")
    assert projects == list(proj_handler.projects.keys())

  @pytest.mark.parametrize("member", ["files", "apps"]) # add "notes", "urls"
  def test_get_project_data_members(
    self,
    create_project_handler,
    member,
  ):
    """Should return all of type member in current project"""
    proj_handler = create_project_handler
    proj_handler.current = list(proj_handler.projects.keys())[0]
    data = proj_handler.get_project_data(member)
    expected_data = getattr(proj_handler.projects[proj_handler.current], member)
    if isinstance(data, pd.DataFrame): assert data.equals(expected_data)
    else: assert data == expected_data

  def test_get_project_data_not_a_member(
    self,
    create_project_handler,
  ):
    """Should raise error that there is no such data member"""
    proj_handler = create_project_handler
    proj_handler.current = list(proj_handler.projects.keys())[0]
    with pytest.raises(ValueError) as err:
      proj_handler.get_project_data("no such data member")
    assert str(err.value) == "undefined data member"

  def test_get_project_no_current(
    self,
    create_project_handler,
  ):
    """Should return none if there is no current project"""
    proj_handler = create_project_handler
    data = proj_handler.get_project_data("no such data member")
    assert data == None

  def test_stop(self, create_project_handler):
    proj_handler = create_project_handler
    assert proj_handler.running == True
    proj_handler.stop()
    assert proj_handler.running == False
