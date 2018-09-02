
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

    # track file for the first time

    out = os.popen("python sample_script.py").read()

    assert "Tracking new file" in out
    assert "some_data_file.txt" in out

    with open("lazydata.yml", "r") as f:
        config = f.read()

    assert "path: data/some_data_file.txt" in config
    assert "hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" in config
    assert "usage: sample_script.py" in config

    ld = Path(Path.home(), ".lazydata")
    assert ld.exists()
    assert Path(ld, "data", "e3", "b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" ).exists()

    # re-run the the same file, this shouldn't do anything
    out = os.popen("python sample_script.py").read()

    assert "Tracking new file" not in out
    assert "some_data_file.txt" not in out

    # deleting the file should reinstate it
    shutil.rmtree("data/")
    out = os.popen("python sample_script.py").read()

    assert "Getting latest version" in out
    assert "some_data_file.txt" in out

    # teardown

    os.chdir(cwd)


