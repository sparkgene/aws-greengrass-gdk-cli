from pathlib import Path
from gdk.commands.RemoteCommand import RemoteCommand
from gdk.commands.component.config.ComponentBuildConfiguration import ComponentBuildConfiguration
from gdk.commands.component.config.ComponentLocalConfiguration import ComponentLocalConfiguration


class LocalRemoveCommand(RemoteCommand):
    def __init__(self, command_args) -> None:
        super().__init__(command_args)
        self.project_config = ComponentBuildConfiguration(command_args)
        self.local_deploy_config = ComponentLocalConfiguration(command_args)

    def run(self):
        cmd = []
        cmd.append("sudo")
        cmd.append(str(
            Path(self.local_deploy_config.greengrass_dir).joinpath("bin", "greengrass-cli")))
        cmd.append("deployment")
        cmd.append("create")
        cmd.append("--remove")
        cmd.append(self.project_config.component_name)
        cmd.append("--recipeDir")
        cmd.append(self.local_deploy_config.remote_component_dir + "/recipes")

        self.run_command(cmd)
