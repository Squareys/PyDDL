from abc import abstractmethod

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

    def __init__(self, name):
        self.structures = []
        self.properties = dict()
        self.name = name


class DdlDocument:
    """
    An OpenDDL document.
    """

    def __init__(self):
        self.structures = []


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

    def __init__(self, document):
        DdlWriter.__init__(self, document)

    def write(self, filename):
        # TODO: not implemented yet!
        pass


# Space reserved for a specification based OpenDdlBinaryWriter ;)
# Hope there will be some specification for it some day.
