from time import sleep
from os import path
from datetime import datetime
import pandas as pd
import threading
import queue

from rarian.gatherer.appsGatherer import AppsGatherer
from rarian.gatherer.filesGatherer import FilesGatherer


class Gatherer(threading.Thread):
    def __init__(self, log_dir, projects_handler, os="windows"):
        self.log_dir = log_dir
        self.os = os
        self.apps_gatherer = AppsGatherer(self.os)
        self.files_gatherer = FilesGatherer(self.os)
        self.projects_handler = projects_handler
        self.reply_q = queue.Queue()

        self.running = False
        self.apps_log_file = path.join(
            self.log_dir,
            "log-" + datetime.now().strftime('%Y-%m-%dT%H-%M-%S') + ".csv"
        )
        # time to sleep between data collection
        self.SLEEP_TIME = 1
        super().__init__(name="gatherer", daemon=True)

    def add_job(self, job):
        self.projects_handler.q.put(job)
        if "reply_q" not in job.keys():
            return
        else:
            reply = None
            while self.reply_q.empty():
                if not self.running:
                    return False
                continue
            reply = self.reply_q.get()
            return reply

    def run(self):
        self.running = True
        while self.running:
            if not self.running:
                break
            self.gather_iteration()

    def gather_iteration(self):
        sleep(self.SLEEP_TIME)
        now = datetime.now().isoformat()[0:-7]
        try:
            self.gather_files()
            self.gather_apps()
            self.cross_files_apps()
            job = {
                "method": "update",
                "args": {
                    "open_files": self.open_files,
                },
            }
            self.add_job(job)
            self.log(now)

        except Exception as err:
            print("Failed to gather data with err: " + str(err))
            print("Waiting a bit, and trying to gather again")

    def gather_files(self):
        project_paths = self.projects_handler.get_proj_dirs()
        proj_paths_job = {
            "method": "get_proj_dirs",
            "args": {},
            "reply_q": self.reply_q
        }
        self.add_job(proj_paths_job)
        project_time = self.projects_handler.get_proj_start_time()
        proj_time_job = {
            "method": "get_proj_start_time",
            "args": {},
            "reply_q": self.reply_q
        }
        self.add_job(proj_time_job)
        self.open_files = self.files_gatherer.get_open_files(
            project_paths, project_time)

    def gather_apps(self):
        self.open_apps = self.apps_gatherer.get_open_apps()

    def cross_files_apps(self):
        cross_correlation = pd.DataFrame(columns=self.open_files.columns)
        for file_ind in self.open_files.index:
            file = self.open_files.loc[file_ind]
            for app_ind in self.open_apps.index:
                app = self.open_apps.loc[app_ind]
                if len(file.Name) == 0:
                    continue
                if file.Name.lower() in app.MainWindowTitle.lower():
                    file["App"] = app.Path
                    file["value"] = len(file.Name) / len(app.MainWindowTitle)
                    cross_correlation = cross_correlation.append(
                        file, ignore_index=True)
        if cross_correlation.empty:
            self.open_files = cross_correlation
        else:
            # Take only the single file with the maximum value:
            # may want to change this to multiple later on
            self.open_files = cross_correlation.loc[
                cross_correlation.groupby(['App'])['value'].idxmax()
            ].reset_index(drop=True)

    def log(self, now):
        if self.open_apps.empty:
            return
        job = {
            "method": "get_current",
            "args": {},
            "reply_q": self.reply_q
        }
        current_proj = self.add_job(job)
        log = self.open_apps.copy()
        log["Project"] = current_proj
        log["TimeStamp"] = now
        self.add_open_file_paths(log)
        log = self.clean_log(log)
        log.to_csv(self.apps_log_file, mode='a', index=False, header=False)

    def add_open_file_paths(self, log):
        log["FilePath"] = ''
        if not self.open_files.empty:
            log["FilePath"][log["Path"].isin(self.open_files["App"])] = \
                self.open_files.index[self.open_files["App"].isin(log["Path"])]
        return log

    def clean_log(self, log):
        clean_log = log.drop(
            [
                "Id",
                "Name",
                "Description",
                "MainWindowTitle",
                "StartTime",
                "EndTime",
            ],
            axis=1
        )
        clean_log = clean_log.rename(columns={"Path": "AppPath"})
        return clean_log

    def stop(self):
        self.running = False
        job = {
            "method": "stop",
            "args": {},
        }
        self.add_job(job)
