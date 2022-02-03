import pytest
from rarian.unknownOSWarning import unknown_OS_Warning

class TestFilesGatherer:
  def test_get_open_files_with_no_paths(self, test_path, start_time, get_files_gatherer):
    """Should return an empty DataFrame for no paths"""
    files_gatherer = get_files_gatherer
    output = files_gatherer.get_open_files(None, start_time)
    assert output.empty
    output = files_gatherer.get_open_files([test_path], start_time)
    assert output.empty

  def test_get_open_files_wrong_os(self, start_time, get_files_gatherer):
    """Should return a warning if the OS isn't supported"""
    files_gatherer = get_files_gatherer
    files_gatherer.os = "linux"
    with pytest.raises(TypeError) as err:
      files_gatherer.get_open_files(["path"], start_time)
      assert err.value == unknown_OS_Warning().value

  def test_get_open_files_call_powershell(self, test_path, start_time, get_files_gatherer, mocker):
    """Should call get_files_from_powershell for paths"""
    files_gatherer = get_files_gatherer
    paths = [test_path]
    mock = mocker.patch("rarian.FilesGatherer.get_files_from_powershell")
    files_gatherer.get_open_files(paths, start_time)
    assert mock.call_count == 1
    mock.assert_called_once_with(paths, start_time)

  def test_get_files_from_powershell_call_psClient(self, test_path, start_time, get_files_gatherer, mocker):
    """Should call the PS client with the correct command"""
    files_gatherer = get_files_gatherer
    mock = mocker.patch("rarian.PSClient.get_PS_table_from_list")
    files_gatherer.get_files_from_powershell([test_path], start_time.isoformat())
    assert mock.call_count == 1
    mock.assert_called_once_with("Get-ChildItem '" + test_path + "\\*'" + \
      " -ErrorAction silentlycontinue " + \
      "| Where-Object { $_.LastAccessTime -gt \"" + \
      start_time.isoformat() + "\"}", files_gatherer.items)

  def test_get_files_from_powershell_multiple_paths(self, test_path, start_time, get_files_gatherer, mocker):
    """Should call the PSClient for each path"""
    files_gatherer = get_files_gatherer
    mock = mocker.patch("rarian.PSClient.get_PS_table_from_list")
    files_gatherer.get_files_from_powershell([test_path, test_path, test_path], start_time.isoformat())
    assert mock.call_count == 3
    mock.assert_called_with("Get-ChildItem '" + test_path + "\\*'" + \
      " -ErrorAction silentlycontinue " + \
      "| Where-Object { $_.LastAccessTime -gt \"" + \
      start_time.isoformat() + "\"}", files_gatherer.items)

  def test_get_files_from_powershell(self, test_path, file_path, start_time, get_files_gatherer):
    """Should return all files that have been opened since start_time"""
    files_gatherer = get_files_gatherer
    print(file_path)
    with open(file_path, 'r') as file:
      file.read()
    import datetime
    import time
    time.sleep(1)
    file_dir_path = '\\'.join(file_path.split('\\')[:-1])
    time = start_time - datetime.timedelta(seconds=30)
    open_files = files_gatherer.get_files_from_powershell([test_path, file_dir_path], time)
    assert "conftest.py" in list(open_files["Name"])
