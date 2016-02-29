import io
import os
import unittest
from pyddl import *

__author__ = "Jonathan Hale"


class DdlTextWriterTest(unittest.TestCase):

    def tearDown(self):
        try:
            os.remove("test.oddl")
        except FileNotFoundError:
            pass  # test_empty failed?

    def test_empty(self):
        # create document
        document = DdlDocument()

        # write document
        DdlTextWriter(document).write("test.oddl")

        # check if file was created
        try:
            self.assertTrue(os.path.isfile("test.oddl"))
        except FileNotFoundError:
            self.fail("DdlTextWriter did not create the specified file.")

    def test_full(self):
        self.assertTrue(True)
        pass

if __name__ == "__main__":
    unittest.main()
