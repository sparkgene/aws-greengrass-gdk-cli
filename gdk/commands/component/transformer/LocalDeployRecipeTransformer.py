import jsonschema
import logging
from pathlib import Path
from gdk.commands.component.config.ComponentLocalConfiguration import ComponentLocalConfiguration
from gdk.common.CaseInsensitive import CaseInsensitiveRecipeFile, CaseInsensitiveDict
from gdk.common.RecipeValidator import RecipeValidator

import gdk.common.consts as consts
import gdk.common.utils as utils
from gdk.common.exceptions.error_messages import BUILT_RECIPE_SIZE_INVALID, PROJECT_RECIPE_FILE_INVALID, SCHEMA_FILE_INVALID


class LocalDeployRecipeTransformer:
    def __init__(self, _project_config: ComponentLocalConfiguration) -> None:
        self.project_config = _project_config

    def _read_recipe(self, recipe_file_path):
        return CaseInsensitiveRecipeFile().read(recipe_file_path)

    def transform(self, recipe_file_path, deploy_recipe_file, version) -> None:
        """
        Transform the component recipe to be deployed to Greengrass Core.
        """
        logging.debug(f"Read recipe file: {recipe_file_path}")
        component_recipe = self._read_recipe(recipe_file_path)
        component_recipe.update_value("ComponentVersion", version)

        # remove Artifact
        component_recipe_dict = self.remove_s3_artifact(component_recipe)

        recipe_for_local = CaseInsensitiveDict(component_recipe_dict)

        logging.debug("Creating component recipe at '%s'.", deploy_recipe_file)
        CaseInsensitiveRecipeFile().write(deploy_recipe_file, recipe_for_local)

        self.replace_decompressed_path(deploy_recipe_file)

        self.verify_recipe(deploy_recipe_file)

    def remove_s3_artifact(self, component_recipe):
        component_recipe_dict = component_recipe.to_dict()
        for i in range(len(component_recipe_dict["Manifests"])):
            if "Artifacts" in component_recipe_dict["Manifests"][i]:
                keep_artifact = False
                for j in range(len(component_recipe_dict["Manifests"][i]["Artifacts"]) - 1, -1, -1):
                    if "URI" in component_recipe_dict["Manifests"][i]["Artifacts"][j]:
                        if component_recipe_dict["Manifests"][i]["Artifacts"][j]["URI"].startswith("s3:"):
                            del component_recipe_dict["Manifests"][i]["Artifacts"][j]["URI"]
                        else:
                            keep_artifact = True
                    else:
                        keep_artifact = True
                if not keep_artifact:
                    del component_recipe_dict["Manifests"][i]["Artifacts"]

        return component_recipe_dict

    def replace_decompressed_path(self, recipe_path) -> None:
        """
        Replace decompressed path with path in the recipe file for zip build component
        Parameters
        ----------
          recipe_path(str): Path to the recipe file
        """
        recipe = Path(recipe_path)
        new_recipe = Path(recipe_path)

        contents = recipe.read_text().replace("{artifacts:decompressedPath}", "{artifacts:path}")
        new_recipe.write_text(contents)

    def verify_recipe(self, recipe_file_path) -> None:
        """
        Validate the built recipe against the Greengrass recipe schema.
        Parameters
        ----------
          recipe_file_path(str): Path to the recipe file
        """
        logging.info(f"Validating the file size of the built recipe {recipe_file_path}")
        # Validate the size of the created recipe file so we can raise an exception if it is too big
        valid_file_size, input_recipe_file_size = utils.is_recipe_size_valid(recipe_file_path)
        if not valid_file_size:
            logging.error(BUILT_RECIPE_SIZE_INVALID.format(input_recipe_file_size))
            raise Exception(BUILT_RECIPE_SIZE_INVALID.format(input_recipe_file_size))

        logging.info("Validating the built recipe against the Greengrass recipe schema.")
        try:
            parsed_component_recipe = CaseInsensitiveRecipeFile().read(recipe_file_path)
            recipe_schema_path = utils.get_static_file_path(consts.recipe_schema_file)
            validator = RecipeValidator(recipe_schema_path)
            validator.validate_recipe(parsed_component_recipe.to_dict())
        except jsonschema.exceptions.ValidationError as err:
            raise Exception(PROJECT_RECIPE_FILE_INVALID.format(recipe_file_path, err.message))
        except jsonschema.exceptions.SchemaError as err:
            raise Exception(SCHEMA_FILE_INVALID.format(err.message))
