import pandas as pd
import pytest
import queue


class TestExecutor:
    def test_constructor(self, get_executor, get_projects_handler_mock):
        """should have all the correct members"""
        executor = get_executor
        assert type(executor.projects_handler) == get_projects_handler_mock
        assert executor.running
        assert executor.os == "windows"
        assert executor.data == {
            "files": None,
            "apps": None,
            "urls": None,
            "notes": None,
            "projects": None
        }
        assert executor.bookmarks == executor.data
        assert type(executor.reply_q) == queue.Queue

    def test_add_job_no_reply(self, get_executor, mocker):
        """should send projects Handler the job and not await a reply"""
        executor = get_executor
        queue_mock = mocker.patch("queue.Queue.put")
        job = {
            "method": "job",
            "args": {}
        }
        executor.add_job(job)
        assert queue_mock.call_count == 1
        queue_mock.assert_called_once_with(job)

    @pytest.mark.skip(reason="waits for reply in endless loop")
    def test_add_job_with_reply(self, get_executor):
        """should send projects Handler the job and await a reply"""
        executor = get_executor
        job = {
            "method": "job",
            "args": {},
            "reply_q": executor.reply_q
        }
        reply = executor.add_job(job)
        assert reply == job

    def test_set_current(self, get_executor):
        """should send 'set current' job to project handler """
        executor = get_executor
        name = 'project'
        path = 'path/to/project'
        job = {
            "method": "set_current",
            "args": {
                "name": name,
                "path": path,
            },
            "reply_q": executor.reply_q
        }
        reply = executor.set_current(name, path)
        assert reply == job

    def test_save(self, get_executor, mocker):
        """should send save job to projects handler"""
        executor = get_executor
        job = {
            "method": "save",
            "args": {},
        }
        job_mock = mocker.patch('rarian.Executor.add_job')
        executor.save()
        assert job_mock.call_count == 1
        job_mock.assert_called_once_with(job)

    def test_close_project(self, get_executor, mocker):
        """should send close current job to project handler"""
        executor = get_executor
        job = {
            "method": "close_project",
            "args": {}
        }
        job_mock = mocker.patch('rarian.Executor.add_job')
        executor.close_project()
        assert job_mock.call_count == 1
        job_mock.assert_called_once_with(job)

    def test_new_project_with_all_args(self, get_executor, mocker):
        """should send new project job to project handler"""
        executor = get_executor
        job = {
            "method": "new_project",
            "args": {
                "paths": ["path/to/project"],
                "name": "project name",
                "proj_type": "proj type",
                "author": "author",
                "start_time": "now",
                "dirs": None,
                "files": None,
                "apps": None,
            },
            "reply_q": executor.reply_q,
        }
        job_mock = mocker.patch('rarian.Executor.add_job')
        executor.new_project(**job["args"])
        assert job_mock.call_count == 1
        job_mock.assert_called_once_with(job)

    @pytest.mark.skip(reason="missing fields not implemented in executor")
    def test_new_project_with_missing_args(self, get_executor):
        """should request missing args from caller"""

    @pytest.mark.skip(reason="not implemented")
    def test_new_file(self, get_executor):
        """should create a new file"""

    def test_open_file_with_default_app(self, get_executor, mocker):
        """should open given file with default app"""
        executor = get_executor
        ps_mock = mocker.patch("rarian.PSClient.run_powershell")
        file_df = pd.DataFrame(
            {"name": ["filename"], "FullName": ["/path/to/file"]})
        file_df = file_df.set_index("FullName")
        executor.open_file(file_df)
        cmd = 'Invoke-Item "/path/to/file"'
        assert ps_mock.call_count == 1
        ps_mock.assert_called_once_with(cmd)

    def test_open_file_with_given_app(self, get_executor, mocker):
        """should open given file with given app"""
        executor = get_executor
        ps_mock = mocker.patch("rarian.PSClient.run_powershell")
        file_df = pd.DataFrame(
            {"name": ["filename"], "FullName": ["/path/to/file"]})
        file_df = file_df.set_index("FullName")
        app = "notepad.exe"
        executor.open_file(file_df, app)
        cmd = '& "notepad.exe" "/path/to/file"'
        assert ps_mock.call_count == 1
        ps_mock.assert_called_once_with(cmd)

    @pytest.mark.skip(reason="not implemented")
    def test_open_file_in_thread(self, get_executor):
        """should open given file with given app in a separate thread"""
        assert True

    @pytest.mark.skip(reason="not implemented")
    def test_open_app(self, get_executor):
        """should open a project app"""

    @pytest.mark.skip(reason="not implemented")
    def test_new_note(self, get_executor):
        """should create a new note"""

    def test_remove_sub_dir(self, get_executor, mocker):
        """should create job to remove given path"""
        executor = get_executor
        path = "/path/to/file"
        job = {
            "method": "remove_sub_dir",
            "args": {
                "path": path,
            },
            "reply_q": executor.reply_q,
        }
        job_mock = mocker.patch('rarian.Executor.add_job')
        executor.remove_sub_dir(path)
        assert job_mock.call_count == 1
        job_mock.assert_called_once_with(job)

    def test_get_open(self, get_executor, mocker):
        """should create job to get open project data"""
        executor = get_executor
        job = {
            "method": "get_open",
            "args": {},
            "reply_q": executor.reply_q,
        }
        job_mock = mocker.patch('rarian.Executor.add_job')
        executor.get_open()
        assert job_mock.call_count == 1
        job_mock.assert_called_once_with(job)

    def test_get_current(self, get_executor, mocker):
        """should create job to get current project"""
        executor = get_executor
        job = {
            "method": "get_current",
            "args": {},
            "reply_q": executor.reply_q,
        }
        job_mock = mocker.patch('rarian.Executor.add_job')
        executor.get_current()
        assert job_mock.call_count == 1
        job_mock.assert_called_once_with(job)

    def test_get_data(self, get_executor, mocker):
        """should create job to get data of type member"""
        executor = get_executor
        job = {
            "method": "get_project_data",
            "args": {
                "member": "files",
                "sort_by": "Relevance"
            },
            "reply_q": executor.reply_q
        }
        job_mock = mocker.patch('rarian.Executor.add_job')
        executor.get_data("files")
        assert job_mock.call_count == 1
        job_mock.assert_called_once_with(job)

    def test_get_data_data_frame(self, get_executor, files_df, mocker):
        """should place data_frame in self.data and return first row"""
        executor = get_executor
        job_mock = mocker.patch('rarian.Executor.add_job')
        job_mock.return_value = files_df
        file_out = executor.get_data("files")
        assert file_out.loc[0].eq(files_df.loc[0]).all()
        assert files_df.equals(executor.data["files"])

    def test_get_data_list(self, get_executor, files_list, mocker):
        """should place the list in self.data and return first row"""
        executor = get_executor
        job_mock = mocker.patch('rarian.Executor.add_job')
        job_mock.return_value = files_list
        file_out = executor.get_data("files")
        assert file_out[0] == files_list[0]
        assert files_list == executor.data["files"]

    def test_get_data_sorted_by(self, get_executor, mocker):
        """should create job to get data of type member, sorted by"""
        executor = get_executor
        job = {
            "method": "get_project_data",
            "args": {
                "member": "files",
                "sort_by": "sort_value"
            },
            "reply_q": executor.reply_q
        }
        job_mock = mocker.patch('rarian.Executor.add_job')
        executor.get_data("files", 1, "sort_value")
        assert job_mock.call_count == 1
        job_mock.assert_called_once_with(job)

    def test_get_data_return_number(self, get_executor, files_df, mocker):
        """should return n rows of member"""
        executor = get_executor
        job_mock = mocker.patch('rarian.Executor.add_job')
        job_mock.return_value = files_df
        file_out = executor.get_data("files", 2)
        assert len(file_out.index) == 2
        file_out = executor.get_data("files", 3)
        assert len(file_out.index) == 3
        assert files_df.equals(file_out)

    def test_get_data_n_greater_than_len(self, get_executor, files_df, mocker):
        """should return minimum between n and len"""
        executor = get_executor
        job_mock = mocker.patch('rarian.Executor.add_job')
        job_mock.return_value = files_df
        file_out = executor.get_data("files", 5)
        assert len(file_out.index) == 3
        assert files_df.equals(file_out)

    def test_get_more(self, get_executor, files_df):
        """should get more of member, n items"""
        executor = get_executor
        executor.data["files"] = files_df
        executor.bookmarks["files"] = 1
        file_out = executor.get_more("files")
        assert file_out.iloc[0].eq(files_df.loc[1]).all()

    def test_get_more_update_bookmark(self, get_executor, files_df):
        """should update the bookmark for the member"""
        executor = get_executor
        executor.data["files"] = files_df
        executor.bookmarks["files"] = 1
        executor.get_more("files")
        assert executor.bookmarks["files"] == 2

    def test_get_previous(self, get_executor, files_df):
        """should get previous of member when n is negative"""
        executor = get_executor
        executor.data["files"] = files_df
        executor.bookmarks["files"] = 2
        file_out = executor.get_more("files", -1)
        assert file_out.iloc[0].eq(files_df.loc[1]).all()
        assert executor.bookmarks["files"] == 1

    def test_get_nothing_n_is_0(self, get_executor, files_df):
        """should get empty list if n=0"""
        executor = get_executor
        executor.data["files"] = files_df
        executor.bookmarks["files"] = 1
        file_out = executor.get_more("files", 0)
        assert file_out.empty
        assert executor.bookmarks["files"] == 1

    def test_get_more_member_doesnt_exist(self, get_executor):
        """should return None if member doesn't exist"""
        executor = get_executor
        file_out = executor.get_more("nonexistant", 5)
        assert file_out is None

    def test_stop(self, get_executor):
        """should stop running"""
        executor = get_executor
        executor.stop()
        assert executor.running is False
