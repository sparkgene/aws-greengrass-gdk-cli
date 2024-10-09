import logging
import subprocess as sp
from gdk.commands.component.config.ComponentLocalConfiguration import ComponentLocalConfiguration


class RemoteCommand():

    def __init__(self, command_args) -> None:

        self.local_deploy_config = ComponentLocalConfiguration(command_args)

    def _ssh_command(self):
        ssh_cmd = []
        if self.local_deploy_config.host:
            ssh_cmd.append("ssh")
            ssh_cmd.append("-p")
            ssh_cmd.append(self.local_deploy_config.port)
            if self.local_deploy_config.key_file:
                ssh_cmd.append("-i")
                ssh_cmd.append(self.local_deploy_config.key_file)
            ssh_cmd.append(self.local_deploy_config.user + "@" + self.local_deploy_config.host)

        return ssh_cmd

    def run_scp_command(self, source, destination, timeout=60):
        logging.info(f"SCP To: {destination} From: {source}")

        scp_cmd = []
        scp_cmd.append("scp")
        scp_cmd.append("-r")
        scp_cmd.append("-P")
        scp_cmd.append(self.local_deploy_config.port)
        if self.local_deploy_config.key_file:
            scp_cmd.append("-i")
            scp_cmd.append(self.local_deploy_config.key_file)
        scp_cmd.append(source)
        scp_cmd.append(destination)

        logging.debug("run_scp_command: " + " ".join(scp_cmd))
        result = sp.run(scp_cmd, shell=False, capture_output=True, text=True, timeout=timeout)

        if result.returncode != 0:
            logging.error("Command failed")
            logging.error(f"Stdout: {result.stdout}")
            logging.error(f"Stderr: {result.stderr}")
            raise Exception("Command failed: " + " ".join(scp_cmd))

        if result.stdout:
            logging.info(result.stdout)

    def run_command(self, commands, timeout=60):
        remote_cmd = self._ssh_command() + commands

        logging.debug("run_command: " + " ".join(remote_cmd))
        result = sp.run(remote_cmd, shell=False, capture_output=True, text=True, timeout=timeout)

        if result.returncode != 0:
            logging.error("Command failed")
            logging.error(f"Stdout: {result.stdout}")
            logging.error(f"Stderr: {result.stderr}")
            raise Exception("Command failed: " + " ".join(remote_cmd))

        logging.info(result.stdout)

        return result.stdout

    def _check_remote_dir_exist(self):
        logging.info("Check remote dir")
        command = self._ssh_command()
        command.append("ls")
        command.append(self.local_deploy_config.remote_component_dir)
        logging.debug(" ".join(command))
        result = sp.run(command, shell=False, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            if "No such file or directory" in result.stderr:
                logging.info("remote dir don't exists")
                # create remote dir
                self._create_remote_dir()
            else:
                logging.error("Command failed")
                logging.error(f"Stdout: {result.stdout}")
                logging.error(f"Stderr: {result.stderr}")
                raise Exception("Command failed: " + " ".join(command))

    def _create_remote_dir(self):
        logging.info("Creating remote dir")
        command = self._ssh_command()
        command.append("mkdir")
        command.append("-p")
        command.append(self.local_deploy_config.remote_component_dir)
        logging.debug(" ".join(command))
        result = sp.run(command, shell=False, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            logging.error("Command failed")
            logging.error(f"Stdout: {result.stdout}")
            logging.error(f"Stderr: {result.stderr}")
            raise Exception("Command failed: " + " ".join(command))

        if result.stdout:
            logging.info(result.stdout)
        logging.info("Create remote dir successful")
