from lazydata.cli.commands.BaseCommand import BaseCommand
from lazydata.storage.cloudsetup import setup_credentials


class ConfigCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('backend', type=str, help='The backend to configure, currently only `aws` and `azure` are supported')
        return parser

    def handle(self, args):
        setup_credentials(args.backend)
