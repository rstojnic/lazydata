"""
Remote storage backend implementation

"""
from typing import Optional

import lazy_import
from pathlib import PurePosixPath, Path

import os, threading, sys

from lazydata.config.config import Config
from lazydata.storage.hash import calculate_file_sha256
from lazydata.storage.local import LocalStorage

from pySmartDL import SmartDL

boto3 = lazy_import.lazy_module("boto3")
botocore = lazy_import.lazy_module("botocore")
from urllib.parse import urlparse

import logging
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

class RemoteStorage:
    """
    A storage backend abstraction layer
    """

    @staticmethod
    def get_from_url(remote_url:str, endpoint_url:str):
        if remote_url.startswith("s3://"):
            return AWSRemoteStorage(remote_url, endpoint_url=endpoint_url)
        else:
            raise RuntimeError("Url `%s` is not supported as a remote storage backend" % remote_url)

    @staticmethod
    def get_from_config(config:Config):
        if "remote" in config.config:
            return RemoteStorage.get_from_url(config.config["remote"], config.config["endpoint"])
        else:
            raise RuntimeError("Remote storage backend not configured for this lazydata project.")


    def check_storage_exists(self):
        """
        Check if the storage backend location exists and is valid

        :return:
        """
        raise NotImplementedError("Not implemented for this storage backend.")

    def upload(self, local:LocalStorage, config:Config):
        """
        Upload the local storage cache for a config file

        :param local:
        :param config:
        :return:
        """
        raise NotImplementedError("Not implemented for this storage backend.")


    def download_to_local(self, config:Config, local:LocalStorage, sha256:str):
        """
        Download a file with a specific SHA256 and save it into path

        :param config: Config
        :param local:
        :param sha256:
        :return:
        """
        raise NotImplementedError("Not implemented for this storage backend.")


class UrlRemoteStorage:
    """
    A storage backend abstraction layer
    """
    @staticmethod
    def check_storage_exists():
        return True

    def upload(self, local: LocalStorage, config: Config):
        raise NotImplementedError("Uploading to the URL remote storage is not implemented. "
                                  "See `lazydata add-source` command.")

    @staticmethod
    def download_to_local(config: Config, local: LocalStorage, sha256: Optional[str] = None,
                          source_url: Optional[str] = None, path: Optional[str] = None):
        if sha256 is not None:
            local_path = local.hash_to_file(sha256)
            source_url = config.source_url(sha256=sha256)
            if source_url is None:
                raise RuntimeError("Cannot find source_url for file with hash `%s`. "
                                   "See `lazydata add-source` command." % sha256)
            if path is None:
                path = config.path(sha256=sha256)
                if path is None:
                    raise RuntimeError("Cannot find path for downloading a file.")
        elif source_url is not None:
            if path is None:
                path = config.path(source_url=source_url)
                if path is None:
                    raise RuntimeError("Cannot find path for downloading a file.")
            local_path = Path(path)
        else:
            raise RuntimeError("Cannot download a file without sha256 and source_url specified.")

        local_path.parent.mkdir(parents=True, exist_ok=True)

        f = SmartDL(urls=source_url, dest=str(local_path), progress_bar=False)
        print("Downloading `%s`" % path)
        f.start()
        # make sure the sha256 of the just downloaded file is correct
        downloaded_sha256 = calculate_file_sha256(str(local_path))
        if sha256 is not None and sha256 != downloaded_sha256:
            raise RuntimeError("Hash for the downloaded file `%s` is incorrect. "
                               "File might be corrupted in the remote storage backend." % str(local_path))
        local.store_file(path=path)


class AWSRemoteStorage(RemoteStorage):

    def __init__(self, remote_url, endpoint_url=None):
        if not remote_url.startswith("s3://"):
            raise RuntimeError("AWSRemoteStorage URL needs to start with s3://")

        # parse the URL
        self.url = remote_url
        p = urlparse(self.url)
        self.bucket_name = p.netloc
        self.path_prefix = p.path.strip()
        if self.path_prefix.startswith("/"):
            self.path_prefix = self.path_prefix[1:]
        # get the reusable clients and resources
        self.s3 = boto3.resource('s3', endpoint_url=endpoint_url)
        self.client = boto3.client('s3', endpoint_url=endpoint_url)

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

    def upload(self, local: LocalStorage, config: Config):
        transfer = boto3.s3.transfer.S3Transfer(self.client)

        # look for all hashes in the config file and upload
        all_sha256 = [e["hash"] for e in config.config["files"]]

        for sha256 in all_sha256:
            local_path = local.hash_to_file(sha256)
            remote_path = local.hash_to_remote_path(sha256)
            s3_key = str(PurePosixPath(self.path_prefix, remote_path))
            s3_success_key = "%s.completed" % s3_key

            # get the filename the user would recognise
            real_path = [e["path"] for e in config.config["files"] if e["hash"] == sha256]
            if len(real_path) > 0:
                real_path = real_path[-1]
            else:
                # file no longer in config? this shouldn't happen but don't fail.
                real_path = ""

            # check if the remote location already exists
            exists = True
            try:
                self.client.head_object(Bucket=self.bucket_name, Key=s3_success_key)
            except botocore.exceptions.ClientError as e:
                error_code = int(e.response['Error']['Code'])
                if error_code == 404:
                    exists = False

            if not exists:
                transfer.upload_file(str(local_path),
                                     self.bucket_name,
                                     s3_key,
                                     callback=S3ProgressPercentage(str(local_path), real_path))

                # Upload the success key, to verify that the upload has completed
                self.s3.Bucket(self.bucket_name).put_object(Key=s3_success_key, Body="")
        # Final newline to flush the progress indicator
        print()

    def download_to_local(self, config:Config, local: LocalStorage, sha256: str, **kwargs):
        try:
            transfer = boto3.s3.transfer.S3Transfer(self.client)

            local_path = local.hash_to_file(sha256)
            remote_path = local.hash_to_remote_path(sha256)
            s3_key = str(PurePosixPath(self.path_prefix, remote_path))

            local_path.parent.mkdir(parents=True, exist_ok=True)

            real_path = [e["path"] for e in config.config["files"] if e["hash"] == sha256]
            if len(real_path) > 0:
                real_path = real_path[-1]
            else:
                # file no longer in config? this shouldn't happen but don't fail.
                real_path = ""

            print("Downloading `%s`" % real_path)

            transfer.download_file(self.bucket_name, s3_key, str(local_path))

            # make sure the sha256 of the just downloaded file is correct
            downloaded_sha256 = calculate_file_sha256(str(local_path))
            if sha256 != downloaded_sha256:
                raise RuntimeError("Hash for the downloaded file `%s` is incorrect. File might be corrupted in the remote storage backend." % str(local_path))
        except botocore.exceptions.NoCredentialsError:
            raise RuntimeError("Download failed. AWS credentials not found. Run `lazydata config aws` to configure them.")


class S3ProgressPercentage:
    def __init__(self, filename, real_filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self._real_filename = real_filename

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r Uploading `%s`  %s / %s  (%.2f%%)" % (
                    self._real_filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()