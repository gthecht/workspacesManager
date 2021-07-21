import os
import pandas as pd
from rarian import powershellClient as psClient

class TestPSClient:
  def test_run_powershell(self):
    """run_powershell returns powershell command output"""
    word = "hello"
    cmd = "echo " + word
    out = psClient.run_powershell(cmd)
    assert out == word + "\r\n"


  def get_child_item(self):
    files = os.listdir('.')
    files.sort()
    return files

  def test_get_PS_table_from_list(self):
    path = os.path.abspath(".")
    cmd = "Get-ChildItem " + path + " -Force"
    items = ["Name"]
    file_names = psClient.get_PS_table_from_list(cmd, items)
    file_names_check = [name[0] for name in file_names]
    file_names_check.sort()
    assert file_names_check == self.get_child_item()

  def test_get_PS_table_from_list_on_dirs(self):
    path = os.path.abspath(".")
    cmd = "Get-ChildItem " + path + "  -Force"
    items = ["Directory", "Name"]
    file_names = psClient.get_PS_table_from_list(cmd, items)
    file_names_check = [name[1] for name in file_names]
    file_names_check.sort()
    assert file_names_check == self.get_child_item()

  def test_reslash_on_list(self):
    data_list = [
      "some\\path\\somewhere",
      "some\\path\\somewhere",
    ]
    normal_data = [os.path.normpath(element) for element in data_list]
    new_data = psClient.reslash(data_list)
    assert new_data == normal_data

  def test_reslash_on_list_with_random_slash(self):
    data_list = [
      "some\'path\'somewhere",
      "some\'path\'somewhere",
    ]
    normal_data = [os.path.normpath(element) for element in data_list]
    new_data = psClient.reslash(data_list, "\'")
    assert new_data == normal_data

  def test_reslash_on_list_of_lists(self):
    data_list = [
      "some\'path\'somewhere",
      "some\'path\'somewhere",
    ]
    data_lol = [data_list, data_list, [data_list, data_list]]
    normal_data = [os.path.normpath(element) for element in data_list]
    normal_lol = [normal_data, normal_data, [normal_data, normal_data]]
    new_data = psClient.reslash(data_list)
    assert new_data == normal_data
    new_lol = psClient.reslash(data_lol)
    assert new_lol == normal_lol

  def test_parse_time(self):
    ps_time_str = "21-Jul-21 10:47:14 PM"
    time_value = "2021-07-21T22:47:14"
    df_dict = {
      "StartTime": [ps_time_str, ps_time_str],
      "EndTime": [ps_time_str, ps_time_str],
    }
    parsed_dict = {
      "StartTime": [time_value, time_value],
      "EndTime": [time_value, time_value],
    }
    df = pd.DataFrame(data=df_dict)
    parsed_df = pd.DataFrame(data=parsed_dict)
    new_df = psClient.parse_time(df, ["StartTime", "EndTime"])
    assert (new_df == parsed_df).all().all()
