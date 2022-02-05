from rarian.gatherer.gatherer import Gatherer
from rarian.executor.executor import Executor
from rarian.project.projectsHandler import ProjectsHandler
from rarian.ui.cliClient import CLIent
import sys
import os
import json

src = os.path.abspath('./src')


class Manager:
    def __init__(self, data_dir):
        self.get_os()
        self.data_dir = data_dir
        self.log_dir = os.path.join(data_dir, "logs")
        self.load_data()

        self.projects_handler = ProjectsHandler(self.data_file, self.os)
        self.gatherer = Gatherer(self.log_dir, self.projects_handler, self.os)
        self.executor = Executor(self.projects_handler, self.quit, self.os)
        self.client = CLIent(self.executor)

    def get_os(self):
        if "win" in sys.platform:
            self.os = "windows"
        elif "linux" in sys.platform:
            self.os = "linux"
        else:
            raise TypeError("unknown system platform", sys.platform)

    def load_data(self):
        self.data_file = os.path.join(self.data_dir, "data.json")
        with open(self.data_file, 'r') as data_json:
            data_str = data_json.read()
        data = json.loads(data_str)
        self.projects = data["projects"]

    def run(self):
        self.projects_handler.start()
        self.gatherer.start()
        self.client.start()
        self.projects_handler.join()
        self.gatherer.join()
        self.client.join()

    def save(self):
        self.executor.save()

    def quit(self):
        self.gatherer.stop()
        self.client.stop()
        self.executor.stop()
