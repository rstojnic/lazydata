# Lazy-data: lazy data dependencies

`lazy-data` is a minimalist library for including data dependencies into Python projects. 

It is designed for machine learning and data science project. It helps you keep everything together without bloating your local copy with files you don't need. 

**Key features:**

- Data is lazy-downloaded when needed
- Choose your own storage backend
- One-line usage for you, zero-config for your team

File consistency between machines is assured by using file hashes. 

## Getting started

Install with pip:

```bash
$ pip install lazy-data
```

### Add to your project

To enable `lazy-data` create a config file in your Python project root:

```bash
$ lazy-data init
```

### Usage 

**my_script.py**
```python
from lazy_data import import_data

# lazy-data will ensure this file is downloaded
import_data("my_big_table.csv")

# work as usual ... 
import pandas as pd
df = pd.read_csv("my_big_table.csv")

```

You can now push your data dependencies to a storage backend to share with your team or as backup.

If using `git`, all subsequent `git push` will upload your data to a storage backend of your choice (AWS S3 and directory-over-ssh supported).

Or, to upload manually:

```bash
$ lazy-data push
```

### How it works

The `lazy-data.yml` config file stores the location of the remote storage backend and tracks all data dependencies. 

Whenever the `import_data()` function is executed this happens:

1. Check if the data file is tracked in the config file
2. If not tracked, start tracking it
3. If tracked, see if the file hash has changed and record a new version if necessary

If the file is not present, `lazy-data` will look for it in the storage backend and download it. 

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
   