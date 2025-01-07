import pytest

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from gdk.commands.component.LocalDeployCommand import LocalDeployCommand
from gdk.common.config.GDKProject import GDKProject


class LocalDeployCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config(),
        )
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())

    def test_run_deploy_local(self):
        mock_build = self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        mock_create_build_dir = self.mocker.patch.object(LocalDeployCommand, "_create_build_dir", return_value=None)
        mock_copy_artifacts = self.mocker.patch.object(LocalDeployCommand, "_copy_artifacts", return_value=None)
        mock_create_recipe = self.mocker.patch.object(LocalDeployCommand, "_create_recipe", return_value=None)
        mock_check_remote_dir_exist = self.mocker.patch.object(LocalDeployCommand,
                                                               "_check_remote_dir_exist", return_value=None)
        mock_copy_to_remote = self.mocker.patch.object(LocalDeployCommand, "_copy_to_remote", return_value=None)
        mock_deploy = self.mocker.patch.object(LocalDeployCommand, "deploy", return_value=None)
        mock_subprocess_run = self.mocker.patch("subprocess.run")

        local_deploy = LocalDeployCommand({})
        local_deploy.run()

        assert not mock_subprocess_run.called
        assert mock_build.assert_called_once
        assert mock_create_build_dir.assert_called_once
        assert mock_copy_artifacts.assert_called_once
        assert mock_create_recipe.assert_called_once
        assert not mock_check_remote_dir_exist.called
        assert not mock_copy_to_remote.called
        assert mock_deploy.assert_called_once

    def test_run_deploy_remote(self):
        mock_build = self.mocker.patch("gdk.commands.component.component.build", return_value=None)
        mock_create_build_dir = self.mocker.patch.object(LocalDeployCommand, "_create_build_dir", return_value=None)
        mock_copy_artifacts = self.mocker.patch.object(LocalDeployCommand, "_copy_artifacts", return_value=None)
        mock_create_recipe = self.mocker.patch.object(LocalDeployCommand, "_create_recipe", return_value=None)
        mock_check_remote_dir_exist = self.mocker.patch.object(LocalDeployCommand,
                                                               "_check_remote_dir_exist", return_value=None)
        mock_copy_to_remote = self.mocker.patch.object(LocalDeployCommand, "_copy_to_remote", return_value=None)
        mock_deploy = self.mocker.patch.object(LocalDeployCommand, "deploy", return_value=None)
        mock_subprocess_run = self.mocker.patch("subprocess.run")

        local_deploy = LocalDeployCommand({"host": "somehost", "user": "someuser"})
        local_deploy.run()

        assert not mock_subprocess_run.called
        assert mock_build.assert_called_once
        assert mock_create_build_dir.assert_called_once
        assert mock_copy_artifacts.assert_called_once
        assert mock_create_recipe.assert_called_once
        assert mock_check_remote_dir_exist.assert_called_once
        assert mock_copy_to_remote.assert_called_once
        assert mock_deploy.assert_called_once

    def test_run_deploy_local_error(self):
        self.mocker.patch("gdk.commands.component.component.build", side_effect=Exception("Build failed"))

        local_deploy = LocalDeployCommand({})
        with pytest.raises(Exception) as exc_info:
            local_deploy.run()

        assert "Build failed" in str(exc_info.value)

    def test_deploy(self):
        mock_run_command = self.mocker.patch.object(LocalDeployCommand, "run_command", return_value=None)

        local_deploy = LocalDeployCommand({})
        local_deploy.deploy("1.0.0")

        assert mock_run_command.assert_called_once

    def test_get_version(self):
        self.mocker.patch.object(LocalDeployCommand, "run_command", return_value="dummy.component1\ndummy.component2")

        local_deploy = LocalDeployCommand({})
        local_deploy.local_deploy_config.component_version = "NEXT_PATCH"
        version = local_deploy._get_version()

        assert version == "0.0.1"

    def test_get_version_from_list(self):
        components = """
Components currently running in Greengrass:
Component Name: com.example.Dummy
Version: 1.0.0
State: RUNNING
Component Name: com.example.HelloWorld
Version: 2.0.0
State: RUNNING
"""
        self.mocker.patch.object(LocalDeployCommand, "run_command", return_value=components)

        local_deploy = LocalDeployCommand({})
        local_deploy.local_deploy_config.component_version = "NEXT_PATCH"
        version = local_deploy._get_version()

        assert version == "2.0.1"

    def test_copy_to_remote(self):
        mock_run_scp_command = self.mocker.patch.object(LocalDeployCommand, "run_scp_command", return_value=None)

        local_deploy = LocalDeployCommand({})
        local_deploy.local_deploy_config.user = "a"
        local_deploy.local_deploy_config.host = "b"
        local_deploy.local_deploy_config.remote_component_dir = "c"
        target_dir = (local_deploy.local_deploy_config.user + "@" +
                      local_deploy.local_deploy_config.host + ":" +
                      local_deploy.local_deploy_config.remote_component_dir + "/")

        local_deploy._copy_to_remote()

        source_dir = local_deploy.local_deploy_config.gg_local_build_dir
        mock_run_scp_command.assert_any_call(str(source_dir.joinpath('artifacts')), target_dir, timeout=300)
        mock_run_scp_command.assert_any_call(str(source_dir.joinpath('recipes')), target_dir, timeout=300)

    @patch('pathlib.Path.mkdir')
    def test_create_build_dir(self, mock_path):
        self.mocker.patch.object(LocalDeployCommand, "run_command", return_value="dummy.component1\ndummy.component2")
        self.mocker.patch("gdk.common.utils.clean_dir", return_value=None)

        local_deploy = LocalDeployCommand({})
        local_deploy._create_build_dir("1.0.0")

        mock_path.assert_any_call(local_deploy.local_deploy_config.gg_local_build_recipes_dir,
                                  parents=True, exist_ok=True)

    @patch('shutil.copytree')
    def test_copy_artifacts_zip_build(self, mock_shutil):

        local_deploy = LocalDeployCommand({})
        local_deploy._copy_artifacts("1.0.0")

        assert mock_shutil.assert_called_once

    @patch('shutil.copytree')
    def test_copy_artifacts_custom_build(self, mock_shutil):

        local_deploy = LocalDeployCommand({})
        local_deploy.project_config.build_system = "custom"
        local_deploy._copy_artifacts("1.0.0")

        assert mock_shutil.assert_called_once


def config():
    return {
        "component": {
            "com.example.HelloWorld": {
                "author": "<PLACEHOLDER_AUTHOR>",
                "version": "1.0.0",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "region"},
            }
        },
        "gdk_version": "1.0.0",
    }
