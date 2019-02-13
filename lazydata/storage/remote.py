"""
Remote storage backend implementation

"""
from typing import Optional

import lazy_import
from pathlib import PurePosixPath, Path

import os, threading, sys
import configparser

from lazydata.config.config import Config
from lazydata.storage.hash import calculate_file_sha256
from lazydata.storage.local import LocalStorage
from lazydata.storage.cloudsetup import azure_config_path

from pySmartDL import SmartDL

boto3 = lazy_import.lazy_module("boto3")
botocore = lazy_import.lazy_module("botocore")
azure_storage = lazy_import.lazy_module("azure.storage.blob.blockblobservice")
from urllib.parse import urlparse

import logging

logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)


class RemoteStorage:
    """
    A storage backend abstraction layer
    """

    @staticmethod
    def get_from_url(remote_url: str, endpoint_url: Optional[str] = None):
        if remote_url.startswith("s3://"):
            return AWSRemoteStorage(remote_url, endpoint_url=endpoint_url)
        elif remote_url.startswith("az://"):
            return AzureRemoteStorage(remote_url, endpoint_url=endpoint_url)
        else:
            raise RuntimeError("Url `%s` is not supported as a remote storage backend" % remote_url)

    @staticmethod
    def get_from_config(config: Config):
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

    def upload(self, local: LocalStorage, config: Config):
        """
        Upload the local storage cache for a config file

        :param local:
        :param config:
        :return:
        """
        raise NotImplementedError("Not implemented for this storage backend.")

    def download_to_local(self, config: Config, local: LocalStorage, sha256: str):
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
        raise NotImplementedError(
            "Uploading to the URL remote storage is not implemented. "
            "See `lazydata add-source` command."
        )

    @staticmethod
    def download_to_local(
        config: Config,
        local: LocalStorage,
        sha256: Optional[str] = None,
        source_url: Optional[str] = None,
        path: Optional[str] = None,
    ):
        if sha256 is not None:
            local_path = local.hash_to_file(sha256)
            source_url = config.source_url(sha256=sha256)
            if source_url is None:
                raise RuntimeError(
                    "Cannot find source_url for file with hash `%s`. "
                    "See `lazydata add-source` command." % sha256
                )
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
            raise RuntimeError(
                "Hash for the downloaded file `%s` is incorrect. "
                "File might be corrupted in the remote storage backend." % str(local_path)
            )
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
        self.s3 = boto3.resource("s3", endpoint_url=endpoint_url)
        self.client = boto3.client("s3", endpoint_url=endpoint_url)

    def check_storage_exists(self):
        exists = True
        try:
            self.s3.meta.client.head_bucket(Bucket=self.bucket_name)
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response["Error"]["Code"])
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
                error_code = int(e.response["Error"]["Code"])
                if error_code == 404:
                    exists = False

            if not exists:
                transfer.upload_file(
                    str(local_path),
                    self.bucket_name,
                    s3_key,
                    callback=S3ProgressPercentage(str(local_path), real_path),
                )

                # Upload the success key, to verify that the upload has completed
                self.s3.Bucket(self.bucket_name).put_object(Key=s3_success_key, Body="")
        # Final newline to flush the progress indicator
        print()

    def download_to_local(self, config: Config, local: LocalStorage, sha256: str, **kwargs):
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
                raise RuntimeError(
                    "Hash for the downloaded file `%s` is incorrect. File might be corrupted in the remote storage backend."
                    % str(local_path)
                )
        except botocore.exceptions.NoCredentialsError:
            raise RuntimeError(
                "Download failed. AWS credentials not found. Run `lazydata config aws` to configure them."
            )


class ProgressPercentage:
    def __init__(self, real_filename: str):
        self._real_filename = real_filename
        self._lock = threading.Lock()

    def _display_percentage(self, current: int, total: int):
        with self._lock:
            percentage = (current / total) * 100
            sys.stdout.write(
                "\r Uploading `%s`  %s / %s  (%.2f%%)"
                % (self._real_filename, current, total, percentage)
            )
        sys.stdout.flush()

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("__call__ not implemented for this class")


