"""
An abstraction layer for the local cache

"""

from pathlib import Path
import yaml
import sqlite3

from peewee import SqliteDatabase, Model, CharField, IntegerField

BASE_PATH = Path(Path.home(), ".lazydata")
METADB_PATH = Path(BASE_PATH, "metadb.sqlite3")

db = SqliteDatabase(str(METADB_PATH))


class LocalStorage:
    """
    An abstraction layer for the local cache

    This class always re-reads all the config files, making sure we have the current latest version.
    """

    def __init__(self):
        """
        Initialise the object and make sure the ~/.lazydata directory exists

        """

        # base path where all the data and metadata is stored
        self.base_path = BASE_PATH
        self.config_path = Path(self.base_path, "config.yml")
        self.files_path = Path(self.base_path, "datafiles")
        self.metadb_path = METADB_PATH

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

        self.metadb = db
        # open a connection to the sqlite database with file metadata
        if not Path(self.metadb_path).exists():
            # Make sure the DB exists
            self.metadb.connect()
            self.metadb.create_tables([DataFile])
        elif self.metadb.is_closed():
            self.metadb.connect()


# MetaDB tables

class BaseModel(Model):
    class Meta:
        database = db


class DataFile(BaseModel):
    """
    The model stores the mtime and inode data of the original file(s).
    This makes it easy to quickly check if the file has changed when calling use()

    :ivar fullpath: The full absolute path to the file when it was used
    :ivar sha256: The SHA256 value
    :ivar mtime: The original mtime value
    :ivar size: The size of the file

    """
    abspath = CharField()
    sha256 = CharField(max_length=70)
    mtime = IntegerField()
    size = IntegerField()



