"""
An abstraction layer for the local cache

"""

from pathlib import Path, PurePosixPath
import yaml
import os
import stat

from peewee import SqliteDatabase, Model, CharField, IntegerField

from lazydata.storage.hash import calculate_file_sha256
import shutil

BASE_PATH = Path(Path.home().resolve(), ".lazydata")
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
            with open(str(self.config_path), "w") as fp:
                fp.write("version: 1\n")

        # make sure the datafile store exists
        if not self.data_path.exists():
            self.data_path.mkdir()

        # Load in the config file
        with open(str(self.config_path)) as fp:
            self.config = yaml.load(fp)

        self.metadb = db
        # open a connection to the sqlite database with file metadata
        if not Path(self.metadb_path).exists():
            # Make sure the DB exists
            self.metadb.connect()
            self.metadb.create_tables([DataFile])
        elif self.metadb.is_closed():
            self.metadb.connect()

    def hash_to_file(self, sha256:str) -> Path:
        """Get the data storage path to a file with this hash

        :param sha256:
        :return: Path to the stored file
        """

        return Path(self.data_path, sha256[:2], sha256[2:])

    def hash_to_remote_path(self, sha256:str) -> PurePosixPath:
        """Get the remote path (in posix format)

        :param sha256:
        :return: Path to the stored file
        """

        return PurePosixPath("data", sha256[:2], sha256[2:])

    def store_file(self, path:str):
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

        # copy over the the cache,
        # TODO: option to hardlink
        datapath.parent.mkdir(parents=True, exist_ok=True)
        if not datapath.exists():
            shutil.copyfile(str(abspath), str(datapath))

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

    def get_file_sha256(self, path:str) -> list:
        """
        Checks if the file has a stored sha256 value

        :param path:
        :return: A list of sha256 strings
        """

        stat = os.stat(path)
        abspath = Path(path).resolve()

        existing_entries = DataFile.select().where(
            (
                (DataFile.abspath == abspath) &
                (DataFile.mtime == stat.st_mtime) &
                (DataFile.size == stat.st_size)
            )
        )

        sha256 = [e.sha256 for e in existing_entries]
        return sha256

    def copy_file_to(self, sha256:str, path:str) -> bool:
        """
        Copy the file from local cache to user's local copy.

        If the file is not available locally it will return False, otherwise return True if successful

        :param config: The project config used to get the remote if the files needs downloading
        :param sha256: The sha256 of the file we need
        :param path: The path where it should be copied
        :return: Returns
        """

        cached_path = self.hash_to_file(sha256)
        path_obj = Path(path)

        if cached_path.exists():
            if path_obj.exists():
                # delete the old file as we'll need to overwrite it
                path_obj.unlink()
            else:
                # we might need to make some directories to pull the file...
                path_obj.parent.mkdir(parents=True, exist_ok=True)

            shutil.copyfile(str(cached_path), str(path))
            return True
        else:
            return False


def is_same_hard_link(filename:str, other:str):
    s1 = os.stat(filename)
    s2 = os.stat(other)
    return (s1[stat.ST_INO], s1[stat.ST_DEV]) == \
        (s2[stat.ST_INO], s2[stat.ST_DEV])

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



