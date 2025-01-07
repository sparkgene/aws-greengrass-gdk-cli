import pytest
import os
from pathlib import Path
import shutil
from unittest import TestCase
from unittest.mock import Mock, patch

from gdk.commands.RemoteCommand import RemoteCommand


class RemoteCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = tmpdir
        self.c_dir = Path(".").resolve()
        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_RemoteCommand_with_command_args(self):
        command_args = {
            "host": "my-host",
            "port": "1234",
            "user": "my-user",
            "key_file": "/args/path/to/key",
            "component_dir": "/args/path/to/component",
            "greengrass_dir": "/args/path/to/greengrass",
        }
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand(command_args)
        assert comm.local_deploy_config.host == command_args["host"]
        assert comm.local_deploy_config.port == command_args["port"]
        assert comm.local_deploy_config.key_file == command_args["key_file"]
        assert comm.local_deploy_config.remote_component_dir == command_args["component_dir"]
        assert comm.local_deploy_config.greengrass_dir == command_args["greengrass_dir"]
        assert comm.local_deploy_config.component_version == "NEXT_PATCH"

    def test_RemoteCommand_default_settings(self):
        command_args = {}
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand(command_args)
        assert comm.local_deploy_config.host == ""
        assert comm.local_deploy_config.port == "22"
        assert comm.local_deploy_config.key_file == ""
        assert comm.local_deploy_config.remote_component_dir == "~/greengrass-components"
        assert comm.local_deploy_config.greengrass_dir == "/greengrass/v2"

    def test_RemoteCommand_config_settings(self):
        command_args = {}
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand(command_args)
        assert comm.local_deploy_config.host == "remote_host"
        assert comm.local_deploy_config.port == "8022"
        assert comm.local_deploy_config.user == "remote-user"
        assert comm.local_deploy_config.key_file == "/path/to/key"
        assert comm.local_deploy_config.remote_component_dir == "/path/to/component"
        assert comm.local_deploy_config.greengrass_dir == "/path/to/greengrass"

    @patch('subprocess.run')
    def test_run_scp_command_success(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "File transferred successfully"
        mock_run.return_value = mock_result

        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand({})
        comm.run_scp_command("source", "destination")
        mock_run.assert_called_once_with(
            ['scp', '-r', '-P', '8022', '-i', '/path/to/key', 'source', 'destination'],
            shell=False, capture_output=True, text=True, timeout=60
        )

    @patch('subprocess.run')
    def test_run_scp_command_failure(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "Some stdout"
        mock_result.stderr = "Some error occurred"
        mock_run.return_value = mock_result

        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand({})
        with pytest.raises(Exception) as exc_info:
            comm.run_scp_command("source_file", "destination_file")

        assert "Command failed: scp -r -P 8022 -i /path/to/key source_file destination_file" in str(exc_info.value)

    @patch('subprocess.run')
    def test_run_command_on_remote_success(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Run Command executed successfully"
        mock_run.return_value = mock_result

        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand({})
        comm.run_command(["ls"])
        mock_run.assert_called_once_with(
            ['ssh', '-p', '8022', '-i', '/path/to/key', 'remote-user@remote_host', 'ls'],
            shell=False, capture_output=True, text=True, timeout=60
        )

    @patch('subprocess.run')
    def test_run_command_on_local_success(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Run Command executed successfully"
        mock_run.return_value = mock_result

        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand({})
        comm.run_command(["ls"])
        mock_run.assert_called_once_with(
            ['ls'],
            shell=False, capture_output=True, text=True, timeout=60
        )

    @patch('subprocess.run')
    def test_run_command_on_local_fail(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "Run Command execute failed"
        mock_run.return_value = mock_result

        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand({})
        with pytest.raises(Exception) as e:
            comm.run_command(["ls"])
        assert (
            "Command failed: ls"
            == e.value.args[0]
        )

    @patch('subprocess.run')
    def test_check_remote_dir_exists(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Run Command executed successfully"
        mock_run.return_value = mock_result

        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand({})
        comm._check_remote_dir_exist()
        mock_run.assert_called_once_with(
            ['ssh', '-p', '8022', '-i', '/path/to/key',
             'remote-user@remote_host', 'ls', '/path/to/component'],
            shell=False, capture_output=True, text=True, timeout=60
        )

    @patch('subprocess.run')
    def test_check_remote_dir_exists_with_create(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "No such file or directory"
        mock_run.return_value = mock_result

        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand({})
        mock_create_remote_dir = self.mocker.patch.object(comm, "_create_remote_dir", return_value=None)
        comm._check_remote_dir_exist()
        assert mock_create_remote_dir.assert_called_once

    @patch('subprocess.run')
    def test_check_remote_dir_exists_fail(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Command failed"
        mock_run.return_value = mock_result

        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand({})
        with pytest.raises(Exception) as e:
            comm._check_remote_dir_exist()
        assert (
            "Command failed: ssh -p 8022 -i /path/to/key remote-user@remote_host ls /path/to/component"
            == e.value.args[0]
        )

    @patch('subprocess.run')
    def test_create_remote_dir(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Run Command executed successfully"
        mock_run.return_value = mock_result

        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand({})
        comm._create_remote_dir()
        mock_run.assert_called_once_with(
            ['ssh', '-p', '8022', '-i', '/path/to/key',
             'remote-user@remote_host', 'mkdir', '-p', '/path/to/component'],
            shell=False, capture_output=True, text=True, timeout=60
        )

    @patch('subprocess.run')
    def test_create_remote_dir_fail(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "Run create directory failed"
        mock_run.return_value = mock_result

        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = RemoteCommand({})
        with pytest.raises(Exception) as e:
            comm._create_remote_dir()
        assert (
            "Command failed: ssh -p 8022 -i /path/to/key remote-user@remote_host mkdir -p /path/to/component"
            == e.value.args[0]
        )
