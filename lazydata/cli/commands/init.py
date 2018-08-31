from lazydata.cli.commands.BaseCommand import BaseCommand
import os.path
import sys

class InitCommand(BaseCommand):

    def handle(self, args):
        # Check if it doesn't exist already
        if os.path.exists("lazydata.yml"):
            print("ERROR: lazydata.yml already exists in the current directory")
            sys.exit(1)

        # create a new template yml file
        with open("lazydata.yml", "w") as fp:
            fp.write("version: 1\n")

        print("Successfully initialised a new lazydata.yml config file.")

