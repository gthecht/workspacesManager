from datetime import time
import queue
import pytest

from rarian.gatherer.appsGatherer import AppsGatherer
from rarian.gatherer.filesGatherer import FilesGatherer

@pytest.mark.skip(reason="run has infinite loop")
class TestGatherer:
  def test_constructor(self, get_gatherer, test_path, get_projects_handler):
    """should have all the correct arguments"""
    gatherer = get_gatherer
    print(f'gatherer: {type(gatherer)}')
    assert gatherer.log_dir == test_path
    assert gatherer.os == "windows"
    assert type(gatherer.apps_handler) == AppsGatherer
    assert type(gatherer.files_handler) == FilesGatherer
    assert gatherer.projects_handler == get_projects_handler
    assert type(gatherer.reply_q) == queue.Queue

  def test_run_running_is_true(self, get_gatherer):
    """should make self.running = True"""
    gatherer = get_gatherer
    gatherer.run()

  def test_run_gather_files(self, get_gatherer, mocker):
    """should run gather_files function"""
    gatherer = get_gatherer
    mock_gather_files = mocker.patch("rarian.Gatherer.gather_files")
    mock_gather_apps = mocker.patch("rarian.Gatherer.gather_apps")
    gatherer.run()
    assert mock_gather_files.call_count == 1
    assert mock_gather_apps.call_count == 1

  def test_run_add_job(self, get_gatherer, mocker):
    """should add a job"""
    gatherer = get_gatherer
    mock = mocker.patch("rarian.Gatherer.add_job")
    gatherer.open_files = "open files"
    gatherer.open_apps = "open apps"
    gatherer.run()
    time.sleep(1)
    gatherer.stop()
    assert mock.call_count == 1
    assert mock.call_countassert_called_with({
        "method": "update",
        "args": {
          "open_files": gatherer.open_files,
          "open_apps": gatherer.open_apps
        },
      })

  # def test_gather_files(self, get_gatherer):
  #   """should gather_files"""
  #   gatherer = get_gatherer
  #   assert True

  # def test_gather_apps(self, get_gatherer):
  #   """should gather_apps"""
  #   gatherer = get_gatherer
  #   assert True

  # def test_stop(self, get_gatherer):
  #   """should stop"""
  #   gatherer = get_gatherer
  #   assert True
