from pathlib import Path
from unittest import TestCase
import pytest
import gdk.common.consts as consts


from gdk.commands.component.config.ComponentLocalConfiguration import ComponentLocalConfiguration
from gdk.common.config.GDKProject import GDKProject
import gdk.common.utils as utils


class ComponentLocalConfigurationTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker
        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())

    def test_config_with_no_local_config_and_no_arguments(self):
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config_without_local(),
        )
        project_dir = utils.get_current_directory()
        pconfig = ComponentLocalConfiguration({})
        assert pconfig.host == ""
        assert pconfig.user == ""
        assert pconfig.port == "22"
        assert pconfig.key_file == ""
        assert pconfig.remote_component_dir == consts.greengrass_local_build_dir
        assert pconfig.greengrass_dir == "/greengrass/v2"
        assert pconfig.component_version == "1.0.0"
        gg_local_build_dir = Path(project_dir).joinpath(consts.greengrass_local_build_dir).resolve()
        assert pconfig.gg_local_build_dir == gg_local_build_dir
        gg_local_build_artifacts_dir = gg_local_build_dir.joinpath("artifacts").resolve()
        assert pconfig.gg_local_build_artifacts_dir == gg_local_build_artifacts_dir
        gg_local_build_component_artifacts_dir = gg_local_build_artifacts_dir.joinpath(
            pconfig.component_name, pconfig.component_version)
        assert pconfig.gg_local_build_component_artifacts_dir == gg_local_build_component_artifacts_dir
        gg_local_build_recipes_dir = gg_local_build_dir.joinpath("recipes").resolve()
        assert pconfig.gg_local_build_recipes_dir == gg_local_build_recipes_dir
        deploy_recipe_file = gg_local_build_recipes_dir.joinpath(
            f"{pconfig.component_name}-{pconfig.component_version}.{pconfig.recipe_file.name.split('.')[-1]}"
        )
        assert pconfig.deploy_recipe_file == deploy_recipe_file

    def test_config_with_no_local_config_and_arguments(self):
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config_without_local(),
        )
        project_dir = utils.get_current_directory()
        pconfig = ComponentLocalConfiguration({
            "host": "arg_host",
            "user": "arg_user",
            "port": "1111",
            "key_file": "test_key_file",
            "component_dir": "test_remote_component_dir",
            "greengrass_dir": "test_greengrass_dir"
        })

        assert pconfig.host == "arg_host"
        assert pconfig.user == "arg_user"
        assert pconfig.port == "1111"
        assert pconfig.key_file == "test_key_file"
        assert pconfig.remote_component_dir == "test_remote_component_dir"
        assert pconfig.greengrass_dir == "test_greengrass_dir"
        assert pconfig.component_version == "1.0.0"
        gg_local_build_dir = Path(project_dir).joinpath(consts.greengrass_local_build_dir).resolve()
        assert pconfig.gg_local_build_dir == gg_local_build_dir
        gg_local_build_artifacts_dir = gg_local_build_dir.joinpath("artifacts").resolve()
        assert pconfig.gg_local_build_artifacts_dir == gg_local_build_artifacts_dir
        gg_local_build_component_artifacts_dir = gg_local_build_artifacts_dir.joinpath(
            pconfig.component_name, pconfig.component_version)
        assert pconfig.gg_local_build_component_artifacts_dir == gg_local_build_component_artifacts_dir
        gg_local_build_recipes_dir = gg_local_build_dir.joinpath("recipes").resolve()
        assert pconfig.gg_local_build_recipes_dir == gg_local_build_recipes_dir
        deploy_recipe_file = gg_local_build_recipes_dir.joinpath(
            f"{pconfig.component_name}-{pconfig.component_version}.{pconfig.recipe_file.name.split('.')[-1]}"
        )
        assert pconfig.deploy_recipe_file == deploy_recipe_file

    def test_config_with_empty_local_config_and_no_arguments(self):
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config_with_local_blank(),
        )
        project_dir = utils.get_current_directory()
        pconfig = ComponentLocalConfiguration({})
        assert pconfig.host == ""
        assert pconfig.user == ""
        assert pconfig.port == "22"
        assert pconfig.key_file == ""
        assert pconfig.remote_component_dir == consts.greengrass_local_build_dir
        assert pconfig.greengrass_dir == "/greengrass/v2"
        assert pconfig.component_version == "1.0.0"
        gg_local_build_dir = Path(project_dir).joinpath(consts.greengrass_local_build_dir).resolve()
        assert pconfig.gg_local_build_dir == gg_local_build_dir
        gg_local_build_artifacts_dir = gg_local_build_dir.joinpath("artifacts").resolve()
        assert pconfig.gg_local_build_artifacts_dir == gg_local_build_artifacts_dir
        gg_local_build_component_artifacts_dir = gg_local_build_artifacts_dir.joinpath(
            pconfig.component_name, pconfig.component_version)
        assert pconfig.gg_local_build_component_artifacts_dir == gg_local_build_component_artifacts_dir
        gg_local_build_recipes_dir = gg_local_build_dir.joinpath("recipes").resolve()
        assert pconfig.gg_local_build_recipes_dir == gg_local_build_recipes_dir
        deploy_recipe_file = gg_local_build_recipes_dir.joinpath(
            f"{pconfig.component_name}-{pconfig.component_version}.{pconfig.recipe_file.name.split('.')[-1]}"
        )
        assert pconfig.deploy_recipe_file == deploy_recipe_file

    def test_config_with_local_config_and_no_arguments(self):
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config_with_local_filled(),
        )
        project_dir = utils.get_current_directory()
        pconfig = ComponentLocalConfiguration({})
        assert pconfig.host == "some.host.name"
        assert pconfig.user == "my-user"
        assert pconfig.port == "1234"
        assert pconfig.key_file == "/path/to/key.pem"
        assert pconfig.remote_component_dir == "/path/to/component"
        assert pconfig.greengrass_dir == "/path/to/greengrass"
        assert pconfig.component_version == "1.0.1"
        gg_local_build_dir = Path(project_dir).joinpath(consts.greengrass_local_build_dir).resolve()
        assert pconfig.gg_local_build_dir == gg_local_build_dir
        gg_local_build_artifacts_dir = gg_local_build_dir.joinpath("artifacts").resolve()
        assert pconfig.gg_local_build_artifacts_dir == gg_local_build_artifacts_dir
        gg_local_build_component_artifacts_dir = gg_local_build_artifacts_dir.joinpath(
            pconfig.component_name, pconfig.component_version)
        assert pconfig.gg_local_build_component_artifacts_dir == gg_local_build_component_artifacts_dir
        gg_local_build_recipes_dir = gg_local_build_dir.joinpath("recipes").resolve()
        assert pconfig.gg_local_build_recipes_dir == gg_local_build_recipes_dir
        deploy_recipe_file = gg_local_build_recipes_dir.joinpath(
            f"{pconfig.component_name}-{pconfig.component_version}.{pconfig.recipe_file.name.split('.')[-1]}"
        )
        assert pconfig.deploy_recipe_file == deploy_recipe_file

    def test_config_with_invalid_local_config_host(self):
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config_with_invalid_local_host(),
        )
        with pytest.raises(Exception) as err:
            ComponentLocalConfiguration({})
        assert "SSH user configuration is required for remote command." == err.value.args[0]

    def test_config_with_invalid_local_config_user(self):
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config_with_invalid_local_user(),
        )
        with pytest.raises(Exception) as err:
            ComponentLocalConfiguration({})
        assert "SSH host configuration is required for remote command." == err.value.args[0]


def config_without_local():
    return {
        "component": {
            "com.example.HelloWorld": {
                "author": "author",
                "version": "1.0.0",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "us-east-1"},
            }
        },
        "gdk_version": "1.0.0",
    }


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


def config_with_local_blank():
    return {
        "component": {
            "com.example.HelloWorld": {
                "author": "author",
                "version": "1.0.0",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "us-east-1"},
                "local": {
                    "host": "",
                    "port": "",
                    "user": "",
                    "key_file": "",
                    "component_dir": "",
                    "greengrass_dir": ""
                }
            }
        },
        "gdk_version": "1.0.0",
    }


def config_with_invalid_local_host():
    return {
        "component": {
            "com.example.HelloWorld": {
                "author": "author",
                "version": "1.0.1",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "us-east-1"},
                "local": {
                    "host": "some.host.name"
                }
            }
        },
        "gdk_version": "1.0.0",
    }


def config_with_invalid_local_user():
    return {
        "component": {
            "com.example.HelloWorld": {
                "author": "author",
                "version": "1.0.1",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "us-east-1"},
                "local": {
                    "user": "some_user"
                }
            }
        },
        "gdk_version": "1.0.0",
    }
