"""
Hashing-related function
"""

import hashlib

# BUF_SIZE is totally arbitrary, change for your app!
BUF_SIZE = 65536  # lets read stuff in 64kb chunks!


def calculate_file_sha256(path:str) -> str:
    """
    Calculate a file SHA256 by reading in the file in chunks

    :param path: Full path to the file
    :return: The hex SHA256 digest of the file
    """

    sha256 = hashlib.sha256()

    with open(path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)

    return sha256.hexdigest()
