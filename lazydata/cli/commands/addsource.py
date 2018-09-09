from lazydata.cli.commands.BaseCommand import BaseCommand
from lazydata.config.config import Config


class AddSourceCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Path of the file')
        parser.add_argument('source_url', type=str, help='URL of the source of file')
        return parser

    def handle(self, args):
        config = Config()
        source_url = args.source_url
        path = args.path
        entry, _ = config.get_latest_and_all_file_entries(path=path)
        config.add_source(entry=entry, source_url=source_url)
