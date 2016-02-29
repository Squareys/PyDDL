from abc import abstractmethod
import math
from pyddl.enum import PrimitiveType

__author__ = "Jonathan Hale"


class DdlPrimitive:
    """
    An OpenDDL primitive structure.
    """

    def __init__(self, data_type, data, name=None, vector_size=0):
        """
        Constructor
        :param data_type: primitive data type (see pyddl.enum.PrimitiveType)
        :param data: list of values. If vector_size != 0, the list should contain tuples
        :param name: name of the primitive structure
        :param vector_size: size of the contained vectors
        """
        self.data_type = data_type
        self.name = name
        self.vector_size = vector_size
        self.data = data

    def is_simple_primitive(self):
        return len(self.data) == 1 and self.vector_size <= 4


class DdlStructure:
    """
    An OpenDDL structure.
    """

    def __init__(self, identifier, name=None, structures=[]):
        self.structures = structures
        self.properties = dict()
        self.identifier = identifier
        self.name = name if name != "" else None

    def is_simple_structure(self):
        """
        A structure is simple if it contains exactly one primitive and has no properties or name.
        :return: true if this structure is simple
        """
        if len(self.structures) != 1:
            return False
        if len(self.properties) != 0:
            return False
        if self.name is not None:
            return False
        if not isinstance(self.structures[0], DdlPrimitive):
            return False

        return self.structures[0].is_simple_primitive()

    def add_structure(self, identifier, name=None, structures=[]):
        """
        Add a substructure
        :param identifier: structure identifier
        :param name: optional name
        :param structures: list of substructures
        :return: self (for method chaining)
        """
        self.structures.append(DdlStructure(identifier, name, structures))
        return self

    def add_primitive(self, data_type, data, name=None, vector_size=0):
        """
        Add a primitive substructure
        :param data_type: primitive data type (see pyddl.enum.PrimitiveType)
        :param data: list of values. If vector_size != 0, the list should contain tuples
        :param name: name of the primitive structure
        :param vector_size: size of the contained vectors
        :return: self (for method chaining)
        """
        self.structures.append(DdlPrimitive(data_type, data, name, vector_size))
        return self


class DdlDocument:
    """
    An OpenDDL document.
    """

    def __init__(self):
        self.structures = []

    def add_structure(self, identifier, name, structures):
        self.structures.append(DdlStructure(identifier, name, structures))


class DdlWriter:
    """
    Abstract class for classes responsible for writing OpenDdlDocuments.
    """

    def __init__(self, document):
        self.doc = document

    def get_document(self):
        """
        :return: document to be written by this writer.
        """
        return self.doc

    @abstractmethod
    def write(self, filename):
        """
        Write the writers document to a specified file.
        :param file: file to write to
        :return: nothing
        """
        pass


class DdlTextWriter(DdlWriter):
    """
    OpenDdlWriter which writes OpenDdlDocuments in human-readable text form.
    """

    def __init__(self, document, rounding=6):
        DdlWriter.__init__(self, document)

        self.file = None
        self.indent = B""
        self.rounding = rounding

    @staticmethod
    def to_float_byte_rounded(f):
        if (math.isinf(f)) or (math.isnan(f)):
            return B"0.0"
        else:
            return bytes(str(round(f, 6)), "UTF-8")

    @staticmethod
    def to_float_byte(f):
        if (math.isinf(f)) or (math.isnan(f)):
            return B"0.0"
        else:
            return bytes(str(f), "UTF-8")

    @staticmethod
    def to_int_byte(i):
        return bytes(str(i), "UTF-8")

    @staticmethod
    def to_string_byte(s):
        return bytes(s, "UTF-8")

    @staticmethod
    def to_bool_byte(b):
        return B"true" if b else B"false"

    def inc_indent(self):
        """
        Increase the current line indent.
        """
        self.indent = self.indent + B"\t"

    def dec_indent(self):
        """
        Decrease the current line indent.
        """
        self.indent = self.indent[:-1]

    def write(self, filename):
        self.file = open(filename, "wb")

        for structure in self.get_document().structures:
            self.file.write(self.structure_as_text(structure))

        self.file.close()

    def property_as_text(self, prop):
        value = prop[1]
        if isinstance(value, int):
            value_bytes = self.to_int_byte(value)
        elif isinstance(value, float):
            value_bytes = self.to_float_byte(value)
        elif isinstance(value, str):
            value_bytes = B"\"" + bytes(value, "UTF-8") + B"\""
        else:
            raise TypeError("ERROR: Unknown property type for property \"{}\"".format(prop[0]))

        return prop[0] + B" = " + value_bytes

    def primitive_as_text(self, primitive, no_indent=False):
        text = (B"" if no_indent else self.indent) + bytes(primitive.data_type.name, "UTF-8") + B" "

        if primitive.name is not None:
            text += primitive.name + B" "

        # find appropriate conversion function
        if primitive.data_type in [PrimitiveType.bool]:
            to_bytes = self.to_bool_byte
        elif primitive.data_type in [PrimitiveType.double, PrimitiveType.float]:
            to_bytes = self.to_float_byte if self.rounding is None else self.to_float_byte_rounded
        elif primitive.data_type in [PrimitiveType.int8, PrimitiveType.int16, PrimitiveType.int32, PrimitiveType.int64,
                                     PrimitiveType.unsigned_int8, PrimitiveType.unsigned_int16,
                                     PrimitiveType.unsigned_int32, PrimitiveType.unsigned_int64, PrimitiveType.half]:
            to_bytes = self.to_int_byte
        elif primitive.data_type in [PrimitiveType.string]:
            to_bytes = self.to_string_byte
        elif primitive.data_type in [PrimitiveType.ref]:
            # TODO: References not implemented yet!
            to_bytes = None
        else:
            raise TypeError("Encountered unknown primitive type.")

        if len(primitive.data) == 0:
            text += B"{ }"
        elif len(primitive.data) == 1:
            if primitive.vector_size == 0:
                text += B"{" + to_bytes(primitive.data[0]) + B"}"
            else:
                text += B"{ {" + (B", ".join(map(to_bytes, primitive.data[0]))) + B"} }"
        else:
            text += B"\n" + self.indent + B"{\n"
            self.inc_indent()

            if primitive.vector_size == 0:
                text += self.indent + (B", ".join(primitive.data)) + B"}\n"
            else:
                text += self.indent + B"{" + (B"}, {".join(B",".join(map(to_bytes, vec)) for vec in primitive.data)) \
                        + B"}\n"

            self.dec_indent()
            text += self.indent + B"}\n"

        return text

    def structure_as_text(self, structure):
        text = self.indent + structure.identifier + B" "

        if structure.name:
            text += structure.name + B" "

        if len(structure.properties) != 0:
            text += B"(" + B", ".join(self.property_as_text(prop) for prop in structure.properties.items()) + B") "

        if structure.is_simple_structure():
            text += B"{" + self.primitive_as_text(structure.structures[0], True) + B"}\n"
        else:
            text += B"\n" + self.indent + B"{\n"

            self.inc_indent()
            for sub in structure.structures:
                if isinstance(sub, DdlPrimitive):
                    text += self.primitive_as_text(sub)
                else:
                    text += self.structure_as_text(sub)
            self.dec_indent()

            text += self.indent + B"}\n"

        return text

# Space reserved for a specification based OpenDdlBinaryWriter ;)
# Hope there will be some specification for it some day.
