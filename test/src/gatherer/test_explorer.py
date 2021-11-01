class TestExplorer:
  def test_get_open_directories_call_psClient(
    self,
    get_explorer,
    get_open_dirs_cmd,
    get_items,
    mocker
  ):
    """should PS client with correct command and items"""
    explorer = get_explorer
    mock = mocker.patch("rarian.PSClient.get_PS_table_from_list")
    explorer.get_open_directories()
    assert mock.call_count == 1
    mock.assert_called_with(get_open_dirs_cmd, get_items)

  def test_get_open_explorers(self, get_explorer, start_explorer, get_explorer_row):
    """should return all open explorers"""
    explorer = get_explorer
    path = start_explorer
    explorer_row = get_explorer_row
    output = explorer.get_open_explorers(explorer_row)
    assert output.loc[0].Name == 'Users'
    assert output.loc[0].MainWindowTitle == 'Users'
    assert output.loc[0].Path == path
