import os
import unittest

from pyddl import *

__author__ = "Jonathan Hale"


class DdlTextWriterTest(unittest.TestCase):

    def readContents(self, filename):
        """
        Open, read the contents and then close a file.
        :param filename: name of the file to read the contents of
        :return: Contents of the file with given filename
        """
        file = open(filename)
        contents = file.read()
        file.close()

        return contents

    def assertFilesEqual(self, test_filename, expected_filename):
        """
        Check whether the contents of two files are equal
        :param test_filename: name of the file to test
        :param expected_filename: name of the file containing expected content
        """
        self.assertEqual(self.readContents(test_filename), self.readContents(expected_filename))

    def tearDown(self):
        try:
            os.remove("test.ddl")
        except FileNotFoundError:
            pass  # test_empty failed?

    def test_empty(self):
        # create document
        document = DdlDocument()

        # write document
        DdlTextWriter(document).write("test.ddl")

        # check if file was created
        try:
            self.assertTrue(os.path.isfile("test.ddl"))
        except FileNotFoundError:
            self.fail("DdlTextWriter did not create the specified file.")

    def test_full(self):
        # create document
        document = DdlDocument()

        document.add_structure(B"Human", None,
                               [DdlStructure(B"Name", None, [DdlPrimitive(PrimitiveType.string, ["Peter"])]),
                                DdlStructure(B"Age", None, [DdlPrimitive(PrimitiveType.unsigned_int16, [21])])]
                               )

        prim = DdlPrimitive(PrimitiveType.int32, range(1, 100))
        DdlTextWriter.set_max_elements_per_line(prim, 10)

        vects = DdlPrimitive(PrimitiveType.int32, [(x, x*2) for x in range(1, 100)], None, 2)
        DdlTextWriter.set_max_elements_per_line(vects, 5)

        document.add_structure(B"SomethingElse", None, [DdlStructure(B"AnArray", None, [prim])])
        document.add_structure(B"MoreElse", None, [DdlStructure(B"AnVectorArray", None, [vects])])

        # write document
        DdlTextWriter(document).write("test.ddl")

        self.assertFilesEqual("test.ddl", "expected.ddl")

if __name__ == "__main__":
    unittest.main()
