import logging
import os
from pathlib import Path

from habanero import Crossref

from pygetpapers.download_tools import DownloadTools
from pygetpapers.repositoryinterface import (
    XML2HTML_CONVERTER,
    XML2HTML_SUPPORTED,
    RepositoryInterface,
)

# File naming constants
crossref_file_name = "crossref_result"

# Dictionary key constants
DOI = "DOI"
UPDATED_DICT = "updated_dict"
NEW_RESULTS = "new_results"
TOTAL_HITS = "total_hits"
ITEMS = "items"
MESSAGE = "message"
raw_crossref_metadata = "raw_crossref_metadata"
TOTAL_JSON_OUTPUT = "total_json_output"
NEXT_CURSOR = "next-cursor"
TOTAL_RESULTS = "total-results"
CURSOR_MARK = "cursor_mark"
CROSSREF = "crossref"

# Configuration constants
CONFIG_SECTION_CROSSREF = "crossref"
CONFIG_FALLBACK_FALSE = "false"
CONFIG_FALLBACK_TRUE = "true"
CONFIG_FALLBACK_EMPTY = ""

# File extension constants
XML_EXTENSION = ".xml"
XML_HTML_EXTENSION = ".xml.html"

# API configuration constants
DEFAULT_CURSOR = "*"
DEFAULT_CUTOFF_SIZE = 10
CONTACT_EMAIL = "ayushgarg@science.org.in"
USER_AGENT_PREFIX = "pygetpapers/version@"

# Logging message constants
LOG_MAKING_REQUEST = "Making request to crossref"
LOG_READING_OLD_JSON = "Reading old json metadata file"
LOG_TOTAL_HITS_TEMPLATE = "Total number of hits for the query are %s"
LOG_XML_TO_HTML_SUCCESS_TEMPLATE = (
    "Converted XML to HTML using Simple HTML Converter for {}"
)
LOG_XML_TO_HTML_FAILURE_TEMPLATE = "Failed to convert XML to HTML for {}: {}"
LOG_XML_TO_HTML_ERROR_TEMPLATE = "Error converting XML to HTML for {}: {}"


