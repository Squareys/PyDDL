from abc import abstractmethod
import math
from enum import Enum

__author__ = "Jonathan Hale"
__version__ = "0.1.0"


class DdlPrimitiveDataType(Enum):
    """
    Enum for primitive structure data types.

    For convenience use `import DdlPrimitiveDataType from pyddl as DataType`
    for example.
    """
    bool = 0
    int8 = 1
    int16 = 2
    int32 = 3
    int64 = 4
    unsigned_int8 = 5
    unsigned_int16 = 6
    unsigned_int32 = 7
    unsigned_int64 = 8
    half = 9
    float = 10
    double = 11
    string = 12
    ref = 13
    type = 14


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

    def __init__(self, identifier, name=None, children=[], props=dict()):
        """
        Constructor
        :param identifier: structure identifier
        :param name: optional name
        :param children: list of substructures
        """
        self.children = children
        self.properties = props
        self.identifier = identifier
        self.name = name if name != "" else None

    def is_simple_structure(self):
        """
        A structure is simple if it contains exactly one primitive and has no properties or name.
        :return: true if this structure is simple
        """
        if len(self.children) != 1:
            # a simple structure may contain only one primitive substructure
            return False
        if len(self.properties) != 0:
            # a simple structure does not have properties
            return False
        if self.name is not None:
            # simple children don't have a name
            return False
        if not isinstance(self.children[0], DdlPrimitive):
            # the only substructure needs to be a primitive
            return False

        return self.children[0].is_simple_primitive()

    def add_structure(self, identifier, name, children, props=dict()):
        """
        Add a substructure
        :param identifier: structure identifier
        :param name: optional name
        :param children: list of substructures or primitives
        :param props: dict of properties
        :return: the created structure
        """
        s = DdlStructure(identifier, name, children, props)
        self.children.append(s)
        return s

    def add_primitive(self, data_type, data, name=None, vector_size=0):
        """
        Add a primitive substructure
        :param data_type: primitive data type (see pyddl.enum.PrimitiveType)
        :param data: list of values. If vector_size != 0, the list should contain tuples
        :param name: name of the primitive structure
        :param vector_size: size of the contained vectors
        :return: self (for method chaining)
        """
        self.children.append(DdlPrimitive(data_type, data, name, vector_size))
        return self


class DdlDocument:
    """
    An OpenDDL document.
    """

    def __init__(self):
        self.structures = []

    def add_structure(self, identifier, name=None, children=[], props=dict()):
        """
        Add a substructure
        :param identifier: structure identifier
        :param name: optional name
        :param children: list of substructures and primitives
        :param props: dict of properties
        :return: the created structure
        """
        s = DdlStructure(identifier, name, children, props)
        self.structures.append(s)
        return s


