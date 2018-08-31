"""
An abstraction layer for the local cache

"""

from pathlib import Path
import yaml


class LocalStorage:
    """
    An abstraction layer for the local cache

    This class always re-reads all the config files, making sure we have the current latest version.
    """

    def __init__(self):
        """
        Initialise the object and make sure the ~/.lazydata directory exists

        """

        home = Path.home()

        # base path where all the data and metadata is stored
        self.base_path = Path(home, ".lazydata")
        self.config_path = Path(self.base_path, "config.yml")
        self.files_path = Path(self.base_path, "datafiles")

        # make sure base path exists
        if not self.base_path.exists():
            self.base_path.mkdir()

            # write a stub config file
            with open(self.config_path, "w") as fp:
                fp.write("version: 1\n")

        # make sure the datafile store exists
        if not self.files_path.exists():
            self.files_path.mkdir()

        # Load in the config file
        with open(self.config_path) as fp:
            self.config = yaml.load(fp)
