from lazydata.cli.commands.BaseCommand import BaseCommand
from lazydata.config.config import Config
from lazydata.storage.fetch_file import fetch_file
from lazydata.storage.local import LocalStorage

from pathlib import Path


class PullCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('artefacts', type=str, nargs="*", help='Artefacts to pull')
        return parser

    def handle(self, args):
        config = Config()
        local = LocalStorage()

        if args.artefacts == []:
            # pull everything
            for e in config.config["files"]:
                file_abs_path = config.abs_path(e["path"])
                fetch_file(config=config, local=local, path=str(file_abs_path), sha256=e["hash"])
        else:
            for artefact in args.artefacts:

                # 1) check if the artefact is a file we are tracking
                latest, _ = config.get_latest_and_all_file_entries(artefact)
                if latest is not None:
                    # pull the latest version of this file
                    fetch_file(config=config, local=local, path=artefact, sha256=latest["hash"])
                    continue

                # 2) Check for usage
                used_entries = config.tracked_files_used_in(artefact)
                if used_entries:
                    for e in used_entries:
                        file_abs_path = config.abs_path(e["path"])
                        fetch_file(config=config, local=local, path=str(file_abs_path), sha256=e["hash"])
                    continue

                # 3) check for a directory
                dir_path = None
                try:
                    # might fail on python 3.5...
                    dir_path = Path(artefact).resolve()
                except Exception:
                    pass
                if dir_path and dir_path.exists() and dir_path.is_dir():
                    dir_entries = config.abs_path_matches_prefix(str(dir_path))
                    if dir_entries:
                        for e in dir_entries:
                            file_abs_path = config.abs_path(e["path"])
                            fetch_file(config=config, local=local, path=str(file_abs_path), sha256=e["hash"])

                    continue

