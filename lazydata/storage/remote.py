"""
Remote storage backend implementation

"""

import lazy_import
boto3 = lazy_import.lazy_module("boto3")
botocore = lazy_import.lazy_module("botocore")
from urllib.parse import urlparse

class RemoteStorage:
    """
    A storage backend abstraction layer
    """

    @staticmethod
    def get_from_url(remote_url):
        if remote_url.startswith("s3://"):
            return AWSRemoteStorage(remote_url)
        else:
            raise RuntimeError("Url `%s` is not supported as a remote storage backend" % remote_url)

    def check_storage_exists(self):
        """
        Check if the storage backend location exists and is valid

        :return:
        """
        raise NotImplementedError("Not implemented for this storage backend.")


class AWSRemoteStorage(RemoteStorage):

    def __init__(self, remote_url):
        if not remote_url.startswith("s3://"):
            raise RuntimeError("AWSRemoteStorage URL needs to start with s3://")

        # parse the URL
        self.url = remote_url
        p = urlparse(self.url)
        self.bucket_name = p.netloc
        self.path = p.path
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(self.bucket_name)

    def check_storage_exists(self):
        exists = True
        try:
            self.s3.meta.client.head_bucket(Bucket=self.bucket_name)
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                exists = False

        return exists

