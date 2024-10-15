from gdk.commands.component.LocalListCommand import LocalListCommand
import pytest
import os
from pathlib import Path
import shutil
from unittest import TestCase
from unittest.mock import Mock, patch


class LocalListCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = tmpdir
        self.c_dir = Path(".").resolve()
        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    @patch("subprocess.run")
    def test_LocalListCommand(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "File transferred successfully"
        mock_run.return_value = mock_result

        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = LocalListCommand({})
        comm.run()
        mock_run.assert_called_once_with(
            ["sudo", "/greengrass/v2/bin/greengrass-cli", "component", "list"],
            shell=False, capture_output=True, text=True, timeout=60
        )

    @patch("subprocess.run")
    def test_LocalListCommand_with_command_args(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "File transferred successfully"
        mock_run.return_value = mock_result

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

        comm = LocalListCommand(command_args)
        comm.run()
        mock_run.assert_called_once_with(
            ["ssh", "-p", "1234", "-i", "/args/path/to/key", "my-user@my-host",
             "sudo", "/args/path/to/greengrass/bin/greengrass-cli", "component", "list"],
            shell=False, capture_output=True, text=True, timeout=60
        )

    @patch("subprocess.run")
    def test_LocalListCommand_on_remote(self, mock_run):
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

        comm = LocalListCommand({})
        comm.run()
        mock_run.assert_called_once_with(
            ["ssh", "-p", "8022", "-i", "/path/to/key", "remote-user@remote_host",
             "sudo", "/path/to/greengrass/bin/greengrass-cli", "component", "list"],
            shell=False, capture_output=True, text=True, timeout=60
        )
