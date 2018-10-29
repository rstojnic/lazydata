from lazydata.cli.commands.BaseCommand import BaseCommand
import sys
from lazydata import track

class TrackCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('one_file', type=str, help='the specified file, full or relative path')
        return parser

    def handle(self, args):
        if args.one_file:
            track(args.one_file)
        else:
            print('Error: Please specify a valid file path')
