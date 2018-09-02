from lazydata.config.config import Config
from lazydata.storage.local import LocalStorage
from lazydata.storage.remote import RemoteStorage


def fetch_file(config:Config, local:LocalStorage, sha256:str, path:str):
    """
    Top level function that fetches the file, either from local or remote storage
    and copies it to `path`.

    If fetching remotely, it always goes to the local storage first, then copied.

    :param config: project Config instance
    :param local: LocalStorage instance
    :param sha256: hash of the file we need
    :param path: where the file should be copied to
    :return:
    """
    local_copy_success = local.copy_file_to(sha256, path)
    if not local_copy_success:
        remote = RemoteStorage.get_from_config(config)
        remote.download_to_local(config, local, sha256)

        local.copy_file_to(sha256, path)