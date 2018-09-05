[![CircleCI](https://circleci.com/gh/rstojnic/lazydata/tree/master.svg?style=shield)](https://circleci.com/gh/rstojnic/lazydata/tree/master)

# lazydata: scalable data dependencies

`lazydata` is a minimalist library for including data dependencies into Python projects. 

**Problem**: Keeping all data files in git (e.g. via git-lfs) results in a bloated repository copy that takes ages to pull. Keeping code and data out of sync is a disaster waiting to happen.     

**Solution**: `lazydata` only stores references to data files in git, and syncs data files on-demand when they are needed.

**Why**: The semantics of code and data are different - code needs to be versioned to merge it, and data just needs to be kept in sync. `lazydata` achieves exactly this in a minimal way.    

**Benefits**:

- Keeps your git repository clean with just code, while enabling seamless access to any number of linked data files 
- Data consistency assured using file hashes and automatic versioning
- Choose your own remote storage backend: AWS S3 or (coming soon:) directory over SSH

`lazydata` is primarily designed for machine learning and data science projects. 
See [this medium post](https://medium.com/@rstojnic/structuring-ml-projects-so-they-can-grow-b63e89c8be8f) for more.  

<div align="center">
<img width="520" src="https://github.com/rstojnic/lazydata/raw/master/docs/lazydata-project-col2.png">
</div>

## Getting started 

In this section we'll show how to use `lazydata` on an example project.

### Installation

Install with pip (requires Python 3.5+):

```bash
$ pip install lazydata
```

### Add to your project

To enable `lazydata`, run in project root:

```bash
$ lazydata init 
```

This will initialise `lazydata.yml` which will hold the list of files managed by lazydata. 

### Tracking a file

To start tracking a file use `track("<path_to_file>")` in your code:

**my_script.py**
```python
from lazydata import track

# store the file when loading  
import pandas as pd
df = pd.read_csv(track("data/my_big_table.csv"))

print("Data shape:" + df.shape)

```

Running the script the first time will start tracking the file:

```bash
$ python my_script.py
## lazydata: Tracking a new file data/my_big_table.csv
## Data shape: (10000,100)
```

The file is now tracked and has been backed-up in your local lazydata cache in `~/.lazydata` and added to **lazydata.yml**:
```yaml
files:
  - path: data/my_big_table.csv
    hash: 2C94697198875B6E...
    usage: my_script.py

```

If you re-run the script without modifying the data file, lazydata will just quickly check that the data file hasn't changed and won't do anything else. 

If you modify the data file and re-run the script, this will add another entry to the yml file with the new hash of the data file, i.e. data files are automatically versioned. If you don't want to keep past versions, simply remove them from the yml. 

And you are done! This data file is now tracked and linked to your local repository.

### Sharing your tracked files

To access your tracked files from multiple machines add a remote storage backend where they can be uploaded. To use S3 as a remote storage backend run:

```bash
$ lazydata add-remote s3://mybucket/lazydata
```

This will configure the S3 backend and also add it to `lazydata.yml` for future reference. 

You can now git commit and push your `my_script.py` and `lazydata.yml` files as you normally would. 
 
To copy the stored data files to S3 use:

```bash
$ lazydata push
```

When your collaborator pulls the latest version of the git repository, they will get the script and the `lazydata.yml` file as usual.  

Data files will be downloaded when your collaborator runs `my_script.py` and the `track("my_big_table.csv")` is executed:

```bash
$ python my_script.py
## lazydata: Downloading stored file my_big_table.csv ...
## Data shape: (10000,100)
``` 
 
To get the data files without running the code, you can also use the command line utility:

```bash
# download just this file
$ lazydata pull my_big_table.csv

# download everything used in this script
$ lazydata pull my_script.py

# download everything stored in the data/ directory and subdirs
$ lazydata pull data/

# download the latest version of all data files
$ lazydata pull
```

Because `lazydata.yml` is tracked by git you can safely make and switch git branches. 

### Data dependency scenarios

You can achieve multiple data dependency scenarios by putting `lazydata.track()` into different parts of the code:

- Jupyter notebook data dependencies by using tracking in notebooks
- Data pipeline output tracking by tracking saved files 
- Class-level data dependencies by tracking files in `__init__(self)`
- Module-level data dependencies by tracking files in `__init__.py`
- Package-level data dependencies by tracking files in `setup.py` 

### Coming soon... 

- Examine stored file provenance and properties
- Faceting multiple files into portable datasets
- Storing data coming from databases and APIs
- More remote storage options

## Stay in touch

This is an early stable beta release. To find out about new releases subscribe to our [new releases mailing list](http://eepurl.com/dFYLIL). 

## Contributing

The library is licenced under Apache-2 licence. All contributions are welcome!
   