class S3ProgressPercentage(ProgressPercentage):
    def __init__(self, filename, real_filename):
        super.__init__(real_filename)
        self._seen_so_far = 0
        self._filename = filename
        self._size = float(os.path.getsize(filename))

    def __call__(self, bytes_amount):
        self._seen_so_far += bytes_amount
        self._display_percentage(self._seen_so_far, self._size)


class AzureProgressPercentage(ProgressPercentage):
    def __call__(self, current: int, total: int):
        self._display_percentage(current, total)


class AzureRemoteStorage(RemoteStorage):
    def __init__(self, remote_url: str, endpoint_url: Optional[str] = None):
        if not remote_url.startswith("az://"):
            raise RuntimeError("AzureRemoteStorage URL needs to start with az://")

        p = urlparse(remote_url)
        self.account_name = p.netloc
        path_prefix = p.path.strip()
        if path_prefix.startswith("/"):
            path_prefix = path_prefix[1:]
        if "/" in path_prefix:
            self.container_name, self.blob_name = path_prefix.split("/", 1)
        else:
            self.container_name, self.blob_name = path_prefix, ""

        # Azure python API does not default to reading the CLI config
        azure_config = configparser.ConfigParser()
        if azure_config_path.exists():
            with open(str(azure_config_path), "r") as f:
                azure_config.read_file(f)

        account_key = azure_config.get("storage", "key")

        self.blob_service = azure_storage.BlockBlobService(
            account_name=self.account_name, account_key=account_key, endpoint_suffix=endpoint_url
        )

    def check_storage_exists(self):
        return self.blob_service.exists(self.container_name)

    def upload(self, local: LocalStorage, config: Config):
        # look for all hashes in the config file and upload
        all_sha256 = [e["hash"] for e in config.config["files"]]

        for sha256 in all_sha256:
            local_path = local.hash_to_file(sha256)
            remote_path = local.hash_to_remote_path(sha256)
            azure_path = str(PurePosixPath(self.blob_name, remote_path))

            # get the filename the user would recognise
            real_path = [e["path"] for e in config.config["files"] if e["hash"] == sha256]
            if len(real_path) > 0:
                real_path = real_path[-1]
            else:
                # file no longer in config? this shouldn't happen but don't fail.
                real_path = ""

            # check if the remote location already exists
            if not self.blob_service.exists(self.container_name, azure_path):
                print(self.container_name)
                print(azure_path)
                print(local_path)
                self.blob_service.create_blob_from_path(
                    self.container_name,
                    azure_path,
                    str(local_path),
                    progress_callback=AzureProgressPercentage(real_path),
                )

        # Final newline to flush the progress indicator
        print()

    def download_to_local(self, config: Config, local: LocalStorage, sha256: str):
        try:
            local_path = local.hash_to_file(sha256)
            remote_path = local.hash_to_remote_path(sha256)
            azure_path = str(PurePosixPath(self.blob_name, remote_path))

            local_path.parent.mkdir(parents=True, exist_ok=True)

            real_path = [e["path"] for e in config.config["files"] if e["hash"] == sha256]
            if len(real_path) > 0:
                real_path = real_path[-1]
            else:
                # file no longer in config? this shouldn't happen but don't fail.
                real_path = ""

            print("Downloading `%s`" % real_path)

            self.blob_service.get_blob_to_path(self.container_name, azure_path, str(local_path))

            # make sure the sha256 of the just downloaded file is correct
            downloaded_sha256 = calculate_file_sha256(str(local_path))
            if sha256 != downloaded_sha256:
                raise RuntimeError(
                    "Hash for the downloaded file `%s` is incorrect. File might be corrupted in the remote storage backend."
                    % str(local_path)
                )

        except Exception:  # TODO: figure out this exception
            raise RuntimeError(
                "Download failed. Azure credentials not found. Run `lazydata config az` to configure them."
            )
