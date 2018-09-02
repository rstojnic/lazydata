"""
Common functions to interactively set up credentials for cloud access
"""

from pathlib import Path

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

    with open(str(aws_cred), "w") as f:
        f.writelines([
            "[default]\n",
            "aws_access_key_id = %s\n" % public_key,
            "aws_secret_access_key = %s\n" % private_key,
        ])

    with open(str(aws_config), "w") as f:
        f.writelines([
            "[default]\n",
            "region = %s\n" % default_zone,
        ])

    print("Credentials written into %s" % str(aws_root))
