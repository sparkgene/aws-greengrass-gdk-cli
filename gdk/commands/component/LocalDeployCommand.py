import logging

import gdk.common.consts as consts
import gdk.commands.component.component as component
import gdk.common.utils as utils
from gdk.commands.RemoteCommand import RemoteCommand
from gdk.commands.component.config.ComponentBuildConfiguration import ComponentBuildConfiguration
from gdk.commands.component.config.ComponentLocalConfiguration import ComponentLocalConfiguration
from gdk.build_system.ComponentBuildSystem import ComponentBuildSystem
import os
from pathlib import Path
import shutil
from gdk.commands.component.transformer.LocalDeployRecipeTransformer import LocalDeployRecipeTransformer


class LocalDeployCommand(RemoteCommand):
    def __init__(self, command_args) -> None:
        super().__init__(command_args)

        self.project_config = ComponentBuildConfiguration(command_args)
        self.local_deploy_config = ComponentLocalConfiguration(command_args)

    def run(self):
        """
        Deploy the component to Greegrass Core
        """
        logging.info("Deploy the component to Greengrass Core.")
        version = self._get_version()
        logging.info("Component version: %s", version)
        try:
            # Build the component before deploying
            component.build({})

            logging.info("Copy the component built artifacts to %s.", self.local_deploy_config.host)
            # Create output dir
            self._create_build_dir(version)
            # Copy artifact for deploy
            self._copy_artifacts(version)
            # Create recipe
            self._create_recipe(version)

            if self.local_deploy_config.host:
                # Check destination dir exists
                self._check_remote_dir_exist()
                # Copy to remote host
                self._copy_to_remote()

            # deploy the component
            self.deploy(version)

        except Exception:
            logging.error(
                "Failed to request deploy component '%s'.",
                self.project_config.component_name,
            )
            raise

    def deploy(self, version):
        """
        Deploy the component to Greegrass Core
        Parameters
        ----------
          version(str): New version for the component
        """
        logging.info("deploy component")

        cmd = []
        cmd.append("sudo")
        cmd.append(str(
            Path(self.local_deploy_config.greengrass_dir).joinpath("bin", "greengrass-cli")))
        cmd.append("deployment")
        cmd.append("create")
        cmd.append("--merge")
        cmd.append(self.local_deploy_config.component_name + "=" + version)
        cmd.append("--recipeDir")
        cmd.append(str(
            Path(self.local_deploy_config.remote_component_dir).joinpath("recipes")))
        build_component_artifacts = list(self.project_config.gg_build_component_artifacts_dir.iterdir())
        if not build_component_artifacts:
            logging.info("No artifacts found in local build dir")
        else:
            cmd.append("--artifactDir")
            cmd.append(str(
                Path(self.local_deploy_config.remote_component_dir).joinpath("artifacts")
            ))

        self.run_command(cmd)

        logging.info("Deploy component request successful")

    def _get_version(self):
        """
        Get the component version. If the version is "NEXT_PATCH", get the version from Greengrass component list
        """
        logging.debug("Get component version")
        if not self.local_deploy_config.component_version == "NEXT_PATCH":
            return self.local_deploy_config.component_version

        cmd = []
        cmd.append("sudo")
        cmd.append(str(
            Path(self.local_deploy_config.greengrass_dir).joinpath("bin", "greengrass-cli")))
        cmd.append("component")
        cmd.append("list")

        result = self.run_command(cmd)
        component_list = result.splitlines()
        for i in range(len(component_list)):
            if self.local_deploy_config.component_name in component_list[i]:
                return self._get_next_version(component_list[i+1].split(":")[1].strip())

        return "0.0.1"

    def _get_next_version(self, version):
        """
        Increment the patch version of the component
        Parameters
        ----------
          version(str): Current version of the component
        Returns
        -------
          str: Next version of the component
        """
        version_parts = version.split(".")
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        return ".".join(version_parts)

    def _copy_to_remote(self):
        """
        Copy artifacts and recipes to remote host
        """
        source_dir = self.local_deploy_config.gg_local_build_dir

        destination = (self.local_deploy_config.user + "@" +
                       self.local_deploy_config.host + ":" +
                       self.local_deploy_config.remote_component_dir + "/")

        # copy artifacts
        source = str(source_dir.joinpath('artifacts'))
        self.run_scp_command(source, destination, timeout=300)

        # copy recipes
        source = str(source_dir.joinpath('recipes'))
        self.run_scp_command(source, destination, timeout=300)

        logging.info("Copy component successful")

    def _create_build_dir(self, version):
        """
        Create build directory for artifacts and recipes. This directory will be copied to remote host
        Parameters
        ----------
          version(str): Component version
        """
        utils.clean_dir(self.local_deploy_config.gg_local_build_dir)

        logging.debug("Creating '%s' directory with artifacts and recipes.", consts.greengrass_local_build_dir)
        # Create build artifacts and recipe directories
        Path.mkdir(self.local_deploy_config.gg_local_build_recipes_dir, parents=True, exist_ok=True)
        artifact_path = self.local_deploy_config.gg_local_build_component_artifacts_dir.parent.joinpath(version)
        Path.mkdir(artifact_path, parents=True, exist_ok=True)

    def _copy_artifacts(self, version):
        """
        Copy artifacts and recipes to local build directory
        """
        target_dir = str(self.local_deploy_config.gg_local_build_component_artifacts_dir)

        build_system = ComponentBuildSystem.get(self.project_config.build_system)
        if self.project_config.build_system == "zip":
            zip_build_dir = utils.get_current_directory().joinpath(*build_system.build_folder).resolve()
            project_dir_name = utils.get_current_directory().name
            source_dir = os.path.join(zip_build_dir, project_dir_name)

            # unpack dir name
            archive_file_name = project_dir_name
            zip_name_setting = self.project_config.build_options.get("zip_name", None)
            if zip_name_setting is not None:
                if len(zip_name_setting):
                    archive_file_name = zip_name_setting
                else:
                    archive_file_name = self.project_config.component_name

            target_dir = self.local_deploy_config.gg_local_build_component_artifacts_dir.parent.joinpath(
                version, archive_file_name).resolve()

            shutil.copytree(
                source_dir,
                target_dir,
                dirs_exist_ok=True
            )
        else:
            if target_dir.endswith("NEXT_PATCH"):
                target_dir = str(self.local_deploy_config.gg_local_build_component_artifacts_dir.parent.joinpath(version))
            logging.info(target_dir)
            source_dir = self.local_deploy_config.gg_build_component_artifacts_dir
            logging.info(source_dir)
            # other build system store artifacts in artifacts dir
            shutil.copytree(
                source_dir,
                target_dir,
                dirs_exist_ok=True
            )
        logging.debug("Copied artifacts to %s", target_dir)

    def _create_recipe(self, version):
        """
        Create recipe file for the component with new version
        Parameters
        ----------
          version(str): Component version
        """
        logging.info("Updating the component recipe %s-%s.",
                     self.project_config.component_name, version)
        recipe_file_path = Path(self.project_config.gg_build_recipes_dir).joinpath(self.project_config.recipe_file.name)
        deploy_recipe_file = self.local_deploy_config.gg_local_build_recipes_dir.joinpath(
            f"{self.project_config.component_name}-{version}.{self.project_config.recipe_file.name.split('.')[-1]}"
        )
        LocalDeployRecipeTransformer(self.local_deploy_config).transform(recipe_file_path, deploy_recipe_file, version)
