import contextlib
import time
import unittest
import os
import sys
import shutil
import copy
from unittest.mock import patch
import threading



from upsonic import Upsonic, HASHES, Upsonic_Serial, Upsonic_Cloud_Pro
import upsonic


class ptest_object:
    def exp(self):
        return {"test": "test"}

def pmy_function():
    return 123


class TestCloudPro(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        cls.remote = Upsonic_Cloud_Pro(os.environ.get("CLOUD_TEST_DATABASE_NAME","cloud-workflow"), os.environ.get("CLOUD_PRO_ACCESS_KEY"))

    def test_remote_api_set_get_deletestring(self):


        the = time.time()
        value = f"Value{the}"

        self.remote.set("key", value)
        time.sleep(1)

        self.assertEqual(self.remote.get("key",), value)

        self.remote.delete("key")
        time.sleep(1)


        self.assertNotEqual(self.remote.get("key"), value)

    def test_remote_api_active(self):
        self.remote.active(pmy_function)
        time.sleep(1)
        self.assertEqual(self.remote.get("pmy_function")(), 123)
        self.remote.delete("pmy_function")

backup = sys.argv
sys.argv = [sys.argv[0]]
unittest.main(exit=False)
sys.argv = backup
