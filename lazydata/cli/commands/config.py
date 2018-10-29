from lazydata.cli.commands.BaseCommand import BaseCommand
from lazydata.storage.cloudsetup import setup_aws_credentials
from lazydata.storage.localsetup import setup_local_folder


class ConfigCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('backend', type=str, help='The backend to configure, currently only `aws` supported')
        return parser

    def handle(self, args):
        if args.backend == "aws":
            setup_aws_credentials()
        elif args.backend in ['drive','local','folder','mount']:
            setup_local_folder()
        else:
            print("ERROR: Unrecognised backend `%s`. Currently supported: `aws`, `folder`" % args.backend)
