import click

from .commands import init, push

cmd = click.Group()
cmd = click.version_option()(cmd)

cmd.add_command(init)
cmd.add_command(push)


def main():
    cmd()
