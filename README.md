# datafreezer: scalable data dependencies

`datafreezer` is a minimalist library for including data dependencies into Python projects. 

**Problem**: Keeping data files in git (e.g. via git-lfs) results in a bloated repository that takes ages to pull.  

**Solution**: `datafreezer` only stores references to data files in git, and syncs data files on-demand when they are needed.

**Benefits**:

- Keeps your git repository clean with just code, while enabling seamless access to any number of linked data files 
- File consistency assured using file hashes and automatic versioning
- Choose your own remote storage backend: AWS S3 or directory over SSH

`file-freezer` is primarily designed for machine learning and data science project. 

## Installation

Install with pip:

```bash
$ pip install datafreezer
```
## Getting started 

In this section we'll show how to use `datafreezer` on an example project.

### Add to your project

To enable `datafreezer` run in your git root:

```bash
$ freezer init 
```

This will initialise`freezer.yml` which will hold the list of all the frozen files.


### Freezing a file

To add a data file to the freezer, use `freezer("<path_to_file>")` in your code:

**my_script.py**
```python
from datafreezer import freezer

# freeze the file when loading  
import pandas as pd
df = pd.read_csv(freezer("data/my_big_table.csv"))

print("Data shape:" + df.shape)

```

Running the script will freeze the file:

```bash
$ python my_script.py
## FREEZER: Freezing new file data/my_big_table.csv
## Data shape: (10000,100)
```

The file has now been backed-up in your local freezer cache in `~/.freezer-cache` and added to **freezer.yml**:
```yaml
files:
  - path: data/my_big_table.csv
    hash: 2C94697198875B6E...
    usage: my_script.py

```

If you modify the data file and re-run the script, this will add another entry to the yml file with the updated hash of the data file, i.e. data files are automatically versioned. If you don't want to keep past versions, simply remove them from the yml file.   

And you are done! This data file is now linked to your local repository.

### Sharing your frozen files

To share your frozen files add a remote storage backend where they can be uploaded. To use S3 as a storage backend run:

```bash
$ freezer add-remote s3://mybucket/freezer
```

This will configure the S3 backend and also add it to `freezer.yml` for future reference. Alternatively, you can also use `ssh://username@myserver/path` as a storage backend.

You can now git commit and push your  `my_script.py` and `freezer.yml` files as you normally would. 
 
To upload the frozen data files to S3 use:

```bash
$ freezer push
```

When your collaborator pulls the latest version of the git repository, they will get the script and the `freezer.yml` file as usual.  

Data files will be downloaded when your collaborator runs `my_script.py` and the `freezer("my_big_table.csv")` is executed:

```bash
$ python my_script.py
## FREEZER: Downloading frozen file my_big_table.csv ...
## Data shape: (10000,100)
``` 

To get the data files without running the code, you can also use the command line utility:

```bash
# download just this file
$ freezer pull my_big_table.csv

# download everything frozen in this script
$ freezer pull my_script.py

# download everything frozen in this git commit
$ freezer pull 653ca451

# download everything in HEAD
$ freezer pull .
```

Because `freezer.yml` is tracked by git you can safely make and switch git branches. 

### Advanced usage

You can achieve multiple data dependency scenarios by putting `freezer()` into different parts of the code:

- Add to outputs of your data pipeline to freeze the outputs
- Add to `__init__(self)` to freeze files when the object is created
- Add to `__init__.py` to freeze files when the python module is used
- Add to `setup.py` to freeze files when a Python package is installed

### Coming soon... 

- Add metadata to a frozen file
- Visualise frozen file provenance
- Distribute frozen files with processing code

## Contributing

The library is licenced under Apache-2 licence. All contributions are welcome!
   