class DdlWriter:
    """
    Abstract class for classes responsible for writing OpenDdlDocuments.
    """

    def __init__(self, document):
        """
        Constructor
        :param document: document to write
        """
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
        :param filename: path to a file to write to
        :return: nothing
        """
        pass


class DdlTextWriter(DdlWriter):
    """
    OpenDdlWriter which writes OpenDdlDocuments in human-readable text form.
    """

    def __init__(self, document, rounding=6):
        """
        Constructor
        :param document: document to write
        :param rounding: number of decimal places to keep or None to keep all
        """
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

    @staticmethod
    def to_ref_byte(structure):
        return B"$" + structure.name

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
        """
        Create a text representation for a key-value-pair. E.g.: "key = value".
        :param prop: a pair to represent as text
        :return: a byte-string in the form "key = value"
        """
        value = prop[1]
        if isinstance(value, bool):
            value_bytes = self.to_bool_byte(value)
        elif isinstance(value, int):
            value_bytes = self.to_int_byte(value)
        elif isinstance(value, float):
            value_bytes = self.to_float_byte(value)
        elif isinstance(value, str):
            value_bytes = B"\"" + bytes(value, "UTF-8") + B"\""
        else:
            raise TypeError("ERROR: Unknown property type for property \"{}\"".format(prop[0]))

        return prop[0] + B" = " + value_bytes

    def primitive_as_text(self, primitive, no_indent=False):
        """
        Get a text representation of the given primitive structure
        :param primitive: primitive structure to get the text representation for
        :param no_indent: if true will skip adding the first indent
        :return: a byte string representing the primitive structure
        """
        text = (B"" if no_indent else self.indent) + bytes(primitive.data_type.name, "UTF-8")

        if primitive.vector_size > 0:
            text += B"[" + self.to_int_byte(primitive.vector_size) + B"]"

        if primitive.name is not None:
            text += B" $" + primitive.name + B" "

        # find appropriate conversion function
        if primitive.data_type in [DdlPrimitiveDataType.bool]:
            # bool
            to_bytes = self.to_bool_byte
        elif primitive.data_type in [DdlPrimitiveDataType.double, DdlPrimitiveDataType.float]:
            # float/double
            to_bytes = self.to_float_byte if self.rounding is None else self.to_float_byte_rounded
        elif primitive.data_type in [DdlPrimitiveDataType.int8, DdlPrimitiveDataType.int16, DdlPrimitiveDataType.int32, DdlPrimitiveDataType.int64,
                                     DdlPrimitiveDataType.unsigned_int8, DdlPrimitiveDataType.unsigned_int16,
                                     DdlPrimitiveDataType.unsigned_int32, DdlPrimitiveDataType.unsigned_int64, DdlPrimitiveDataType.half]:
            # integer types
            to_bytes = self.to_int_byte
        elif primitive.data_type in [DdlPrimitiveDataType.string]:
            # string
            to_bytes = self.to_string_byte
        elif primitive.data_type in [DdlPrimitiveDataType.ref]:
            to_bytes = self.to_ref_byte
        else:
            raise TypeError("Encountered unknown primitive type.")

        if len(primitive.data) == 0:
            text += B" { }"
        elif len(primitive.data) == 1:
            if primitive.vector_size == 0:
                text += B" {" + to_bytes(primitive.data[0]) + B"}"
            else:
                text += B" { {" + (B", ".join(map(to_bytes, primitive.data[0]))) + B"} }"
        else:
            text += B"\n" + self.indent + B"{\n"
            self.inc_indent()

            if primitive.vector_size == 0:
                if hasattr(primitive, 'max_elements_per_line'):
                    n = primitive.max_elements_per_line
                    data = primitive.data
                    text += self.indent + ((B",\n" + self.indent).join(
                        [B", ".join(group) for group in
                         [map(to_bytes, data[i:i + n]) for i in range(0, len(data), n)]])) + B"\n"
                else:
                    text += self.indent + (B", ".join(map(to_bytes, primitive.data))) + B"\n"
            else:
                if hasattr(primitive, 'max_elements_per_line'):
                    n = primitive.max_elements_per_line
                    data = primitive.data
                    text += self.indent + B"{" + ((B"},\n" + self.indent + B"{").join(
                        [B"}, {".join(B", ".join(map(to_bytes, vec)) for vec in group) for group in
                         [data[i:i + n] for i in range(0, len(data), n)]])) + B"}\n"
                else:
                    text += self.indent + B"{" + (B"}, {".join(
                        B", ".join(map(to_bytes, vec)) for vec in primitive.data)) + B"}\n"

            self.dec_indent()
            text += self.indent + B"}\n"

        return text

    def structure_as_text(self, structure):
        """
        Get a text representation of the given structure
        :param structure: structure to get the text representation for
        :return: a byte string representing the structure
        """
        text = self.indent + structure.identifier

        if structure.name:
            text += B" $" + structure.name

        if len(structure.properties) != 0:
            text += B" (" + B", ".join(self.property_as_text(prop) for prop in structure.properties.items()) + B")"

        if structure.is_simple_structure():
            text += B" {" + self.primitive_as_text(structure.children[0], True) + B"}\n"
        else:
            text += B"\n" + self.indent + B"{\n"

            self.inc_indent()
            for sub in structure.children:
                if isinstance(sub, DdlPrimitive):
                    text += self.primitive_as_text(sub)
                else:
                    text += self.structure_as_text(sub)
            self.dec_indent()

            text += self.indent + B"}\n"

        return text

    @staticmethod
    def set_max_elements_per_line(primitive, elements):
        """
        Set how many elements should be displayed per line for a primitive structure.
        :param primitive: the primitive
        :param elements: max amount of elements per line
        """
        if isinstance(primitive, DdlPrimitive):
            primitive.max_elements_per_line = elements
        else:
            raise TypeError("max_elements_per_line can only be set for DdlPrimitive")


# Space reserved for a specification based OpenDdlBinaryWriter ;)
# Hope there will be some specification for it some day.
