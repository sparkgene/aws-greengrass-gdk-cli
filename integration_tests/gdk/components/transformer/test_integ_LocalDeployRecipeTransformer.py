import json
from pathlib import Path
from gdk.commands.component.transformer.LocalDeployRecipeTransformer import LocalDeployRecipeTransformer
from unittest import TestCase

import pytest
import gdk.common.utils as utils
from gdk.commands.component.config.ComponentBuildConfiguration import ComponentBuildConfiguration
import os
import shutil

gradle_build_command = ["gradle", "clean", "build"]


@pytest.fixture()
def rglob_build_file(mocker):
    def search(*args, **kwargs):
        if "build.gradle" in args[0] or "pom.xml" in args[0]:
            return [Path(utils.current_directory).joinpath("build_file")]
        return []

    mock_rglob = mocker.patch("pathlib.Path.rglob", side_effect=search)
    return mock_rglob


class ComponentBuildCommandIntegTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = Path(tmpdir).resolve()
        self.c_dir = Path(".").resolve()
        self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config(),
        )
        os.chdir(self.tmpdir)

        yield
        os.chdir(self.c_dir)

    def test_transform_recipe(self):
        recipe = self.c_dir.joinpath("integration_tests/test_data/recipes").joinpath("local_recipe.yaml").resolve()
        shutil.copy(recipe, Path(self.tmpdir).joinpath("recipe.yaml").resolve())

        brg = LocalDeployRecipeTransformer(ComponentBuildConfiguration({}))
        new_recipe = self.tmpdir.joinpath("new.json")
        brg.transform(recipe, new_recipe, "1.2.3")

        assert new_recipe.is_file()

        with open(new_recipe, "r") as f:
            recipe_text = f.read()

            assert "{artifacts:decompressedPath}" not in recipe_text
            recipe = json.loads(recipe_text)
            # Artifact is removed
            assert "Artifacts" not in recipe["Manifests"][0]


def config():
    return {
        "component": {
            "component_name": {
                "author": "abc",
                "version": "1.0.0",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "default", "region": "us-east-1"},
            }
        },
        "gdk_version": "1.0.0",
    }
