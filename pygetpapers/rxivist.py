import json
import logging
import os
import time

import requests

from pygetpapers.download_tools import DownloadTools

TOTAL_HITS = "total_hits"

NEW_RESULTS = "new_results"

UPDATED_DICT = "updated_dict"

RXIVIST_RESULT = "rxivist-result"

DOI = "doi"

QUERY = "query"

TOTAL_RESULTS = "total_results"

RESULTS = "results"

TOTAL_JSON_OUTPUT = "total_json_output"

CURSOR_MARK = "cursor_mark"

RXIVIST = "rxivist"


class Rxivist:
    """Rxivist class which handles the rxivist wrapper"""

    def __init__(self):
        """initiate Rxivist class"""
        self.download_tools = DownloadTools(RXIVIST)
        self.get_url = self.download_tools.query_url

    def rxivist(self,
                query,
                size,
                update=None,
                makecsv=False,
                makexml=False,
                makehtml=False, ):
        """[summary]

        :param query: [description]
        :type query: [type]
        :param size: [description]
        :type size: [type]
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
        
        if update:
            cursor_mark = update[CURSOR_MARK]
        else:
            cursor_mark = 0
        total_number_of_results = size
        total_papers_list = []
        logging.info("Making Request to rxivist")
        while len(total_papers_list) < size:
            total_number_of_results, total_papers_list, papers_list = self.make_request_add_papers(
                query,
                cursor_mark,
                total_number_of_results,
                total_papers_list,
            )
            cursor_mark += 1
            if len(papers_list) == 0:
                logging.warning("Could not find more papers")
                break

        total_result_list = total_papers_list[:size]
        json_return_dict = self.download_tools.make_dict_from_list(
            total_result_list, paper_key=DOI
        )
        for paper in json_return_dict:
            self.download_tools.add_download_status_keys(
                paper, json_return_dict)
        result_dict = self.download_tools.make_dict_to_return(
            cursor_mark, json_return_dict, total_number_of_results, update=update
        )
        new_dict_to_return = result_dict[NEW_RESULTS]
        return_dict = new_dict_to_return[TOTAL_JSON_OUTPUT]
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv=makecsv,
            makehtml=makehtml,
            makexml=makexml,
            return_dict=return_dict,
            name=RXIVIST_RESULT,
        )
        return result_dict

    def send_post_request(self, query, cursor_mark=0, page_size=20):
        """[summary]

        :param query: [description]
        :type query: [type]
        :param cursor_mark: [description], defaults to 0
        :type cursor_mark: int, optional
        :param page_size: [description], defaults to 20
        :type page_size: int, optional
        :return: [description]
        :rtype: [type]
        """
        
        url_to_request = self.get_url.format(
            query=query, cursor=cursor_mark, page_size=page_size)
        start = time.time()
        request_handler = requests.get(url_to_request)
        stop = time.time()
        logging.debug("*/Got the Query Result */")
        logging.debug("Time elapsed: %s", (stop - start))
        return request_handler

    def make_request_add_papers(
            self, query, cursor_mark, total_number_of_results, total_papers_list
    ):
        """[summary]

        :param query: [description]
        :type query: [type]
        :param cursor_mark: [description]
        :type cursor_mark: [type]
        :param total_number_of_results: [description]
        :type total_number_of_results: [type]
        :param total_papers_list: [description]
        :type total_papers_list: [type]
        :return: [description]
        :rtype: [type]
        """
        request_handler = self.send_post_request(query, cursor_mark)
        request_dict = json.loads(request_handler.text)
        papers_list = request_dict[RESULTS]
        if TOTAL_RESULTS in request_dict[QUERY]:
            total_number_of_results = request_dict[QUERY][TOTAL_RESULTS]
        total_papers_list += papers_list
        return total_number_of_results, total_papers_list, papers_list

    def rxivist_update(
            self,
            query,
            size,
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
        :param update: [description], defaults to None
        :type update: [type], optional
        :param makecsv: [description], defaults to False
        :type makecsv: bool, optional
        :param makexml: [description], defaults to False
        :type makexml: bool, optional
        :param makehtml: [description], defaults to False
        :type makehtml: bool, optional
        """

        os.chdir(os.path.dirname(update))
        update = self.download_tools.readjsondata(update)
        logging.info("Reading old json metadata file")
        self.download_and_save_results(
            query,
            size,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )

    def download_and_save_results(
            self,
            query,
            size,
            update=False,
            makecsv=False,
            makexml=False,
            makehtml=False,
    ):
        """[summary]

        :param query: [description]
        :type query: [type]
        :param size: [description]
        :type size: [type]
        :param update: [description], defaults to False
        :type update: bool, optional
        :param makecsv: [description], defaults to False
        :type makecsv: bool, optional
        :param makexml: [description], defaults to False
        :type makexml: bool, optional
        :param makehtml: [description], defaults to False
        :type makehtml: bool, optional
        """
        
        result_dict = self.rxivist(
            query,
            size,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], paper_key=DOI,
            name_of_file=RXIVIST_RESULT
        )

    def apipaperdownload(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        self.download_and_save_results(
            args.query,
            args.limit,
            makecsv=args.makecsv,
            makexml=args.xml,
            makehtml=args.makehtml,
        )

    def update(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        update_file_path = self.download_tools.get_metadata_results_file()
        logging.info(
            "Please ensure that you are providing the same --api as the one in the corpus or you "
            "may get errors")
        self.rxivist_update(
            args.query,
            args.limit,
            update=update_file_path,
            makecsv=args.makecsv,
            makexml=args.xml,
            makehtml=args.makehtml,
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        result_dict = self.rxivist(args.query, size=10)
        results = result_dict[NEW_RESULTS]
        totalhits = results[TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)
