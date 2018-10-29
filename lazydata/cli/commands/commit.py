"""
commit, tracks all existing files at once.
"""
from lazydata.cli.commands.BaseCommand import BaseCommand
from lazydata import tracker as lazy_tracker
from lazydata.config.config import Config

class CommitCommand(BaseCommand):

    def handle(self, args):
        config = Config()
        paths = [e["path"] for e in config.config["files"]]
        for path in paths:
            lazy_tracker.track(path)
