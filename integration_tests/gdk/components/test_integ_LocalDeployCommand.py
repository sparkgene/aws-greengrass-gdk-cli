from gdk.commands.component.LocalDeployCommand import LocalDeployCommand
import pytest
import os
from pathlib import Path
import shutil
from unittest import TestCase
from unittest.mock import Mock, patch
from unittest.mock import call


class LocalDeployCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = tmpdir
        self.c_dir = Path(".").resolve()
        os.chdir(tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_LocalDeployCommand_with_command_args(self):
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
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("local_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = LocalDeployCommand(command_args)
        assert comm.local_deploy_config.host == command_args["host"]
        assert comm.local_deploy_config.port == command_args["port"]
        assert comm.local_deploy_config.key_file == command_args["key_file"]
        assert comm.local_deploy_config.remote_component_dir == command_args["component_dir"]
        assert comm.local_deploy_config.greengrass_dir == command_args["greengrass_dir"]
        assert comm.local_deploy_config.component_version == "NEXT_PATCH"

    def test_LocalDeployCommand_default_settings(self):
        command_args = {}
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = LocalDeployCommand(command_args)
        assert comm.local_deploy_config.host == ""
        assert comm.local_deploy_config.port == "22"
        assert comm.local_deploy_config.key_file == ""
        assert comm.local_deploy_config.remote_component_dir == "~/greengrass-components"
        assert comm.local_deploy_config.greengrass_dir == "/greengrass/v2"

    def test_run_get_version_no_data(self):

        self.mocker.patch.object(LocalDeployCommand, "run_command", return_value="")
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = LocalDeployCommand({})
        version = comm._get_version()
        assert version == "0.0.1"

    def test_run_get_version_with_data(self):
        component_list = """
Components currently running in Greengrass:
Component Name: aws.greengrass.Cli
    Version: 2.13.0
    State: RUNNING
    Configuration: {"AuthorizedPosixGroups":null,"AuthorizedWindowsGroups":null}
Component Name: abc
    Version: 0.1.0
    State: RUNNING
    Configuration: null
"""

        self.mocker.patch.object(LocalDeployCommand, "run_command", return_value=component_list)
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = LocalDeployCommand({})
        print(comm.local_deploy_config.component_name)
        version = comm._get_version()
        assert version == "0.1.1"

    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "File transferred successfully"
        mock_run.return_value = mock_result
        self.mocker.patch("pathlib.Path.iterdir", return_value=["/path/to/artifacts"])
        self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        self.mocker.patch.object(LocalDeployCommand, "_get_version", return_value="1.1.1")
        self.mocker.patch.object(LocalDeployCommand, "_create_build_dir", return_value=None)
        self.mocker.patch.object(LocalDeployCommand, "_copy_artifacts", return_value=None)
        self.mocker.patch.object(LocalDeployCommand, "_create_recipe", return_value=None)
        self.mocker.patch.object(LocalDeployCommand, "_check_remote_dir_exist", return_value=None)
        self.mocker.patch.object(LocalDeployCommand, "_copy_to_remote", return_value=None)
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        comm = LocalDeployCommand({})
        comm.run()
        mock_run.assert_called_once_with(
            ['ssh', '-p', '8022', '-i', '/path/to/key', 'remote-user@remote_host',
             'sudo', '/path/to/greengrass/bin/greengrass-cli', 'deployment', 'create',
             '--merge', 'abc=1.1.1', '--recipeDir', '/path/to/component/recipes',
             '--artifactDir', '/path/to/component/artifacts'],
            shell=False, capture_output=True, text=True, timeout=60
        )

    def test_copy_to_remote(self):

        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/config/config_with_local.json"),
            Path(self.tmpdir).joinpath("gdk-config.json"),
        )
        shutil.copy(
            Path(self.c_dir).joinpath("integration_tests/test_data/recipes/").joinpath("build_recipe.yaml"),
            Path(self.tmpdir).joinpath("recipe.yaml"),
        )

        mock_spc_command = self.mocker.patch.object(LocalDeployCommand, "run_scp_command", return_value=None)

        comm = LocalDeployCommand({})
        comm._copy_to_remote()

        assert mock_spc_command.call_args_list == [
            call(str(comm.local_deploy_config.gg_local_build_dir.joinpath("artifacts")),
                 'remote-user@remote_host:/path/to/component/', timeout=300),
            call(str(comm.local_deploy_config.gg_local_build_dir.joinpath("recipes")),
                 'remote-user@remote_host:/path/to/component/', timeout=300)
            ]


def config_with_local_filled():
    return {
        "component": {
            "com.example.HelloWorld": {
                "author": "author",
                "version": "1.0.1",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "us-east-1"},
                "local": {
                    "host": "some.host.name",
                    "port": "1234",
                    "user": "my-user",
                    "key_file": "/path/to/key.pem",
                    "component_dir": "/path/to/component",
                    "greengrass_dir": "/path/to/greengrass"
                }
            }
        },
        "gdk_version": "1.0.0",
    }
