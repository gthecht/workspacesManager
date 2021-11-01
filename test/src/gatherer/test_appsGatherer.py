import pandas as pd
from rarian.gatherer.appsGatherer import *

class TestAppsGatherer:
  def test_find_words_in_string(self):
    """Should return the number of words appearing in a string, normalized"""
    wordStr = "A couple of WORDS"
    string = "here we see you use a term, but not too many words, just a word."
    assert find_words_in_string(wordStr, string) == 0.5 # A and word

  def test_find_words_in_string_empty(self):
    """Should return 0 if the number of words or the string are empty"""
    wordStr = "A couple of words"
    string = "here we see you use a term, but not too many words, just a word."
    assert find_words_in_string("", string) == 0
    assert find_words_in_string(wordStr, "") == 0

  def test_match_candidates(self):
    """Should return a list relative to the given lists"""
    list1 = [0, 0, 1]
    list2 = [1, 0, 1]
    expected = [0, 0, 2]
    out = match_candidates(list1, list2)
    assert len(out) == len(expected)
    assert all([a == b for a, b in zip(out, expected)])

  def test_match_candidates_empty(self):
    """Should return the non empty list if given an empty list"""
    list1 = [0, 0, 1]
    assert all([a == b for a, b in zip(match_candidates(list1, []), list1)])
    assert all([a == b for a, b in zip(match_candidates([], list1), list1)])
    assert match_candidates([], []) == []

  def test_match_candidates_partial(self):
    """Should return a list relative to the given lists"""
    list1 = [1, 0.333333, 0.5]
    list2 = [0, 1, 0.5]
    expected = [0, 1.333333, 1]
    out = match_candidates(list1, list2)
    assert len(out) == len(expected)
    assert all([a == b for a, b in zip(out, expected)])

  def test_get_apps(self, get_apps_gatherer):
    apps_gatherer = get_apps_gatherer
    apps_gatherer.get_apps()
    assert isinstance(apps_gatherer.apps, pd.DataFrame)
    assert all(apps_gatherer.apps.columns == ["path", "pathCandidates"])

  def test_get_open_apps(self):
    pass

  def test_clean_list(self):
    items=[]
    appsList = 0
    pass

  def test_get_app_candidates(self):
    item = 0
    pass

  def test_get_top_app(self):
    pass

  def test_add_open_apps_command_to_apps(self):
    open_apps = 0
    pass

  def test_get_open_folders(self):
    open_apps = ""
    pass
