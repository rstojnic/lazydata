from lazydata.cli.commands.BaseCommand import BaseCommand
import sys

from lazydata.config.config import Config
from lazydata.storage.cloudsetup import setup_aws_credentials
from lazydata.storage.remote import RemoteStorage

import lazy_import
botocore = lazy_import.lazy_module("botocore")

class AddRemoteCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='URL of the remote storage backend')
        parser.add_argument('--endpoint-url', type=str, nargs='?', help='The complete URL to use for the constructed client')
        return parser

    def handle(self, args):
        url = args.url
        endpoint_url = args.endpoint_url

        if not url.startswith("s3://"):
            print("ERROR: Only S3 URLs are currently supported. For example: `s3://mybucket` or `s3://mybucket/myfolder`")
            sys.exit(1)

        success = False
        while not success:
            remote = RemoteStorage.get_from_url(url, endpoint_url=endpoint_url)
            try:
                if remote.check_storage_exists():
                    config = Config()
                    config.add_remote(url, endpoint_url=endpoint_url)
                    success = True
                else:
                    success = True
                    print("ERROR: The remote storage location you specified does not exist or is not accessible to you")
            except botocore.exceptions.NoCredentialsError:
                success = False

            if not success:
                print("ERROR: No valid AWS credentials found.")
                config_now = input("Do you want to configure AWS credentials now? [y/n] ")
                if config_now.strip() == "y":
                    setup_aws_credentials()
                    print("Credentials successfully stored. Trying again with these new credentials...")
                else:
                    success = True
                    print("Alright, will not configure credentials now. Re-run this command to try again, "
                          "or configure using the AWS CLI: `aws configure`.")
