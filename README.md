# filefreezer: scalable data dependencies

`filefreezer` is a minimalist library for including data dependencies into Python projects. 

Keeping data files in git (e.g. via git-lfs) results in a bloated repository that take ages to pull.  

`filefreezer` is an alternative in which only the data file references are stored in git and data files are synced on-demand when they are needed.

**Benefits**:

- Keeps your git repository clean, with just code, but gives you seamless access any number of linked data files 
- File consistency assured using file hashes and automatic versioning
- Choose your own remote storage backend: AWS S3 or directory over SSH

`file-freezer` is primarily designed for machine learning and data science project. 

## Getting started

Install with pip:

```bash
$ pip install filefreezer
```

### Add to your project

To enable `filefreezer` create a config file in your Python project root:

```bash
$ freezer init
```

This will create `freezer.yml` which will contain the list of all the frozen files. A frozen file is represented by its path, hash and permanent remote storage location (e.g. S3).

### Usage 

**my_script.py**
```python
from filefreezer import freeze

# freeze the file  
import pandas as pd
df = pd.read_csv(freeze("my_big_table.csv"))

```

You can now push your data dependencies to a storage backend (e.g. S3) to share with your team or as backup.

If using `git`, all subsequent `git push` will upload your data to a storage backend of your choice (AWS S3 and directory-over-ssh supported).

Or, to upload manually:

```bash
$ freezer push
```

### How it works

The `filefreezer.yml` config file stores the location of the remote storage backend and tracks all data dependencies. 

Whenever the `import_data()` function is executed this happens:

1. Check if the data file is tracked in the config file
2. If not tracked, start tracking it
3. If tracked, see if the file hash has changed and record a new version if necessary

If the file is not present, `filefreezer` will look for it in the storage backend and download it. 

### Advanced usage

You can achieve multiple data dependency scenarios by putting `import_data()` into different parts of the code:

- Add to `__init__(self)` of a class to add data as a class dependency
- Add to `__init__.py` of a module to add data as a module dependency
- Add to `setup.py` to add data as a Python package dependency

The `import_data()` function also has further options that let you customise the behaviour.

`data_data(file_path, download_link=None)`

- `file_path` - one or more files to download. Glob-style wildcards are accepted, e.g. `"data/*.csv"`. 
- `download_link` - alternative download link for the file, e.g. if it's a public dataset or already available somewhere else. 

## Contributing

The library is licenced under Apache-2 licence. All contributions are welcome!
   