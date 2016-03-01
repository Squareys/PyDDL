import os
import unittest
from pyddl import *
from pyddl.enum import *

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
        # create document
        document = DdlDocument()

        document.add_structure(B"Human", None,
                               [DdlStructure(B"Name", None, [DdlPrimitive(PrimitiveType.string, ["Peter"])]),
                                DdlStructure(B"Age", None, [DdlPrimitive(PrimitiveType.unsigned_int16, [21])])]
                               )

        prim = DdlPrimitive(PrimitiveType.int32, range(1, 100))
        DdlTextWriter.set_max_elements_per_line(prim, 10)

        document.add_structure(B"SomethingElse", None,
                               [DdlStructure(B"AnArray", None, [prim])]
                               )
        document.add_structure(B"MoreElse", None,
                               [DdlStructure(B"AnVectorArray", None,
                                             [DdlPrimitive(PrimitiveType.int32,
                                                           [(1, 2), (12, 42), (13, 31)], None, 2)])]
                               )

        # write document
        DdlTextWriter(document).write("test.oddl")

if __name__ == "__main__":
    unittest.main()
