# filefreezer: scalable data dependencies

`filefreezer` is a minimalist library for including data dependencies into Python projects. 

**Problem**: Keeping data files in git (e.g. via git-lfs) results in a bloated repository that take ages to pull.  

**Our solution**: `filefreezer` store only references to data file in git, and syncs data files on-demand when they are needed.

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

To enable `filefreezer`:

```bash
$ freezer init s3://mybucket/freezer
```

This will:
 
1. Set your permanent storage location to S3 (the other options is directory over SSH)
2. Create `freezer.yml` which contains a list of all the frozen files. A frozen file is represented by its path and hash.

### Usage 

In this section we'll run through the set of steps you need to use file freezer. 

Lets say our repository structure looks like this: 

``` 
freezer.yml
my_script.py
data/
     my_big_table.csv
```

To add the datafile to the freezer, use `freeze("<path_to_file>")` in the code:

**my_script.py**
```python
from filefreezer import freeze

# freeze the file when loading  
import pandas as pd
df = pd.read_csv(freeze("data/my_big_table.csv"))

print("Data shape:" + df.shape)

```

Using `freeze("data/my_big_table.csv")` adds this file  to your local freezer:

**freezer.yml**
```yaml
storage: s3://mybucket/freezer
files:
  - path: data/my_big_table.csv
    hash: 2C94697198875B6E...
    usage: my_script.py

```

Now you can commit and push your  `my_script.py` and `freezer.yml` files as you normally would. 
 
To upload the data files use:

```bash
$ freezer push
```

This command uploads the cached version of your frozen files from your local machine to the remote storage (in our case S3). 

When your collaborator pulls the latest version of the git repository, they will get the script and the `freezer.yml` file as usual.  

Data files will be downloaded when your collaborator runs `my_script.py` and the `freeze("my_big_table.csv")` is executed:

```bash
$ python my_script.py
## FREEZER: Downloading frozen file my_big_table.csv ...
## Data shape: (10000,100)
``` 

To get the data files without running any code, you can also use the command line utility:

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

### Advanced usage

You can achieve multiple data dependency scenarios by putting `freeze()` into different parts of the code:

- Add to outputs of your data pipeline to freeze the outputs
- Add to `__init__(self)` of a class to add data as a class dependency
- Add to `__init__.py` of a module to add data as a module dependency
- Add to `setup.py` to add data as a Python package dependency

## Contributing

The library is licenced under Apache-2 licence. All contributions are welcome!
   