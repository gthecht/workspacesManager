import pandas as pd
import pytest
import threading
import queue
from rarian.executor.executor import Executor


class ProjectsHandlerMock(threading.Thread):
    def __init__(self):
        self.q = queue.Queue()
        self.running = True
        super().__init__(name="projectHandler", daemon=True)

    def run(self):
        while self.running:
            job = self.q.get()
            if "reply_q" in job.keys():
                job["reply_q"].put(job)

    def stop(self):
        self.running = False


projects_handler = ProjectsHandlerMock()


def quit():
    return


executor = Executor(projects_handler, quit)


@pytest.fixture
def get_executor():
    executor.projects_handler = ProjectsHandlerMock()
    executor.projects_handler.start()
    yield executor
    executor.projects_handler.stop()


@pytest.fixture
def get_projects_handler_mock():
    return ProjectsHandlerMock


@pytest.fixture
def files_df():
    return pd.DataFrame({
        "name": ["one", "two", "three"],
        "type": ["txt", "csv", "json"],
        "FullName": ["path/one", "path/two", "path/three"],
    })


@pytest.fixture
def files_list():
    return [
        {
            "name": "one",
            "type": "txt",
            "FullName": "path/one",
        },
        {
            "name": "two",
            "type": "csv",
            "FullName": "path/two",
        },
        {
            "name": "three",
            "type": "json",
            "FullName": "path/three",
        },
    ]
