from abc import ABC, abstractmethod

TOTAL_HITS = "total_hits"
NEW_RESULTS = "new_results"
RXIV_RESULT = "rxiv_result"
UPDATED_DICT = "updated_dict"
JATSXML = "jatsxml"
FULLTEXT_XML = "fulltext.xml"
DOI = "doi"
TOTAL_JSON_OUTPUT = "total_json_output"
BIORXIV = "biorxiv"
MESSAGES = "messages"
TOTAL = "total"
COLLECTION = "collection"
CURSOR_MARK = "cursor_mark"
RXIV = "rxiv"

# XML2HTML support constants
XML2HTML_SUPPORTED = "xml2html_supported"
XML2HTML_CONVERTER = "xml2html_converter"
FULLTEXT_HTML = "fulltext_html"


class RepositoryInterface(ABC):

    def __init__(self) -> None:
        super().__init__()
        self.metadata_dictionary = dict()

    @abstractmethod
    def noexecute(self, query_namespace):
        """Takes in the query_namespace object as the parameter and runs the query
        search for given search parameters but only prints the output and not write
        to disk.

        :param query_namespace: pygetpaper's namespace object containing the queries
        from argparse
        :type query_namespace: dict
        """

    @abstractmethod
    def update(self, query_namespace):
        """If there is a previously existing corpus, this function reads in the
        'cursor mark' from the previous run, increments in, and adds new papers
        for the given parameters to the existing corpus.

        :param query_namespace: pygetpaper's namespace object containing the queries
        from argparse
        :type query_namespace: dict
        """

    @abstractmethod
    def apipaperdownload(self, query_namespace):
        """Takes in the query_namespace object as the parameter and runs the query
        search for given search parameters.

        :param query_namespace: pygetpaper's namespace object containing the queries
        from argparse
        :type query_namespace: dict
        """

    def supports_xml2html(self) -> bool:
        """Check if this repository supports XML to HTML conversion.

        :return: True if XML2HTML is supported, False otherwise
        :rtype: bool
        """
        return False

    def get_xml2html_converters(self) -> list:
        """Get list of available XML to HTML converters for this repository.

        :return: List of converter names (e.g., ['jats4r', 'simple_html'])
        :rtype: list
        """
        return []

    def convert_xml_to_html(
        self, xml_file_path: str, identifier_for_paper: str
    ) -> bool:
        """Convert XML file to HTML using available converters.

        :param xml_file_path: Path to XML file
        :type xml_file_path: str
        :param identifier_for_paper: Paper identifier
        :type identifier_for_paper: str
        :return: True if conversion was successful, False otherwise
        :rtype: bool
        """
        return False
