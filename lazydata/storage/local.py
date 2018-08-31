"""
An abstraction layer for the local cache

"""

from pathlib import Path
import yaml


class LocalStorage:
    """
    An abstraction layer for the local cache

    This class is a singleton - it always returns the same instance of the local storage backend
    """

    __instance = None

    def __new__(cls):
        if LocalStorage.__instance is None:
            LocalStorage.__instance = object.__new__(cls)

        return LocalStorage.__instance

    def __init__(self):
        """
        Initialise the object and make sure the ~/.lazydata directory exists

        """

        home = Path.home()

        # base path where all the data and metadata is stored
        self.base_path = Path(home, ".lazydata")
        self.config_path = Path(self.base_path, "config.yml")

        # make sure base path exists
        if not self.base_path.exists():
            self.base_path.mkdir()

            # write a stub config file
            with open(self.config_path, "w") as fp:
                fp.write("version: 1\n")

        with open(self.config_path) as fp:
            self.config = yaml.load(fp)
