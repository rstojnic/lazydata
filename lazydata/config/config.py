"""
Class to read and manipulate the project's config file

"""

from pathlib import Path
from typing import Dict, Optional, List
import yaml
import os

from lazydata.storage.hash import calculate_file_sha256

class Config:

    def __init__(self, init_dir=Path.cwd()):
        """
        Object initialisation

        :param init_dir: The initialisation dir to use for the search for the project file.
                         Usually this is the path to the python file calling lazydata.use()
        """
        # look for the location of the config file by looking at parents directories

        self.config_path = None
        init_parents = [init_dir]
        init_parents.extend([p for p in init_dir.parents])
        for p in init_parents:
            proposed_path = Path(p.resolve(), "lazydata.yml")
            if proposed_path.exists():
                self.config_path = proposed_path

        if self.config_path is None:
            raise RuntimeError("Cannot find the lazydata.yml file in any of the parent directories. "
                               "Did you run `lazydata init`?")

        try:
            with open(str(self.config_path)) as fp:
                self.config = yaml.safe_load(fp)
        except Exception as e:
            raise RuntimeError("Error parsing `lazydata.yml`. Please revert to the last working version.\n%s" % str(e))

        if "files" not in self.config:
            self.config["files"] = []

    def path_relative_to_config(self, path:str) -> Path:
        """
        Return the Path relative to the config file

        :param path: file path
        :return: Path object relative to the config file
        """

        return Path(os.path.abspath(path)).relative_to(self.config_path.parent)

    def abs_path(self, path_relative_to_config:str) -> Path:
        """
        Return the absolute path of a file that is defined as being relative to config

        :param path_relative_to_config:
        :return:
        """
        return Path(self.config_path.parent.resolve(), path_relative_to_config)

    def get_latest_and_all_file_entries(self, path:str):
        """
        Get the latest and all other versions of the file entry for a path

        :param path:
        :return: tuple: None, None if nothing found, otherwise <latest>,<older>
        """

        # path relative to the config file
        path_rel = str(self.path_relative_to_config(path))

        all_entries = [f for f in self.config["files"] if f["path"] == path_rel]

        if len(all_entries) == 0:
            return None, None
        else:
            return all_entries[-1], all_entries[:-1]

    def add_file_entry(self, path:str, script_path:str, source_url: Optional[str] = None) -> Dict[str, str]:
        """
        Add a file entry to the config file

        :param path: The path to the data file
        :param script_path: The path to the script that used it
        :param source_url: The source to download file from
        :return:
        """
        # path relative to the config file
        path_rel = str(self.path_relative_to_config(path))
        script_path_rel = str(self.path_relative_to_config(script_path))

        sha256 = calculate_file_sha256(path)

        result = {
            "path": path_rel,
            "hash": sha256,
            "usage": script_path_rel,
        }
        if source_url is not None:
            result['source_url'] = source_url
        self.config["files"].append(result)

        self.save_config()

        return result

    def add_usage(self, entry:dict, script_path:str):
        """
        Make sure the usage string is present in the usage.

        This function modifies the `entry` input parameter and only has side-effects.

        :param entry: The dict with the config file entry that needs to be modified
        :param script_path: The location where the file was used
        :return:
        """

        script_path_rel = str(self.path_relative_to_config(script_path))

        config_changed = False

        if isinstance(entry["usage"], list):
            usage_set = set(entry["usage"])
            if script_path_rel not in usage_set:
                entry["usage"].append(script_path_rel)
                config_changed = True
        elif entry["usage"] != script_path_rel:
            entry["usage"] = [entry["usage"], script_path_rel]
            config_changed = True

        if config_changed:
            self.save_config()

    def add_source(self, entry: dict, source_url: str) -> Dict[str, str]:
        """
        Make sure the source string is present.

        This function modifies the `entry` input parameter and only has side-effects.

        :param entry: The dict with the config file entry that needs to be modified
        :param source_url: The str with url to the source of file
        :return:
        """

        config_changed = False
        if "source_url" in entry:
            if entry["source_url"] != source_url:
                entry = self.add_file_entry(path=entry["path"], script_path=entry["usage"])
                config_changed = True
        else:
            entry["source_url"] = source_url
            config_changed = True
        if config_changed:
            self.save_config()
        return entry

    def add_remote(self, remote_url:str, endpoint_url:str):
        """
        Add a remote to the config file

        :param remote_url:
        :return:
        """

        if "remote" in self.config:
            print("ERROR: Remote storage backend in `lazydata.yml` already exists. Aborting...")
        else:
            # Setting the remote config automatically sets the endpoint parameter, even if it is None
            self.config["remote"] = remote_url
            self.config["endpoint"] = endpoint_url
            self.save_config()

    def check_file_tracked(self, path:str):
        """
        Checks if the file is tracked in the config file

        :return:
        """
        latest, _ = self.get_latest_and_all_file_entries(path)

        return latest is not None

    def tracked_files_used_in(self, script_path:str):
        """
        See if there are any tracked files used by this script

        :param script_path:
        :return:
        """
        script_path_rel = str(self.path_relative_to_config(script_path))

        entries = [e for e in self.config["files"] if usage_filter(e["usage"], script_path_rel)]

        return entries

    def abs_path_matches_prefix(self, abspath_prefix:str):
        """
        Select those tracked files that match an absolute path prefix

        :param abspath_prefix:
        :return:
        """
        entries = [e for e in self.config["files"] if str(self.abs_path(e["path"])).startswith(abspath_prefix)]

        return entries

    def source_url(self, sha256: str) -> Optional[str]:
        try:
            result = [e["source_url"] for e in self.config["files"] if e["hash"] == sha256][-1]
        except IndexError:
            result = None
        return result

    def path(self, sha256: Optional[str] = None, source_url: Optional[str] = None) -> Optional[str]:
        if sha256 is not None:
            try:
                result = [e["path"] for e in self.config["files"] if e["hash"] == sha256][-1]
            except IndexError:
                result = None
        elif source_url is not None:
            try:
                result = [e["path"] for e in self.config["files"] if e["source_url"] == source_url][-1]
            except IndexError:
                result = None
        else:
            raise ValueError("Neither sha256 nor source_url was specified")
        return result

    def save_config(self):
        """
        Save the config file

        :return:
        """

        with open(str(self.config_path), "w") as fp:
            yaml.dump({"version": self.config["version"]}, fp, default_flow_style=False)
            if "remote" in self.config:
                yaml.dump({"remote": self.config["remote"]}, fp, default_flow_style=False)
            if "endpoint" in self.config:
                yaml.dump({"endpoint": self.config["endpoint"]}, fp, default_flow_style=False)
            if "files" in self.config:
                yaml.dump({"files": self.config["files"]}, fp, default_flow_style=False)


def usage_filter(usage, script_path):
    if isinstance(usage, list):
        return script_path in usage
    else:
        return script_path == usage