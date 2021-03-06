import os
import unittest
from collections import OrderedDict

from pyddl import DdlPrimitiveDataType as DataType
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
            os.remove("test_compressed.ddl")
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

    def test_empty_compressed(self):
        # create document
        document = DdlDocument()

        # write document
        DdlCompressedTextWriter(document).write("test_compressed.ddl")

        # check if file was created
        try:
            self.assertTrue(os.path.isfile("test_compressed.ddl"))
        except FileNotFoundError:
            self.fail("DdlCompressedTextWriter did not create the specified file.")

    @staticmethod
    def create_document():
        document = DdlDocument()
        human_struct = document.add_structure(
                                B"Human", B"human1",
                                [DdlStructure(B"Name", children=[DdlPrimitive(DataType.string, ["Peter"])]),
                                 DdlStructure(B"Age",
                                              children=[DdlPrimitive(DataType.unsigned_int16, [21])])],
                                props=OrderedDict([(B"Weird", True), (B"Funny", 12)]))

        DdlTextWriter.set_comment(human_struct, B"not an alien")
        human_struct.add_structure(B"Self", children=[DdlPrimitive(DataType.ref, [human_struct])])

        # a primitive array
        prim = DdlTextWriter.set_comment(DdlPrimitive(DataType.int32, range(1, 100)), B"100")
        DdlTextWriter.set_max_elements_per_line(prim, 10)

        # a array of vectors of primitives
        vects = DdlPrimitive(DataType.int32, [(x, x * 2) for x in range(1, 100)], None, 2)
        DdlTextWriter.set_max_elements_per_line(vects, 5)

        # add the above primitives to the document, wrapped by another structure
        document.add_structure(B"SomethingElse", children=[DdlStructure(B"AnArray", children=[prim])])
        document.add_structure(B"MoreElse", children=[DdlStructure(B"AnVectorArray", children=[vects])])

        return document

    def test_full(self):
        # create document
        document = self.create_document()

        # write document
        DdlTextWriter(document).write("test.ddl")

        self.assertFilesEqual("test.ddl", "expected.ddl")

    def test_full_compressed(self):
        # create document
        document = self.create_document()

        # write document
        DdlCompressedTextWriter(document).write("test_compressed.ddl")

        self.assertFilesEqual("test_compressed.ddl", "expected_compressed.ddl")

if __name__ == "__main__":
    unittest.main()
