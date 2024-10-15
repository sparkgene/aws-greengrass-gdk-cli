def init(d_args):
    from gdk.commands.component.InitCommand import InitCommand

    InitCommand(d_args).run()


def build(d_args):
    from gdk.commands.component.BuildCommand import BuildCommand

    BuildCommand(d_args).run()


def publish(d_args):
    from gdk.commands.component.PublishCommand import PublishCommand

    PublishCommand(d_args).run()


def list(d_args):
    from gdk.commands.component.ListCommand import ListCommand

    ListCommand(d_args).run()


def local_deploy(d_args):
    from gdk.commands.component.LocalDeployCommand import LocalDeployCommand

    LocalDeployCommand(d_args).run()


def local_list(d_args):
    from gdk.commands.component.LocalListCommand import LocalListCommand

    LocalListCommand(d_args).run()


def local_remove(d_args):
    from gdk.commands.component.LocalRemoveCommand import LocalRemoveCommand

    LocalRemoveCommand(d_args).run()
