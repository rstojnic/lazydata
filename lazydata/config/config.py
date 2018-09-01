"""
Class to read and manipulate the project's config file

"""

from pathlib import Path
import yaml

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
            proposed_path = Path(p, "lazydata.yml").resolve()
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
        return Path(path).resolve().relative_to(self.config_path.parent)

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

    def add_file_entry(self, path:str, script_path:str):
        """
        Add a file entry to the config file

        :param path: The path to the data file
        :param script_path: The path to the script that used it
        :return:
        """
        # path relative to the config file
        path_rel = str(self.path_relative_to_config(path))
        script_path_rel = str(self.path_relative_to_config(script_path))

        sha256 = calculate_file_sha256(path)

        self.config["files"].append({
            "path": path_rel,
            "hash": sha256,
            "usage": script_path_rel,
        })

        self.save_config()

    def add_usage(self, entry:dict, script_path:str):
        """
        Make sure the usage string is present in the usage.

        This function modifies the `entry` input parameter and only has side-effects.

        :param entry: The dict with the config file entry that needs to be modified
        :param script_path: The location where the file was used
        :return:
        """

        script_path_rel = str(self.path_relative_to_config(script_path))

        if isinstance(entry["usage"], list):
            usage_set = set(entry["usage"])
            if script_path_rel not in usage_set:
                entry["usage"].append(script_path_rel)
        elif entry["usage"] != script_path_rel:
            entry["usage"] = [entry["usage"], script_path_rel]

        self.save_config()

    def save_config(self):
        """
        Save the config file

        :return:
        """

        with open(str(self.config_path), "w") as fp:
            yaml.dump({"version": self.config["version"]}, fp, default_flow_style=False)
            yaml.dump({"files": self.config["files"]}, fp, default_flow_style=False)
