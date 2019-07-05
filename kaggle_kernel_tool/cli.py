import click

from .init import init
from .push import push

cmd = click.Group()
cmd = click.version_option(cmd)

cmd.add_command(init)
cmd.add_command(push)


def main():
    cmd()
