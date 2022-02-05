import queue
from rarian.gatherer.appsGatherer import AppsGatherer
from rarian.gatherer.filesGatherer import FilesGatherer


class TestGatherer:
    def test_constructor(self, get_gatherer, test_path, get_projects_handler):
        """should have all the correct arguments"""
        gatherer = get_gatherer
        print(f'gatherer: {type(gatherer)}')
        assert gatherer.log_dir == test_path
        assert gatherer.os == "windows"
        assert type(gatherer.apps_gatherer) == AppsGatherer
        assert type(gatherer.files_gatherer) == FilesGatherer
        assert gatherer.projects_handler == get_projects_handler
        assert type(gatherer.reply_q) == queue.Queue

    def test_run_gather_files(self, get_gatherer, mocker):
        """should call gather_files function"""
        gatherer = get_gatherer
        mock_gather_files = mocker.patch("rarian.Gatherer.gather_files")
        mock_gather_apps = mocker.patch("rarian.Gatherer.gather_apps")
        gatherer.gather_iteration()
        assert mock_gather_files.call_count == 1
        assert mock_gather_apps.call_count == 1

    def test_run_add_job(self, get_gatherer, mocker):
        """should add a job"""
        gatherer = get_gatherer
        mock_add_job = mocker.patch("rarian.Gatherer.add_job")
        mocker.patch("rarian.Gatherer.gather_files", return_value=None)
        mocker.patch("rarian.Gatherer.gather_apps", return_value=None)
        mocker.patch("rarian.Gatherer.cross_files_apps", return_value=None)
        gatherer.open_files = "open files"
        gatherer.open_apps = "open apps"
        gatherer.gather_iteration()
        assert mock_add_job.call_count == 1
        mock_add_job.assert_called_once_with({
            "method": "update",
            "args": {
                "open_files": gatherer.open_files,
            },
        })

    def test_gather_files_get_proj_dirs(self, get_gatherer, mocker):
        """should get proj dirs"""
        gatherer = get_gatherer
        proj_handler_mock = mocker.patch(
            'rarian.ProjectsHandler.get_proj_dirs')
        gatherer.projects_handler = proj_handler_mock()
        gatherer.gather_files()
        assert proj_handler_mock.call_count == 1
        proj_handler_mock.assert_called_once_with()

    def test_gather_files_get_proj_start_time(self, get_gatherer, mocker):
        """should get proj start time"""
        gatherer = get_gatherer
        proj_handler_mock = mocker.patch(
            'rarian.ProjectsHandler.get_proj_start_time')
        gatherer.projects_handler = proj_handler_mock()
        gatherer.gather_files()
        assert proj_handler_mock.call_count == 1
        proj_handler_mock.assert_called_once_with()

    def test_gather_files_call_files_gatherer(self, get_gatherer, mocker):
        """should get proj call files gatherer"""
        gatherer = get_gatherer
        files_gatherer_mock = mocker.patch('rarian.FilesGatherer')
        gatherer.files_gatherer = files_gatherer_mock()
        gatherer.gather_files()
        assert files_gatherer_mock.call_count == 1

    def test_gather_apps(self, get_gatherer, mocker):
        """should gather_apps"""
        gatherer = get_gatherer
        apps_gatherer_mock = mocker.patch('rarian.AppsGatherer')
        gatherer.apps_gatherer = apps_gatherer_mock()
        gatherer.gather_files()
        assert apps_gatherer_mock.call_count == 1

    def test_stop_running_to_false(self, get_gatherer):
        """should set running to false"""
        gatherer = get_gatherer
        gatherer.running = True
        gatherer.stop()
        assert gatherer.running is False

    def test_stop_send_stop_to_projects_handler(self, get_gatherer, mocker):
        """should create stop job for projects handler"""
        gatherer = get_gatherer
        mock_add_job = mocker.patch("rarian.Gatherer.add_job")
        gatherer.stop()
        assert mock_add_job.call_count == 1
        mock_add_job.assert_called_once_with({
            "method": "stop",
            "args": {},
        })
