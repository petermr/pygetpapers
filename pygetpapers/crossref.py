import logging
import os

from habanero import Crossref

from pygetpapers.download_tools import DownloadTools
from pygetpapers.pgexceptions import PygetpapersError

CROSSREF_RESULTS = "crossref_result"

DOI = "DOI"

UPDATED_DICT = "updated_dict"

NEW_RESULTS = "new_results"

TOTAL_HITS = "total_hits"

ITEMS = "items"

MESSAGE = "message"

CROSSREF_RESULT = "crossref_result"

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
        size,
        filter_dict=None,
        update=None,
        makecsv=False,
        makexml=False,
        makehtml=False,
    ):
        """[summary]

        :param query: [description]
        :type query: [type]
        :param size: [description]
        :type size: [type]
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
        crossref_result = crossref_client.works(
            query={query}, filter=filter_dict, cursor_max=size, cursor=cursor
        )
        doi_list = []
        logging.info("Got request result from crossref")
        for item in crossref_result[MESSAGE][ITEMS]:
            doi_list.append(item[DOI])
        logging.debug("Added DOIs to a list")
        total_number_of_results = crossref_result[MESSAGE][TOTAL_RESULTS]
        cursor_mark = crossref_result[MESSAGE][NEXT_CURSOR]
        total_result_list = self.make_list_of_required_size_from_crossref_result(
            crossref_result, size
        )
        json_return_dict = self.download_tools.make_dict_from_returned_list(
            total_result_list, key_in_dict=DOI
        )
        for paper in json_return_dict:
            self.download_tools.add_keys_for_conditions(
                paper, json_return_dict)
        result_dict = self.download_tools.make_dict_to_return(
            cursor_mark, json_return_dict, total_number_of_results, update
        )
        return_dict = result_dict[NEW_RESULTS][TOTAL_JSON_OUTPUT]
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv, makehtml, makexml, return_dict, CROSSREF_RESULT
        )
        return result_dict

    @staticmethod
    def make_list_of_required_size_from_crossref_result(crossref_client, size):
        """[summary]

        :param crossref_client: [description]
        :type crossref_client: [type]
        :param size: [description]
        :type size: [type]
        :return: [description]
        :rtype: [type]
        """
        total_result_list = crossref_client[MESSAGE][ITEMS]
        total_result_list = total_result_list[:size]
        return total_result_list

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
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI,
            name_of_file=CROSSREF_RESULTS
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        filter_dict = args.filter
        result_dict = self.crossref(
            query, size=10, filter_dict=filter_dict
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
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=None,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI, name_of_file=CROSSREF_RESULTS
        )
