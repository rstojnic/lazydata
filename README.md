# Lazy-data: lazy loading for data

Manage your data dependencies using lazy loading. Only download data when needed and with all references in code. 

It’s the easiest way to incorporate data into your git repository, with your own choice of storage backend, such as S3 or a directory on a remote server. 

This is especially useful for Machine Learning and Data Science projects. 

## Installation

Lazy-data is a Python 3 library intended to be used with Python code. 

Install with pip:

```bash
$ pip install lazy-data
```

## Getting started

You wrote some awesome machine learning or data science code that takes `my_big_table.csv` as input. Now it's the time to share with your team. 

Your *could* upload the file to a shared server manually, tell them where you put it or make a download script, but it quickly turns into a mess of scripts and files. 

Lazy-data can manage this whole process for you, and also guarantee that your collaborators have the correct version of the file as verified by its hash. 

### Configuring 

To share the data files with your team you need to set up a shared location to which everyone has access to. We currently support AWS S3 and directory-over-SSH as storage backends. 

To enable lazy-data on your repository, run the following command in your git repository root: 

```bash
$ lazy-data config 
```

This will ask you which storage backend you want to use. For AWS you will have to provide your API key, and for directory-over-ssh the name of the server, path and an SSH key to access it.  

A new file `lazy-data.jsonl` will be created. This files is a JSON-line file, meaning each JSON record is a single line in the file. It contains:

- The location of your storage backend
- A list of all of your data dependencies  

Your secrets will be stored in `~/.lazy-data/secrets` outside of the git repository.

You are now ready to add lazy data dependencies to your Python project. 

### Basic usage 

Use the `lazy_data()` function to add a lazy data dependency. 

**my_script.py**
```python
from lazy_data import lazy_data

lazy_data("my_big_table.csv")

# at this point lazy-data will ensure `my_big_table.csv`
# file exists in the current directory
```

When you execute `my_script.py` one of the following happens:
 
 - If the file `my_big_table.csv` **exists** and **is not recorded** in `lazy-data.jsonl` it will be marked as a dependency of `my_script.py` and added to `lazy-data.jsonl` with its hash.
 - If the file `my_big_table.csv` **exists** and **is recorded** in `lazy-data.jsonl`, the hashes will be checked against the stored value. If the hashes are the same, nothing else happens. If the hashes are different, the hash will be updated if the hash hasn't been part of a git commit yet, otherwise a new version of the file will be recorded.   
 - If the file `my_big_table.csv` **does not exist**, lazy-data will look for it in the storage backend using the information in `lazy-data.jsonl`. It will then download it before continuing. 
 
To make sure your team has the same version of the file as you, always keep the `lazy-data.jsonl` file in git, as it defines all the external file dependencies. 

Commit all of your code files, together with `lazy-data.jsonl` into git as usual. 

And that's it! If your team mate tries to execute `my_script.py` they will be prompted for backend access credentials (if they haven't provided those already) and will seamlessly download the correct data files. 

### Usage with Python classes

To use with a Python class, put `lazy_data` into your `__init__()` method. 

**my_class.py**
```python
from lazy_data import lazy_data

class MyClass:
    def __init__(self):        
        lazy_data("my_big_table.csv")
```

### Advanced options

The `lazy_data` function has further options that let you customise the behaviour. 

`lazy_data(file_path, download_link=None, overwrite_hash="uncommitted", compress=False)`

Arguments:
- `file_path` - the local file path to an existing file(s). Either a string or a list of strings. Glob-style wildcards are accepted, e.g. `"data/*.csv"`. 
- `download_link` - alternative download link for the file, e.g. if it's a public dataset or already available somewhere else. 
- `overwrite_hash` - specifies when to overwrite an existing hash in `lazy-data.jsonl`. Default is `uncommitted` meaning that the hash will be over-written if the line containing the hash hasn't been yet committed to git. Other possible values are `never` and `always`. The former will record all versions of the file, and the later only makes sense if you treat all files as immutable.
- `compress` if to store this fill compressed in the backend.     

## Contributing

The library is licenced under Apache-2 licence. Contributions are welcome!
   