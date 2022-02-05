import logging
import os

from habanero import Crossref

from pygetpapers.download_tools import DownloadTools
from pygetpapers.pgexceptions import PygetpapersError

raw_crossref_metadataS = "raw_crossref_metadata"

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


class CrossRef:
    """CrossRef class which handles crossref repository"""

    def __init__(self):
        """[summary]
        """
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
        """[summary]

        :param query: [description]
        :type query: [type]
        :param cutoff_size: [description]
        :type cutoff_size: [type]
        :param filter_dict: [description], defaults to None
        :type filter_dict: [type], optional
        :param update: [description], defaults to None
        :type update: [type], optional
        :param makecsv: [description], defaults to False
        :type makecsv: bool, optional
        :param makexml: [description], defaults to False
        :type makexml: bool, optional
        :param makehtml: [description], defaults to False
        :type makehtml: bool, optional
        :return: [description]
        :rtype: [type]
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
        cutoff_metadata_list = self.make_metadata_subset(
            raw_crossref_metadata, cutoff_size
        )
        cutoff_metadata_dictionary = self.download_tools.make_dict_from_list(
            cutoff_metadata_list, paper_key=DOI
        )
        for paper in cutoff_metadata_dictionary:
            self.download_tools.add_download_status_keys(
                paper, cutoff_metadata_dictionary)
        result_dict = self.download_tools.make_dict_to_return(
            cursor_mark, cutoff_metadata_dictionary, metadata_count, update
        )
        return_dict = result_dict[NEW_RESULTS][TOTAL_JSON_OUTPUT]
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv, makehtml, makexml, return_dict, raw_crossref_metadata
        )
        return result_dict

    @staticmethod
    def make_metadata_subset(crossref_client, cutoff_size):
        """[summary]

        :param crossref_client: [description]
        :type crossref_client: [type]
        :param cutoff_size: [description]
        :type cutoff_size: [type]
        :return: [description]
        :rtype: [type]
        """
        total_metadata_list = crossref_client[MESSAGE][ITEMS]
        total_metadata_list = total_metadata_list[:cutoff_size]
        return total_metadata_list

    def initiate_crossref(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        cr = Crossref()
        Crossref(mailto="ayushgarg@science.org.in")
        version = self.download_tools.get_version()
        Crossref(ua_string=f"pygetpapers/version@{version}")
        return cr

    def update(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        logging.info("Reading old json metadata file")
        update_path = self.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        update = self.download_tools.readjsondata(update_path)
        query = args.query
        cutoff_size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            cutoff_size,
            filter_dict=filter_dict,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], paper_key=DOI,
            name_of_file=raw_crossref_metadataS
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        filter_dict = args.filter
        result_dict = self.crossref(
            query, cutoff_size=10, filter_dict=filter_dict
        )
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)

    def apipaperdownload(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        cutoff_size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            cutoff_size,
            filter_dict=filter_dict,
            update=None,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], paper_key=DOI, name_of_file=raw_crossref_metadataS
        )
        