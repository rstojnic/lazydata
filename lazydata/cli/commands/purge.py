from lazydata.cli.commands.BaseCommand import BaseCommand
import os, shutil
from pathlib import Path

class PurgeCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--force', type=str, help='delete all lazydata.yml files on machine as opposed to the current folder; takes several minutes')
        return parser


    def handle(self, args):

        def delete_yml_everywhere(folder):
            for the_file in os.listdir(folder):
                file_path = os.path.join(folder, the_file)
                try:
                    if the_file == "lazydata.yml":
                        print('removing',file_path)
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        delete_yml_everywhere(file_path)
                except Exception as e:
                    print(e)

        def delete_lazydata_configs():
            aws_root = Path(Path.home(), ".aws")
            ld_root = Path(Path.home(), ".lazydata")
            if aws_root.exists():
                shutil.rmtree(aws_root)
            if ld_root.exists():
                shutil.rmtree(ld_root)

        force = args.force
        if force:
            are_you_sure = True if input('Are you sure you want to delete all lazydata config files on your entire machine? y/N ') == 'y' else False
            if are_you_sure:
                root_path = os.path.abspath(os.sep)
                delete_yml_everywhere(root_path)
        else:
            are_you_sure = True if input('Are you sure you want to delete any lazydata config files in the current folder? y/N ') == 'y' else False
            if are_you_sure:
                if os.path.exists("lazydata.yml"):
                    os.remove("lazydata.yml")

        if are_you_sure:
            delete_lazydata_configs()


#C:\Users\jmiller\.lazydata_local

        print("Successfully deleted all lazydata.yml and lazydata config files.")
