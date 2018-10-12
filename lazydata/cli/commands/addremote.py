from lazydata.cli.commands.BaseCommand import BaseCommand
import sys

from lazydata.config.config import Config
from lazydata.storage.cloudsetup import setup_aws_credentials
from lazydata.storage.remote import RemoteStorage

import lazy_import
botocore_exceptions = lazy_import.lazy_module("botocore.exceptions")
gcp_auth_exceptions = lazy_import.lazy_module('google.auth.exceptions')

class AddRemoteCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='URL of the remote storage backend')
        parser.add_argument('--endpoint-url', type=str, nargs='?', help='The complete URL to use for the constructed client')
        return parser

    def handle(self, args):
        url = args.url
        endpoint_url = args.endpoint_url

        if url.startswith('s3://') or url.startswith('gs://'):
            success = False
            while not success:
                try:
                    remote = RemoteStorage.get_from_url(url, endpoint_url=endpoint_url)
                    if remote.check_storage_exists():
                        config = Config()
                        config.add_remote(url, endpoint_url=endpoint_url)
                        success = True
                    else:
                        success = True
                        print("ERROR: The remote storage location you specified does not exist or is not accessible to you")
                except botocore_exceptions.NoCredentialsError:
                    success = False
                except AttributeError as err:
                    success = True
                    print("ERROR: Couldn't find credentials for Google Cloud Storage. Please set "
                          "GOOGLE_APPLICATION_CREDENTIALS or explicitly create credentials and re-run the application. "
                          "For more information, please see "
                          "https://developers.google.com/accounts/docs/application-default-credentials.")

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
        else:
            print('ERROR: Only S3 or Google Cloud Storage urls are currently suppored. For example: '
                  '`s3://mybucket`, gs://mybucket/myfolder, s3://mybucket/myfolder')
            sys.exit(1)
