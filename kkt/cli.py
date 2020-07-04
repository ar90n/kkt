import click

from .commands import init, install, push, status, download

cmd = click.Group()
cmd = click.version_option()(cmd)

cmd.add_command(init)
cmd.add_command(push)
cmd.add_command(status)
cmd.add_command(install)
cmd.add_command(download)


def main() -> None:
    cmd()
