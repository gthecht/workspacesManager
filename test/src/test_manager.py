import os

from rarian.project.projectsHandler import ProjectsHandler
from rarian.gatherer.gatherer import Gatherer
from rarian.executor.executor import Executor
from rarian.ui.cliClient import CLIent

class TestManager:
  def test_constructor(self, get_data_dir, get_manager):
    manager = get_manager
    assert manager.os == "windows"
    assert manager.data_dir == get_data_dir
    assert manager.log_dir == os.path.join(get_data_dir, "logs")
    assert type(manager.projects_handler) == ProjectsHandler
    assert type(manager.gatherer) == Gatherer
    assert type(manager.executor) == Executor
    assert type(manager.client) == CLIent

  def test_get_os(self, get_manager):
    manager = get_manager
    manager.os = None
    manager.get_os()
    assert manager.os == "windows"

  def test_load_data(self, get_data_dir, get_manager, new_data_json):
    manager = get_manager
    manager.data_file = None
    manager.projects = []
    new_data_json
    manager.load_data()
    assert manager.data_file == os.path.join(get_data_dir, "data.json")
    assert manager.projects[0] == {"name": "first_proj", "path": "path/to/project"}
    assert len(manager.projects) == 2

  def test_run(self, get_manager, mocker):
    manager = get_manager
    projects_handler_start = mocker.patch("rarian.ProjectsHandler.start")
    projects_handler_join = mocker.patch("rarian.ProjectsHandler.join")
    gatherer_start = mocker.patch("rarian.Gatherer.start")
    gatherer_join = mocker.patch("rarian.Gatherer.join")
    client_start = mocker.patch("rarian.CLIent.start")
    client_join = mocker.patch("rarian.CLIent.join")
    manager.run()
    assert projects_handler_start.call_count == 1
    assert projects_handler_join.call_count == 1
    assert gatherer_start.call_count == 1
    assert gatherer_join.call_count == 1
    assert client_start.call_count == 1
    assert client_join.call_count == 1

  def test_save(self, get_manager, mocker):
    manager = get_manager
    save_mock = mocker.patch("rarian.Executor.save")
    manager.save()
    assert save_mock.call_count == 1

  def test_quit(self, get_manager, mocker):
    manager = get_manager
    gatherer_stop = mocker.patch("rarian.Gatherer.stop")
    client_stop = mocker.patch("rarian.CLIent.stop")
    executor_stop = mocker.patch("rarian.Executor.stop")
    manager.quit()
    assert gatherer_stop.call_count == 1
    assert client_stop.call_count == 1
    assert executor_stop.call_count == 1
