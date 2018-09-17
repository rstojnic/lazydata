from lazydata.cli.commands.BaseCommand import BaseCommand
import os, shutil
import sys

class PurgeCommand(BaseCommand):

    def handle(self, args):

        def delete_yml_everywhere(folder):

            for the_file in os.listdir(folder):
                file_path = os.path.join(folder, the_file)
                try:
                    if the_file == "lazydata.yml":
                        print('remove',file_path)
                        #os.remove(file_path)
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

        are_you_sure = True if input('Are you sure you want to delete all lazydata config files on your entire machine? y/N ') == 'y' else False

        # Check if it doesn't exist already
        if os.path.exists("lazydata.yml") and are_you_sure:
            root_path = os.path.abspath(os.sep)
            delete_yml_everywhere(root_path)
            delete_lazydata_configs()


        print("Successfully deleted all lazydata.yml and lazydata config files.")
