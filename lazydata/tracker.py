from pathlib import Path
from typing import Optional
import traceback

from lazydata.config.config import Config
from lazydata.storage.fetch_file import fetch_file
from lazydata.storage.hash import calculate_file_sha256
from lazydata.storage.local import LocalStorage


def track(path: str, source_url: Optional[str] = None) -> str:
    """
    Track a file using lazydata.

    :param path: a path to the file to be tracked
    :param source_url: a URL to the file to download from
    :return: Returns the path string that is now tracked
    """

    stack = traceback.extract_stack()

    script_location = ""
    if len(stack) >= 2:
        script_location = stack[-2].filename

    # remove the ipython hash because it's going to be changing all the time
    if script_location.startswith("<ipython-input") or script_location.startswith("<stdin"):
        script_location = ""

    path_obj = Path(path)

    # 1) Check if the path exists
    path_exists = path_obj.exists()

    if path_exists and path_obj.is_dir():
        raise NotImplementedError("Tracking directories is not currently supported: `%s`" % path)

    # 2) Check it's present in the config file
    config = Config()
    latest, older = config.get_latest_and_all_file_entries(path)

    local = LocalStorage()

    if path_exists and latest is None:
        # CASE: Start tracking a new file
        print("LAZYDATA: Tracking new file `%s`" % path)
        local.store_file(path)
        config.add_file_entry(path=path, script_path=script_location, source_url=source_url)
    elif path_exists and latest:
        if source_url is not None:
            entry_with_url = config.add_source(entry=latest, source_url=source_url)
            if entry_with_url != latest:
                latest = entry_with_url
                older = [latest] + older

        # CASE: Check for change or stale version
        # check if it has changed
        cached_sha256 = local.get_file_sha256(path)

        # compare with the value in config
        if latest["hash"] in cached_sha256:
            # file is at the latest version!
            # just make sure the usage is recorded
            config.add_usage(latest, script_location)
            return path

        # check if it's one of the stale versions
        matching_old = [e for e in older if e["hash"] in cached_sha256]
        if matching_old:
            print("LAZYDATA: Detected an old version of `%s`, updating to the latest..." % path)
            fetch_file(config=config, local=local, path=path, sha256=latest["hash"])
            # make sure usage is recorded
            config.add_usage(latest, script_location)
        else:
            # It's not a stale version...
            # So now recalculate the SHA256 to see if the file really changed
            path_sha256 = calculate_file_sha256(path)

            if latest["hash"] != path_sha256:
                print("LAZYDATA: Tracked file `%s` changed, recording a new version..." % path)
                local.store_file(path)
                config.add_file_entry(path=path, script_path=script_location, source_url=source_url)
                # make sure usage is recorded
                config.add_usage(latest, script_location)
            else:
                # the file hasn't changed but the metadata was missing locally, so add it...
                local.store_file(path)
                # make sure usage is recorded
                config.add_usage(latest, script_location)

    elif not path_exists and latest:
        # CASE: Remote download
        print("LAZYDATA: Getting latest version of tracked file `%s`..." % path)
        if source_url is not None:
            config.add_source(entry=latest, source_url=source_url)
        fetch_file(config=config, local=local, path=path, sha256=latest["hash"])
        # make sure usage is recorded
        config.add_usage(latest, script_location)
    elif not path_exists and not latest:
        if source_url is not None:
            fetch_file(config=config, local=local, path=path, source_url=source_url)
            config.add_file_entry(path=path, script_path=script_location, source_url=source_url)
        else:
            # CASE: Trying to track non-existing without source_url
            raise RuntimeError("Cannot track file, because file is not found: %s" % path)

    return path
