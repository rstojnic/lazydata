import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lazydata",
    python_requires='>=3.5.2',
    version="1.0.18",
    author="Robert Stojnic",
    author_email="robert.stojnic@gmail.com",
    description="Scalable data dependencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rstojnic/lazydata",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pyyaml', "peewee", "boto3", "lazy-import"],
    scripts=['lazydata/bin/lazydata']
)