class CrossRef(RepositoryInterface):
    """CrossRef class which handles crossref repository. It uses habanero repository
    wrapper to make its query"""

    def __init__(self):

        self.download_tools = DownloadTools(CROSSREF)
        self.xml2html_supported = (
            self.download_tools.config.get(
                CONFIG_SECTION_CROSSREF,
                XML2HTML_SUPPORTED,
                fallback=CONFIG_FALLBACK_FALSE,
            ).lower()
            == CONFIG_FALLBACK_TRUE
        )
        self.xml2html_converters = self.download_tools.config.get(
            CONFIG_SECTION_CROSSREF, XML2HTML_CONVERTER, fallback=CONFIG_FALLBACK_EMPTY
        ).split(",")

    def supports_xml2html(self) -> bool:
        """Check if this repository supports XML to HTML conversion.

        :return: True if XML2HTML is supported, False otherwise
        :rtype: bool
        """
        return self.xml2html_supported

    def get_xml2html_converters(self) -> list:
        """Get list of available XML to HTML converters for this repository.

        :return: List of converter names (e.g., ['simple_html'])
        :rtype: list
        """
        return [
            converter.strip()
            for converter in self.xml2html_converters
            if converter.strip()
        ]

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
        if not self.supports_xml2html():
            return False

        try:
            # Use Simple HTML Converter for Crossref XML
            from src.pygetpapers.simple_html_converter import SimpleHTMLConverter

            converter = SimpleHTMLConverter()
            # Use XML-to-HTML naming convention: fulltext.xml.html
            html_file_path = xml_file_path.replace(XML_EXTENSION, XML_HTML_EXTENSION)

            success, result = converter.convert_xml_to_html(
                xml_file_path, html_file_path
            )

            if success:
                logging.info(
                    LOG_XML_TO_HTML_SUCCESS_TEMPLATE.format(identifier_for_paper)
                )
                return True
            else:
                logging.warning(
                    LOG_XML_TO_HTML_FAILURE_TEMPLATE.format(
                        identifier_for_paper, result
                    )
                )

        except Exception as e:
            logging.error(
                LOG_XML_TO_HTML_ERROR_TEMPLATE.format(identifier_for_paper, e)
            )

        return False

    def crossref(
        self,
        query,
        cutoff_size,
        filter_dict=None,
        update=None,
        makecsv=False,
        makexml=False,
        makehtml=False,
    ):
        """Builds the crossref searcher and writes the xml, csv and html

        :param query: query given to crossref
        :type query: string
        :param cutoff_size: number of papers to retrieve
        :type cutoff_size: int
        :param filter_dict: filters for crossref search
        :type filter_dict: bool, optional
        :param makecsv: whether to get csv
        :type makecsv: bool
        :param makehtml: whether to get html
        :type makehtml: bool
        :param makexml: whether to get xml
        :type makexml: bool
        :param update: dictionary containing results from previous run of pygetpapers
        :type update: dict
        :return: dictionary of results retrieved from crossref
        :rtype: dict
        """
        crossref_client = self.initiate_crossref()
        logging.info(LOG_MAKING_REQUEST)

        if update:
            cursor = update[CURSOR_MARK]
        else:
            cursor = DEFAULT_CURSOR
        # Submits a request to crossref
        # raw_crossref_metadata is a dictionary containing bibliographic metadata
        # for each paper
        raw_crossref_metadata = crossref_client.works(
            query={query}, filter=filter_dict, cursor_max=cutoff_size, cursor=cursor
        )
        metadata_count = raw_crossref_metadata[MESSAGE][TOTAL_RESULTS]
        cursor_mark = raw_crossref_metadata[MESSAGE][NEXT_CURSOR]
        cutoff_metadata_list = self._make_metadata_subset(
            raw_crossref_metadata, cutoff_size
        )
        cutoff_metadata_dictionary = self.download_tools._make_dict_from_list(
            cutoff_metadata_list, paper_key=DOI
        )
        for paper in cutoff_metadata_dictionary:
            self.download_tools._add_download_status_keys(
                paper, cutoff_metadata_dictionary
            )
        result_dict = self.download_tools._adds_new_results_to_metadata_dictionary(
            cursor_mark, cutoff_metadata_dictionary, metadata_count, update
        )
        metadata_dictionary = result_dict[NEW_RESULTS][TOTAL_JSON_OUTPUT]
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv, makehtml, makexml, metadata_dictionary, crossref_file_name
        )
        return result_dict

    def _make_metadata_subset(self, crossref_client, cutoff_size):

        total_metadata_list = crossref_client[MESSAGE][ITEMS]
        total_metadata_list = total_metadata_list[:cutoff_size]
        return total_metadata_list

    def initiate_crossref(self):
        """Initate habanero wrapper for crossref

        :return: crossref object
        """
        cr = Crossref()
        Crossref(mailto=CONTACT_EMAIL)
        version = self.download_tools.get_version()
        Crossref(ua_string=f"{USER_AGENT_PREFIX}{version}")
        return cr

    def update(self, query_namespace):

        logging.info(LOG_READING_OLD_JSON)
        update_path = self.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        update = self.download_tools.readjsondata(update_path)
        result_dict = self.crossref(
            query_namespace["query"],
            query_namespace["limit"],
            filter_dict=query_namespace["filter"],
            update=update,
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            makehtml=query_namespace["makehtml"],
        )
        self.download_tools._make_metadata_json_files_for_paper(
            result_dict[NEW_RESULTS],
            updated_dict=result_dict[UPDATED_DICT],
            paper_key=DOI,
            name_of_file=crossref_file_name,
        )

    def noexecute(self, query_namespace):

        query = query_namespace["query"]
        filter_dict = query_namespace["filter"]
        result_dict = self.crossref(
            query, cutoff_size=DEFAULT_CUTOFF_SIZE, filter_dict=filter_dict
        )
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info(LOG_TOTAL_HITS_TEMPLATE, totalhits)

    def apipaperdownload(self, query_namespace):

        result_dict = self.crossref(
            query_namespace["query"],
            query_namespace["limit"],
            filter_dict=query_namespace["filter"],
            update=None,
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            makehtml=query_namespace["makehtml"],
        )
        self.download_tools._make_metadata_json_files_for_paper(
            result_dict[NEW_RESULTS],
            updated_dict=result_dict[UPDATED_DICT],
            paper_key=DOI,
            name_of_file=crossref_file_name,
        )
