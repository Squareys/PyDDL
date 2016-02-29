from abc import abstractmethod

__author__ = "Jonathan Hale"


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
