import os
import unittest
from pathlib import Path
import argparse

from lazydata.cli.commands import addremote, init
from lazydata.config.config import Config
from lazydata import track

from tests.test_gcp_remote import LAZYDATA_TEST_GCP_VAR_NAME, init_lazydata


class TestAddRemoteGCP(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_lazydata()

    @classmethod
    def tearDownClass(cls):
        os.remove('lazydata.yml')

    @unittest.skipIf("GOOGLE_APPLICATION_CREDENTIALS" not in os.environ, "testAddRemoteWithCredentials: no credentials found")
    @unittest.skipIf(LAZYDATA_TEST_GCP_VAR_NAME not in os.environ, 'no URL available to test against GCP Storage.')
    def testAddRemoteWithCredentials(self):
        add_remote_cmd = addremote.AddRemoteCommand()

        parser = add_remote_cmd.add_arguments(argparse.ArgumentParser())
        args = parser.parse_args([os.environ[LAZYDATA_TEST_GCP_VAR_NAME]])
        add_remote_cmd.handle(args)

        config = Config()
        self.assertTrue('remote' in config.config)
        self.assertEqual(config.config['remote'], os.environ[LAZYDATA_TEST_GCP_VAR_NAME])

    @unittest.skipIf("GOOGLE_APPLICATION_CREDENTIALS" in os.environ, "credentials found so this test doesn't make sense")
    @unittest.skipIf(LAZYDATA_TEST_GCP_VAR_NAME not in os.environ, 'no URL available to test against GCP Storage.')
    def testAddRemoteWithOutCredentials(self):
        add_remote_cmd = addremote.AddRemoteCommand()

        parser = add_remote_cmd.add_arguments(argparse.ArgumentParser())
        args = parser.parse_args([os.environ[LAZYDATA_TEST_GCP_VAR_NAME]])
        add_remote_cmd.handle(args)
        config = Config()
        self.assertFalse('remote' in config.config)


if __name__ == '__main__':
    unittest.main()
