import pytest
from pathlib import Path
from unittest import TestCase

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
