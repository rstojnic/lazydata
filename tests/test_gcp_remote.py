import unittest
import os
from uuid import uuid4
from pathlib import Path, PurePosixPath
from lazydata.storage.remote import GCPRemoteStorage
from lazydata.config.config import Config
from lazydata.storage.local import LocalStorage
from lazydata.cli.commands.init import InitCommand
from lazydata import track
from google.cloud import storage

LAZYDATA_TEST_GCP_VAR_NAME = 'lazydata_gcp_test_url'


class TestGCPRemoteStorage(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = storage.Client()

    @classmethod
    def setUpClass(cls):
        # create a lazydata.yml file.
        InitCommand().handle(None)

        # start tracking.
        with open(track('templates/sample-project/data/some_data_file.txt')) as f:
            print(f.read())

    @classmethod
    def tearDownClass(cls):
        os.remove('lazydata.yml')

    def test_constructor(self):
        url = 'gs://bucket/path/to/object'
        remote = GCPRemoteStorage(url)
        self.assertEqual(remote.url, url)
        self.assertEqual(remote.bucket_name, 'bucket')
        self.assertEqual(remote.path_prefix, 'path/to/object')

    def test_constructor_bad_url(self):
        with self.assertRaises(RuntimeError) as err:
            GCPRemoteStorage('http://blah.com')

        self.assertEqual(str(err.exception), 'GCPRemoteStorage URL needs to start with gs://')

    @unittest.skipIf(LAZYDATA_TEST_GCP_VAR_NAME not in os.environ, 'no URL available to test against GCP Storage.')
    def test_upload(self):
        local = LocalStorage()
        config = Config(Path(Path.cwd(), 'templates/sample-project'))

        url = os.environ[LAZYDATA_TEST_GCP_VAR_NAME]
        remote = GCPRemoteStorage(url)
        remote.upload(local, config)

        # make sure the object was created.
        bucket = self.client.bucket(remote.bucket_name)
        sha256 = config.config['files'][0]['hash']
        blob = bucket.blob(str(PurePosixPath(remote.path_prefix, "data", sha256[:2], sha256[2:])))
        self.assertTrue(blob.exists())

        # delete the test object we just created
        blob.delete()

    def test_storage_doesnt_exists(self):
        # let's use something that's unlikely to exist as a bucket
        url = 'gs://{}'.format(str(uuid4()))
        remote = GCPRemoteStorage(url)
        self.assertFalse(remote.check_storage_exists())

    @unittest.skipIf(LAZYDATA_TEST_GCP_VAR_NAME not in os.environ, 'no URL available to test against GCP Storage.')
    def test_storage_exists(self):
        url = os.environ[LAZYDATA_TEST_GCP_VAR_NAME]
        remote = GCPRemoteStorage(url)
        self.assertTrue(remote.check_storage_exists())

    @unittest.skipIf(LAZYDATA_TEST_GCP_VAR_NAME not in os.environ, 'no URL available to test against GCP Storage.')
    def test_download_to_local(self):
        local = LocalStorage()
        config = Config(Path(Path.cwd(), 'templates/sample-project'))

        url = os.environ[LAZYDATA_TEST_GCP_VAR_NAME]
        remote = GCPRemoteStorage(url)

        # first upload something
        remote.upload(local, config)

        # delete it from where we expect it to be
        sha256 = config.config['files'][0]['hash']
        local_path = str(local.hash_to_file(sha256))
        os.remove(local_path)
        self.assertFalse(os.path.exists(local_path))

        # and download it
        remote.download_to_local(config, local, sha256)

        self.assertTrue(os.path.exists(local_path))


if __name__ == '__main__':
    unittest.main()
