import click

from .commands import init, push, status

cmd = click.Group()
cmd = click.version_option()(cmd)

cmd.add_command(init)
cmd.add_command(push)
cmd.add_command(status)


def main():
    cmd()
