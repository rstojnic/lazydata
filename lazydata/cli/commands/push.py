from lazydata.cli.commands.BaseCommand import BaseCommand
from lazydata.config.config import Config
from lazydata.storage.local import LocalStorage
from lazydata.storage.remote import RemoteStorage


class PushCommand(BaseCommand):

    def handle(self, args):
        config = Config()
        if "remote" in config.config:
            remote = RemoteStorage.get_from_config(config)
            local = LocalStorage()
            remote.upload(local,config)
        else:
            print("ERROR: Remote not specified for this lazydata project. Use `lazydata add-remote` to add it.")
