#!/usr/bin/env bash

# The script to release a new version of lazydata

# Package up:
python3 setup.py sdist bdist_wheel

# Make sure to have twine installed:
python3 -m pip install --upgrade twine

# Upload to PyPI
twine upload --repository-url  https://upload.pypi.org/legacy/ dist/*