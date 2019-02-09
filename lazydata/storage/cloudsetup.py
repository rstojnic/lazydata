"""
Common functions to interactively set up credentials for cloud access
"""

import configparser
from pathlib import Path

azure_root = Path(Path.home(), ".azure")
azure_config_path = Path(azure_root, "config")


def setup_credentials(backend: str):
    if backend == "aws":
        setup_aws_credentials()
    elif backend == "azure":
        setup_azure_credentials()
    else:
        print("ERROR: Unrecognised backend `%s`. Currently supported: `aws` and `azure`" % backend)


def setup_aws_credentials():

    public_key = input("Your AWS access key: ")
    private_key = input("Your AWS secret access key: ")
    default_zone = input("Default region [default us-east-1]:")

    if default_zone.strip() == "":
        default_zone = "us-east-1"

    aws_root = Path(Path.home(), ".aws")
    aws_cred = Path(aws_root, "credentials")
    aws_config = Path(aws_root, "config")

    if not aws_root.exists():
        aws_root.mkdir()

    aws_cred_parser = configparser.ConfigParser()
    aws_config_parser = configparser.ConfigParser()

    if aws_cred.exists():
        with open(str(aws_cred), "r") as f:
            aws_cred_parser.read_file(f)

    aws_cred_parser.set("default", "aws_access_key_id", public_key)
    aws_cred_parser.set("default", "aws_secret_access_key", private_key)

    with open(str(aws_cred), "w") as f:
        aws_cred_parser.write(f)

    if aws_config.exists():
        with open(str(aws_config), "r") as f:
            aws_config_parser.read_file(f)

    aws_config_parser.set("default", "region", default_zone)

    with open(str(aws_config), "w") as f:
        aws_config_parser.write(f)

    print("Credentials written into %s" % str(aws_root))


def setup_azure_credentials():

    private_key = input("Your Azure storage access key: ")

    if not azure_root.exists():
        azure_root.mkdir()

    azure_config_parser = configparser.ConfigParser()

    if azure_config_path.exists():
        with open(str(azure_config_path), "r") as f:
            azure_config_parser.read_file(f)

    azure_config_parser.set("storage", "key", private_key)

    with open(str(azure_config_path), "w") as f:
        azure_config_parser.write(f)

    print("Credentials written into %s" % str(azure_root))
