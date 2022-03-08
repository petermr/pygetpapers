import logging
import os

from habanero import Crossref

from pygetpapers.download_tools import DownloadTools
from pygetpapers.pgexceptions import PygetpapersError
from pygetpapers.repositoryinterface import RepositoryInterface
crossref_file_name = "crossref_result"

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


class CrossRef(RepositoryInterface):
    """CrossRef class which handles crossref repository"""

    def __init__(self):
        
        self.download_tools = DownloadTools(CROSSREF)

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
        logging.info("Making request to crossref")

        if update:
            cursor = update[CURSOR_MARK]
        else:
            cursor = "*"
        # Submits a request to crossref
        # raw_crossref_metadata is a dictionary containing bibliographic metadata for each paper
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
                paper, cutoff_metadata_dictionary)
        result_dict = self.download_tools._adds_new_results_to_metadata_dictionary(
            cursor_mark, cutoff_metadata_dictionary, metadata_count, update
        )
        metadata_dictionary = result_dict[NEW_RESULTS][TOTAL_JSON_OUTPUT]
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv, makehtml, makexml, metadata_dictionary, raw_crossref_metadata
        )
        return result_dict

    def _make_metadata_subset(self,crossref_client, cutoff_size):
        
        total_metadata_list = crossref_client[MESSAGE][ITEMS]
        total_metadata_list = total_metadata_list[:cutoff_size]
        return total_metadata_list

    def initiate_crossref(self):
        """Initate habanero wrapper for crossref

        :return: crossref object
        """
        cr = Crossref()
        Crossref(mailto="ayushgarg@science.org.in")
        version = self.download_tools.get_version()
        Crossref(ua_string=f"pygetpapers/version@{version}")
        return cr

    def update(
        self,
        query_namespace
    ):

        logging.info("Reading old json metadata file")
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
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], paper_key=DOI,
            name_of_file=crossref_file_name
        )

    def noexecute(self, query_namespace):
 
        query = query_namespace["query"]
        filter_dict = query_namespace["filter"]
        result_dict = self.crossref(
            query, cutoff_size=10, filter_dict=filter_dict
        )
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)

    def apipaperdownload(
        self,
        query_namespace
    ):

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
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], paper_key=DOI, name_of_file=crossref_file_name
        )
        