from pathlib import Path
from unittest import TestCase

import pytest

from gdk.commands.component.transformer.LocalDeployRecipeTransformer import LocalDeployRecipeTransformer
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile, CaseInsensitiveDict
from gdk.commands.component.config.ComponentLocalConfiguration import ComponentLocalConfiguration
from gdk.common.config.GDKProject import GDKProject


class LocalDeployRecipeTransformerTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = Path(tmpdir).resolve()
        self.c_dir = Path(".").resolve()
        self.mock_get_proj_config = self.mocker.patch(
            "gdk.common.configuration.get_configuration",
            return_value=config(),
        )

        self.mocker.patch.object(GDKProject, "_get_recipe_file", return_value=Path(".").joinpath("recipe.json").resolve())

        self.case_insensitive_recipe = CaseInsensitiveDict(fake_recipe())

    def test_build_recipe_transformer_instantiate(self):
        pc = ComponentLocalConfiguration({})
        brg = LocalDeployRecipeTransformer(pc)
        assert brg.project_config == pc

    def test_transform_good_recipe(self):
        version = "0.0.1"
        self.mocker.patch.object(LocalDeployRecipeTransformer, "_read_recipe", return_value=self.case_insensitive_recipe)
        brg = LocalDeployRecipeTransformer(ComponentLocalConfiguration({}))
        recipe_out_path = self.tmpdir.joinpath("recipe.json").resolve()
        brg.transform(self.tmpdir, recipe_out_path, version)

        # check generated recipe
        recipe = Path(recipe_out_path)
        recipe_text = recipe.read_text()
        assert "decompressedPath" not in recipe_text

        recipe = CaseInsensitiveRecipeFile().read(recipe_out_path)
        assert recipe.get("ComponentVersion") == version

        artifacts_count = 0
        for i in range(len(recipe["Manifests"])):
            if "Artifacts" in recipe["Manifests"][i]:
                artifacts_count += 1
        assert artifacts_count == 0

    def test_transform_oversized_recipe(self):
        version = "0.0.1"
        self.mocker.patch.object(LocalDeployRecipeTransformer, "_read_recipe", return_value=self.case_insensitive_recipe)
        self.mocker.patch("gdk.common.utils.is_recipe_size_valid", return_value=[False, 17000])
        brg = LocalDeployRecipeTransformer(ComponentLocalConfiguration({}))
        recipe_out_path = self.tmpdir.joinpath("recipe.json").resolve()
        with pytest.raises(Exception) as e:
            brg.transform(self.tmpdir, recipe_out_path, version)

        assert "The build updated recipe file is too big with a size of 17000 bytes." in str(e)


def config():
    return {
        "component": {
            "com.example.PythonLocalPubSub": {
                "author": "<PLACEHOLDER_AUTHOR>",
                "version": "NEXT_PATCH",
                "build": {"build_system": "zip"},
                "publish": {"bucket": "<PLACEHOLDER_BUCKET>", "region": "region"},
            }
        },
        "gdk_version": "1.0.0",
    }


def fake_recipe():
    return {
        "RecipeFormatVersion": "2020-01-25",
        "ComponentName": "com.example.HelloWorld",
        "ComponentVersion": "1.0.0",
        "ComponentDescription": "My first Greengrass component.",
        "ComponentPublisher": "Amazon",
        "ComponentConfiguration": {"DefaultConfiguration": {"Message": "world"}},
        "Manifests": [
            {
                "Platform": {"os": "linux"},
                "Lifecycle": {"Run": "python3 -u {artifacts:decompressedPath}/hello_world.py '{configuration:/Message}'"},
                "Artifacts": [{"URI": "s3://DOC-EXAMPLE-BUCKET/artifacts/com.example.HelloWorld/1.0.0/hello_world.py"}],
            }
        ],
    }
