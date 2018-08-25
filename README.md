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
$ freezer init s3://mybucket/freezer
```

This will set your permanent storage location to S3 (but you can also use directory over SSH).

And, it will create `freezer.yml` which contains a list of all the frozen files. A frozen file is represented by its path and hash.

### Usage 

Lets say you want to use a local data file `my_big_table.csv` in your Python project. To add it to the file freezer, call `freeze("<path_to_file>")`:

**my_script.py**
```python
from filefreezer import freeze

# freeze the file when loading  
import pandas as pd
df = pd.read_csv(freeze("my_big_table.csv"))

print("Data shape:" + df.shape)

```

This will add `my_big_table.yml` to your local freezer file:

**freezer.yml**
```yaml
storage: s3://mybucket/freezer
files:
  - path: my_big_table.csv
    hash: 2C94697198875B6E...
    usage: my_script.py

```

Next, commit both `my_script.py` and `freezer.yml` into git and push to remove. To upload the data files use:

```bash
$ freezer push
```

This will upload the cached version of files from your local machine to the remote storage (in our case S3). 

When your collaborator pulls the latest version of the git repository, they will receive the script and the `freezer.yml` file, but no data files. 

Data files will be downloaded when your collaborator when `my_script.py` is run:

```bash
$ python my_script.py
## FREEZER: Downloading my_big_table.csv ...
## Data shape: (10000,100)
``` 

You can also download specific files by name, or python file where they are used:

```bash
# download just this file
$ freezer pull my_big_table.csv

# download everything frozen in this script
$ freezer pull my_script.py

# download everything
$ freezer pull .
```

### Advanced usage

You can achieve multiple data dependency scenarios by putting `freeze()` into different parts of the code:

- Add to outputs of your data pipeline to also freeze the outputs
- Add to `__init__(self)` of a class to add data as a class dependency
- Add to `__init__.py` of a module to add data as a module dependency
- Add to `setup.py` to add data as a Python package dependency

## Contributing

The library is licenced under Apache-2 licence. All contributions are welcome!
   