"""
An abstraction layer for the local cache

"""

from pathlib import Path
import yaml
import sqlite3
import os

from peewee import SqliteDatabase, Model, CharField, IntegerField

from lazydata.storage.hash import calculate_file_sha256

BASE_PATH = Path(Path.home(), ".lazydata").resolve()
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
        self.data_path = Path(self.base_path, "data")
        self.metadb_path = METADB_PATH

        # make sure base path exists
        if not self.base_path.exists():
            self.base_path.mkdir()

            # write a stub config file
            with open(self.config_path, "w") as fp:
                fp.write("version: 1\n")

        # make sure the datafile store exists
        if not self.data_path.exists():
            self.data_path.mkdir()

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

    def hash_to_file(self, sha256):
        """Get the data storage path to a file with this hash

        :param sha256:
        :return: Path to the stored file
        """

        return Path(self.data_path, sha256[:2], sha256[2:])


    def store_file(self, path):
        """
        Store a file in the local backend.

        :ivar path: The path to the file to store
        :return:
        """

        stat = os.stat(path)
        abspath = Path(path).resolve()

        sha256 = calculate_file_sha256(path)

        # see if we stored this file already
        datapath = self.hash_to_file(sha256)
        if not datapath.exists():
            # Hard-link the file to the path
            datapath.parent.mkdir(parents=True, exist_ok=True)
            os.link(abspath, str(datapath))

        # Store in the metadata DB if doesn't exist already
        existing_entries = DataFile.select().where(
            (
                (DataFile.abspath == abspath) &
                (DataFile.sha256 == sha256) &
                (DataFile.mtime == stat.st_mtime) &
                (DataFile.size == stat.st_size)
            )
        )

        if existing_entries.count() == 0:
            DataFile.create(abspath=abspath, sha256=sha256, mtime=stat.st_mtime, size=stat.st_size)


# MetaDB tables

class BaseModel(Model):
    class Meta:
        database = db


class DataFile(BaseModel):
    """
    The model stores the mtime and size of the original file(s).
    This makes it easy to quickly check if the file has changed when calling use()

    :ivar fullpath: The full absolute path to the file when it was used
    :ivar sha256: The SHA256 value
    :ivar mtime: The original mtime value
    :ivar size: The size of the file

    """
    abspath = CharField(index=True)
    sha256 = CharField(max_length=70, index=True)
    mtime = IntegerField(index=True)
    size = IntegerField(index=True)



