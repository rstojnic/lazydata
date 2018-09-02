
import shutil
import os
from pathlib import Path

def test_local_project():
    """
    Test a simple local project to make sure everything is working

    :return:
    """

    cwd = os.getcwd()

    shutil.rmtree("tests/projects", ignore_errors=True)
    os.mkdir("tests/projects")

    shutil.copytree("tests/templates/sample-project", "tests/projects/local1")

    os.chdir("tests/projects/local1")
    os.system("lazydata init")

    assert Path("lazydata.yml").exists()

    os.chdir(cwd)


