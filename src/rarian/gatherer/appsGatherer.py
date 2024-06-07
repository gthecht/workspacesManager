from rarian.gatherer.explorer import Explorer
from rarian.unknownOSWarning import unknown_OS_Warning
from rarian import powershellClient as PSClient
import os
import sys
from datetime import datetime
import numpy as np
import pandas as pd
import dateutil.parser

parent = os.path.abspath('./src')
sys.path.insert(1, parent)


def find_words_in_string(wordStr, string):
    """Find the number of words in wordStr that appear in string,
    normalized by the number of words"""
    if not wordStr or not string:
        return 0
    words = wordStr.split()
    appear = list(filter(lambda word: word.lower() in string.lower(), words))
    return len(appear) / len(words)


def match_candidates(list1, list2):
    if not len(list1):
        return list2
    elif not len(list2):
        return list1
    else:
        return np.multiply(
            np.add(list1, list2),
            np.multiply(
                [weight > 0 for weight in list1],
                [weight > 0 for weight in list2]
            )
        )


class AppsGatherer:
    def __init__(self, os="windows"):
        self.os = os
        if self.os == "windows":
            self.STARTPATH = "C:\\ProgramData\\Microsoft\\Windows" \
                + "\\Start Menu\\Programs\\"
        self.explorer = Explorer()
        self.get_apps()

    def get_apps(self):
        start_apps = PSClient.get_PS_table_from_list("Get-StartApps", ["Name"])
        start_apps = [app[0] for app in start_apps]
        apps_table = PSClient.get_PS_table_from_list(
            "Get-ChildItem \"" + self.STARTPATH +
            "*\" -Recurse | where { ! $_.PSIsContainer }",
            ["Name", "FullName"]
        )

        apps_list = []
        candidates = []
        path = []
        for app in start_apps:
            if app not in apps_list:
                apps_list.append(app)
                candid_list = list(
                    filter(lambda row: app in row[0], apps_table))
                candidates.append([row[1] for row in candid_list])
                if candidates[-1] == []:
                    path.append(None)
                else:
                    path.append(candidates[-1][0])
        apps_dict = {
            "path": path,
            "pathCandidates": candidates
        }
        self.apps = pd.DataFrame(apps_dict, index=apps_list, columns=[
                                 "path", "pathCandidates"])

    def get_open_apps(self):
        if self.os == "windows":
            items = ["Id", "Name", "Description",
                     "MainWindowTitle", "StartTime", "Path"]
            try:
                open_apps_list = PSClient.get_PS_table_from_list(
                    "Get-Process | Where-Object { $_.MainWindowHandle -ne 0}",
                    items
                )
            except Exception as err:
                print(
                    "Powershell client failed to get open apps with error: " +
                    str(err))
                raise err
            open_apps_list = self.clean_list(items, open_apps_list)
            open_apps = pd.DataFrame(open_apps_list, columns=items)
            app_names = [""] * open_apps.shape[0]
            for ind in range(open_apps.shape[0]):
                desc_candidates = self.get_app_candidates(
                    open_apps.loc[ind].Description)
                title_candidates = self.get_app_candidates(
                    open_apps.loc[ind].MainWindowTitle)
                path_candidates = self.get_app_candidates(
                    open_apps.loc[ind].Path)
                matches = match_candidates(match_candidates(
                    desc_candidates, title_candidates), path_candidates)
                if (not all(matches == np.zeros(len(matches)))):
                    appInd = np.argmax(matches)
                    app_names[ind] = (self.apps.index[appInd])
            open_apps.insert(1, "App", app_names)
            self.add_open_apps_command_to_apps(open_apps)
            open_apps = self.get_open_folders(open_apps)
            open_apps.reset_index(drop=True, inplace=True)
            try:
                start_time = open_apps.assign(
                    start_time=lambda dataframe: dataframe["StartTime"].map(
                        lambda timeStr: dateutil.parser.parse(timeStr).
                        isoformat()
                    )
                )
            except Exception as err:
                print(
                    "Apps handler failed to parse start time field, " +
                    "with error: " + str(err)
                )
                raise err
            open_apps.update(start_time)
            open_apps.insert(len(items), "EndTime", [""] * open_apps.shape[0])
            open_apps = PSClient.parse_time(open_apps, ["StartTime"])
            return open_apps
        else:
            return unknown_OS_Warning()

    # cleans the list because sometimes powershell returns moved rows in the
    # table
    def clean_list(self, items, appsList):
        clean_list = []
        start_time_ind = items.index("StartTime")
        for row in appsList:
            if not row[start_time_ind][0].isdigit():
                first_digit = [c.isdigit()
                               for c in row[start_time_ind]].index(True)
                for ind in np.arange(start_time_ind, len(items)):
                    row[ind - 1] += row[ind][:first_digit]
                    row[ind - 1] = row[ind - 1].strip()
                    row[ind] = row[ind][first_digit:]
            clean_list.append(row)
        return clean_list

    def get_app_candidates(self, item):
        if item == "":
            return []
        return list(map(lambda name: find_words_in_string(item, name)
                        + find_words_in_string(name, item), self.apps.index))

    def get_top_app(self):
        if self.os == "windows":
            print("need to get the top window")
            # use the cpp program using windows SDK
        else:
            return unknown_OS_Warning()

    def add_open_apps_command_to_apps(self, open_apps):
        for ind in range(open_apps.shape[0]):
            if (open_apps.App.loc[ind] == ""):
                continue
            if (self.apps.path.loc[open_apps.App.loc[ind]] is None):
                self.apps.path.loc[open_apps.App.loc[ind]
                                   ] = open_apps.Path.loc[ind]

    def get_open_folders(self, open_apps):
        explorer_row = open_apps.loc[open_apps["Name"] == "explorer"]
        open_apps = open_apps[open_apps["Name"] != "explorer"]
        if not explorer_row.empty:
            open_folders = self.explorer.get_open_explorers(explorer_row)
            open_apps = open_apps.append(open_folders)
        return open_apps

    def compare_apps(self, new_apps, old_apps):
        concat_df = pd.concat([new_apps, old_apps], ignore_index=True)
        duplicated = concat_df.duplicated(
            subset=['Id', 'App', 'Name', 'Description', 'MainWindowTitle'],
            keep='first',
        )
        ended = [not dup for dup in duplicated[len(new_apps):]]
        now = datetime.now().isoformat()[0:-7]
        for ind in [i for i, e in enumerate(ended) if e]:
            if concat_df.loc[ind + len(new_apps.index)]["EndTime"] == "":
                concat_df.loc[ind + len(new_apps.index)]["EndTime"] = now

        duplicated_start = concat_df.duplicated(keep='last')
        started = [not dup for dup in duplicated_start[:len(new_apps)]]
        for ind in [i for i, e in enumerate(started) if e]:
            concat_df.loc[ind]["StartTime"] = now
        return concat_df.drop_duplicates(
            subset=['Id', 'App', 'Name', 'Description', 'MainWindowTitle'],
        ).sort_values(
            ["App", "Name", "StartTime", "EndTime"],
            ignore_index=True,
        )
