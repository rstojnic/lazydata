import argparse

from lazydata.cli.commands.init import InitCommand
from lazydata.cli.commands.pull import PullCommand
from lazydata.cli.commands.push import PushCommand
from lazydata.cli.commands.addremote import AddRemoteCommand
from lazydata.cli.commands.config import ConfigCommand
from lazydata.cli.commands.purge import PurgeCommand
from lazydata.cli.commands.track import TrackCommand

def cli():
    """
    The CLI entry point

    :return:
    """

    parser = argparse.ArgumentParser(prog='lazydata')

    # register all the subcommands here
    subcommands = [
        {
            "command": "init",
            "handler": InitCommand(),
            "help": "Initialise a new lazydata config file"
        },
        {
            "command": "push",
            "handler": PushCommand(),
            "help": "Push files to remote storage"
        },
        {
            "command": "pull",
            "handler": PullCommand(),
            "help": "Pull files from remote storage"
        },
        {
            "command": "add-remote",
            "handler": AddRemoteCommand(),
            "help": "Add a remote storage backend"
        },
        {
            "command": "config",
            "handler": ConfigCommand(),
            "help": "Configure access credentials for remote storage backends"
        },
        {
            "command": "purge",
            "handler": PurgeCommand(),
            "help": "Deletes all config files related to lazydata globally"
        },
        {
            "command": "track",
            "handler": TrackCommand(),
            "help": "Tracks a specified file on command"
        }
        # {
        #     "command": "remove-remote",
        #     "handler": RemoveRemoteCommand(),
        #     "help": "Remove a remote storage backend"
        # },
        # {
        #     "command": "ls",
        #     "handler": LsCommand(),
        #     "help": "List tracked files and their current status"
        # },
        #{
        #     "command": "commit",
        #     "handler": CommitCommand(),
        #     "help": "commit, tracks all existing files at once."
        #},

    ]
    subparsers = parser.add_subparsers(title="subcommands")

    # register all the subparsers
    for subcommand in subcommands:
        obj = subcommand["handler"]
        subparser = subparsers.add_parser(subcommand["command"], help=subcommand["help"])
        subparser = obj.add_arguments(subparser)
        subparser.set_defaults(func=obj.handle)
        obj.parser = parser

    # parse the call the appropriate function
    args, _ = parser.parse_known_args()

    if "func" in args:
        args.func(args)
    else:
        parser.print_help()
