from lazydata.cli.commands.BaseCommand import BaseCommand
import sys

from lazydata.config.config import Config
from lazydata.storage.remote import RemoteStorage


class AddRemoteCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='URL of the remote storage backend')
        return parser

    def handle(self, args):
        url = args.url

        if not url.startswith("s3://"):
            print("ERROR: Only S3 URLs are currently supported. For example: `s3://mybucket` or `s3://mybucket/myfolder`")
            sys.exit(1)

        remote = RemoteStorage.get_from_url(url)
        if remote.check_storage_exists():
            config = Config()
            config.add_remote(url)
        else:
            print("ERROR: The remote storage location you specified does not exist or is not accessible to you")
