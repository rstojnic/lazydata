"""
Common functions to interactively set up credentials for cloud access
"""

from pathlib import Path

def setup_local_folder():

    local_folder = input("Full path of local folder: ")

    if local_folder.strip() == "":
        local_folder = Path.home()

    folder_root = Path(Path.home(), ".lazydata_local")
    aws_config = Path(aws_root, "config")

    if not folder_root.exists():
        folder_root.mkdir()

    print("Folder %s accepted." % str(local_folder))
