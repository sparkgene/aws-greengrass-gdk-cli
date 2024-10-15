from pathlib import Path
from gdk.commands.RemoteCommand import RemoteCommand


class LocalListCommand(RemoteCommand):
    def __init__(self, command_args) -> None:
        super().__init__(command_args)

    def run(self):
        """
        Run the greengrass-cli command to list components
        """
        cmd = []
        cmd.append("sudo")
        cmd.append(str(
            Path(self.local_deploy_config.greengrass_dir).joinpath("bin", "greengrass-cli")))
        cmd.append("component")
        cmd.append("list")

        self.run_command(cmd)
