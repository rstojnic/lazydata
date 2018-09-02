from lazydata.cli.commands.BaseCommand import BaseCommand
from lazydata.storage.cloudsetup import setup_aws_credentials


class ConfigCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('backend', type=str, help='The backend to configure, currently only `aws` supported')
        return parser

    def handle(self, args):
        if args.backend == "aws":
            setup_aws_credentials()
        else:
            print("ERROR: Unrecognised backend `%s`. Currently supported: `aws`" % args.backend)