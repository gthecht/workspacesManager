import pandas as pd
import pytest
from datetime import datetime
from rarian.gatherer.appsGatherer import find_words_in_string, match_candidates


class TestAppsGatherer:
    def test_find_words_in_string(self):
        """Should return the number of words appearing in a string,
        normalized"""
        wordStr = "A couple of WORDS"
        string = "here we see you use a term, but not too many words"
        assert find_words_in_string(wordStr, string) == 0.5  # A and word

    def test_find_words_in_string_empty(self):
        """Should return 0 if the number of words or the string are empty"""
        wordStr = "A couple of words"
        string = "here we see you use a term, but not too many words"
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
        assert all([a == b for a, b in zip(
            match_candidates(list1, []), list1)])
        assert all([a == b for a, b in zip(
            match_candidates([], list1), list1)])
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

    def test_get_open_apps_not_windows(self, get_apps_gatherer):
        """Should return unknown os warning if os is unknown"""
        apps_gatherer = get_apps_gatherer
        old_os = apps_gatherer.os
        apps_gatherer.os = "Unknown os"
        with pytest.raises(TypeError):
            apps_gatherer.get_open_apps()
        apps_gatherer.os = old_os

    def test_get_open_apps_call_psClient(self, get_apps_gatherer, mocker):
        """Should call ps client to get open apps"""
        apps_gatherer = get_apps_gatherer
        items = ["Id", "Name", "Description",
                 "MainWindowTitle", "StartTime", "Path"]
        cmd = "Get-Process | Where-Object { $_.MainWindowHandle -ne 0}"
        ps_mock = mocker.patch('rarian.PSClient.get_PS_table_from_list')
        apps_gatherer.get_open_apps()
        assert ps_mock.call_args_list[0].args == (cmd, items)

    def test_get_open_apps_catches_error(self, get_apps_gatherer, mocker):
        """Should catch exception if PSClient doesn't get open apps
        successfully"""
        apps_gatherer = get_apps_gatherer
        mocker.patch('rarian.PSClient.get_PS_table_from_list',
                     side_effect=Exception('mocked error'))
        with pytest.raises(Exception) as err:
            apps_gatherer.get_open_apps()
            assert str(err) == 'mocked error'

    def test_get_open_apps_cleans_list(
        self,
        get_apps_gatherer,
        apps_items,
        mocker,
    ):
        """Should call self.clean_list on apps from PSClient"""
        apps_gatherer = get_apps_gatherer
        clean_list_mock = mocker.patch('rarian.AppsGatherer.clean_list')
        apps_gatherer.get_open_apps()
        assert clean_list_mock.call_args[0][0] == apps_items

    def test_get_open_apps_get_open_folders(self, get_apps_gatherer, mocker):
        """Should call self.get_open_folders"""
        apps_gatherer = get_apps_gatherer
        get_open_folders_mock = mocker.patch('rarian.AppsGatherer.clean_list')
        apps_gatherer.get_open_apps()
        assert get_open_folders_mock.called_once

    def test_get_open_apps_has_right_columns(
        self,
        get_apps_gatherer,
        apps_items,
    ):
        """Should return correct dataframe"""
        apps_gatherer = get_apps_gatherer
        open_apps = apps_gatherer.get_open_apps()
        columns = apps_items
        columns.extend(["EndTime", "App"])
        assert [col in columns for col in open_apps.columns]
        assert [col in open_apps.columns for col in columns]

    @pytest.mark.skip(reason='Probably will remove the function')
    def test_clean_list(self):
        pass

    def test_get_app_candidates(self, get_apps_gatherer):
        """Should get list of candidates for item from apps"""
        apps_gatherer = get_apps_gatherer
        item = "3D"
        candidates = apps_gatherer.get_app_candidates(item)
        real_candidates = [
            find_words_in_string(item, name)
            + find_words_in_string(name, item)
            for name in apps_gatherer.apps.index
        ]
        assert candidates == real_candidates

    @pytest.mark.skip(reason='as yet unimplemented')
    def test_get_top_app(self):
        pass

    def test_add_open_apps_command_to_apps(self, get_apps_gatherer):
        """Should add the path in open_apps to the relevant app if no path"""
        apps_gatherer = get_apps_gatherer
        prev_apps = apps_gatherer.apps.copy()
        apps_gatherer.apps = pd.DataFrame({"App": ["app"], "path": [None]})
        path = "path/to/app"
        open_apps = pd.DataFrame({"App": [0], "Path": [path]})
        apps_gatherer.add_open_apps_command_to_apps(open_apps)
        assert apps_gatherer.apps.path.loc[0] == path
        apps_gatherer.apps = prev_apps.copy()

    def test_get_open_folders(self, get_apps_gatherer, mocker):
        """Should call get open explorers on open explorer apps"""
        apps_gatherer = get_apps_gatherer
        open_apps = pd.DataFrame(
            {"App": ["folder"], "Name": ["explorer"], "Path": [None]})
        explorer_mock = mocker.patch('rarian.Explorer.get_open_explorers')
        returned_apps = open_apps
        returned_apps["Path"].loc[0] = "explorer/path"
        explorer_mock.return_value = returned_apps
        out_apps = apps_gatherer.get_open_folders(open_apps)
        assert explorer_mock.callled_with(open_apps)
        assert out_apps.equals(returned_apps)

    def test_compare_apps_keeps_newer_duplicate(
        self,
        get_apps_gatherer,
        get_old_apps,
    ):
        """Should keep the newer version of duplicate rows"""
        apps_gatherer = get_apps_gatherer
        old_apps = get_old_apps
        new_apps = old_apps.copy()
        new_apps["EndTime"].loc[0] = ""
        out_apps = apps_gatherer.compare_apps(new_apps, old_apps)
        # compare apps updates the start time so we'll remove it
        del out_apps["StartTime"]
        del new_apps["StartTime"]
        assert out_apps.equals(new_apps)

    def test_compare_apps_adds_end_time_to_closed_apps(
        self,
        get_apps_gatherer,
        get_old_apps,
    ):
        """Should Add EndTime to rows that aren't in new"""
        apps_gatherer = get_apps_gatherer
        old_apps = get_old_apps
        new_apps = old_apps[old_apps.index == 0].copy()
        new_apps["EndTime"].loc[0] = ""
        now = datetime.fromisoformat(datetime.now().isoformat()[0:-7])
        out_apps = apps_gatherer.compare_apps(new_apps, old_apps)
        assert datetime.fromisoformat(out_apps["EndTime"].loc[1]) >= now

    def test_compare_apps_changes_start_time_of_new_apps_to_now(
        self,
        get_apps_gatherer,
        get_old_apps,
    ):
        """Should change the start time of apps in new to now but not the old"""
        apps_gatherer = get_apps_gatherer
        old_apps = get_old_apps
        new_apps = old_apps[old_apps.index == 0].copy()
        old_apps["EndTime"].loc[1] = ""
        now = datetime.fromisoformat(datetime.now().isoformat()[0:-7])
        out_apps = apps_gatherer.compare_apps(old_apps, new_apps)
        print(old_apps)
        print(new_apps)
        print(out_apps)
        assert datetime.fromisoformat(out_apps["StartTime"].loc[0]) < now
        assert datetime.fromisoformat(out_apps["StartTime"].loc[1]) >= now

