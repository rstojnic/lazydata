from pathlib import Path
import traceback

from lazydata.config.config import Config
from lazydata.storage.fetch_file import fetch_file
from lazydata.storage.hash import calculate_file_sha256
from lazydata.storage.local import LocalStorage
from lazydata.storage.remote import RemoteStorage


def track(path:str) -> str:
    """
    Track a file using lazydata.

    :param path: a path to the file to be tracked
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

    if path_exists and latest is None:
        # CASE: Start tracking a new file
        print("LAZYDATA: Tracking new file `%s`" % path)
        local = LocalStorage()
        local.store_file(path)
        config.add_file_entry(path, script_location)
    elif path_exists and latest:
        # CASE: Check for change or stale version
        # check if it has changed
        local = LocalStorage()
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
            fetch_file(config, local, latest["hash"], path)
            # make sure usage is recorded
            config.add_usage(latest, script_location)
        else:
            # It's not a stale version...
            # So now recalculate the SHA256 to see if the file really changed
            path_sha256 = calculate_file_sha256(path)

            if latest["hash"] != path_sha256:
                print("LAZYDATA: Tracked file `%s` changed, recording a new version..." % path)
                local.store_file(path)
                config.add_file_entry(path, script_location)
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
        local = LocalStorage()
        fetch_file(config, local, latest["hash"], path)
        # make sure usage is recorded
        config.add_usage(latest, script_location)
    elif not path_exists and not latest:
        # CASE: Trying to track non-existing
        raise RuntimeError("Cannot track file, because file is not found: %s" % path)

    return path
