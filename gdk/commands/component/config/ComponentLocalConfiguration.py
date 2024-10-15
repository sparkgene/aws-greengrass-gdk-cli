from gdk.common.config.GDKProject import GDKProject
from pathlib import Path
import gdk.common.consts as consts


class ComponentLocalConfiguration(GDKProject):
    def __init__(self, _args) -> None:
        super().__init__()
        self._args = _args
        self.host = self._get_host()
        self.user = self._get_user()
        if self.host and self.user == "":
            raise Exception("SSH user configuration is required for remote command.")
        if self.user and self.host == "":
            raise Exception("SSH host configuration is required for remote command.")

        self.remote_component_dir = self._get_component_dir()
        self.port = self._get_port()
        self.key_file = self._get_key_file()
        self.greengrass_dir = self._get_greengrass_dir()
        self.component_version = self.component_config.get("version", "NEXT_PATCH")

        # These variables are used for local deploy
        self.gg_local_build_dir = Path(self._project_dir).joinpath(consts.greengrass_local_build_dir).resolve()
        self.gg_local_build_artifacts_dir = Path(self.gg_local_build_dir).joinpath("artifacts").resolve()
        self.gg_local_build_recipes_dir = Path(self.gg_local_build_dir).joinpath("recipes").resolve()
        self.gg_local_build_component_artifacts_dir = (
            Path(self.gg_local_build_artifacts_dir).joinpath(self.component_name, self.component_version).resolve()
        )

        self.deploy_recipe_file = self.gg_local_build_recipes_dir.joinpath(
            f"{self.component_name}-{self.component_version}.{self.recipe_file.name.split('.')[-1]}"
        )

    def _get_host(self):
        _host = ""
        _host_args = self._args.get("host")
        if not _host_args:
            _host = self.component_local_config.get("host", "")
        else:
            _host = _host_args
        return _host

    def _get_user(self):
        _user = ""
        _user_args = self._args.get("user")
        if not _user_args:
            _user = self.component_local_config.get("user", "")
        else:
            _user = _user_args
        return _user

    def _get_port(self):
        _port = ""
        _port_args = self._args.get("port")
        if not _port_args:
            _port = self.component_local_config.get("port", "22")
            if not _port:
                _port = "22"
        else:
            _port = _port_args
        return _port

    def _get_key_file(self):
        _key_file = ""
        _key_file_args = self._args.get("key_file")
        if _key_file_args:
            _key_file = _key_file_args
        else:
            _key_file = self.component_local_config.get("key_file", "")
        return _key_file

    def _get_component_dir(self):
        _component_dir = ""
        _component_dir_args = self._args.get("component_dir")
        if _component_dir_args:
            _component_dir = _component_dir_args
        else:
            _component_dir = self.component_local_config.get("component_dir", "~/greengrass-components")
            if not _component_dir:
                _component_dir = "~/greengrass-components"
        return _component_dir

    def _get_greengrass_dir(self):
        _greengrass_dir = ""
        _greengrass_dir_args = self._args.get("greengrass_dir")
        if _greengrass_dir_args:
            _greengrass_dir = _greengrass_dir_args
        else:
            _greengrass_dir = self.component_local_config.get("greengrass_dir", "/greengrass/v2")
            if not _greengrass_dir:
                _greengrass_dir = "/greengrass/v2"
        return _greengrass_dir
