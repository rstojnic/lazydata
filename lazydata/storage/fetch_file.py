from typing import Optional

from lazydata.config.config import Config
from lazydata.storage.local import LocalStorage
from lazydata.storage.remote import RemoteStorage, UrlRemoteStorage


def fetch_file(config: Config, local: LocalStorage, path: str, sha256: Optional[str] = None,
               source_url: Optional[str] = None):
    """
    Top level function that fetches the file, either from local or remote storage
    and copies it to `path`.

    If fetching remotely, it always goes to the local storage first, then copied.

    :param config: project Config instance
    :param local: LocalStorage instance
    :param path: where the file should be copied to
    :param sha256: hash of the file we need
    :param source_url: URL of the source of the file we need
    :return:
    """
    if sha256 is None and source_url is None:
        raise RuntimeError("Fetching file `%s`: neither sha256 nor source_url was specified.")

    if sha256 is not None:
        local_copy_success = local.copy_file_to(sha256, path)
    else:
        local_copy_success = False
    if not local_copy_success:
        if source_url is None:
            source_url = config.source_url(sha256=sha256)
        if source_url is None:
            remote = RemoteStorage.get_from_config(config)
        else:
            remote = UrlRemoteStorage()
        remote.download_to_local(config=config, local=local, sha256=sha256, source_url=source_url, path=path)

        if sha256 is not None:
            local.copy_file_to(sha256, path)
