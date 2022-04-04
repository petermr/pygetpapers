import json
import logging
import os
import time

import requests

from pygetpapers.download_tools import DownloadTools
from pygetpapers.repositoryinterface import RepositoryInterface

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


class Rxivist(RepositoryInterface):
    """Rxivist wrapper for biorxiv and medrxiv
    
    From the site (rxivist.org):
    "Rxivist combines biology preprints from bioRxiv and medRxiv with data from Twitter
    to help you find the papers being discussed in your field."
    
    Appears to be metadata-only. To get full-text you may have to submit the IDs to biorxiv or medrxiv
    or EPMC as this aggregates preprints.
    """

    def __init__(self):
        self.download_tools = DownloadTools(RXIVIST)
        self.get_url = self.download_tools.query_url

    def rxivist(self,
                query,
                size,
                update=None,
                makecsv=False,
                makexml=False,
                makehtml=False, ):
 
        
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
            self.download_tools._add_download_status_keys(
                paper, json_return_dict)
        result_dict = self.download_tools.adds_new_results_to_metadata_dictionary(
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
       
        
        result_dict = self.rxivist(
            query,
            size,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_metadata_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], paper_key=DOI,
            name_of_file=RXIVIST_RESULT
        )

    def apipaperdownload(self, query_namespace):
        
        self.download_and_save_results(
            query_namespace["query"],
            query_namespace["limit"],
            update=None,
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            makehtml=query_namespace["makehtml"],
        )

    def update(self, query_namespace):
        
        update_file_path = self.download_tools.get_metadata_results_file()
        logging.info(
            "Please ensure that you are providing the same --api as the one in the corpus or you "
            "may get errors")
        self.rxivist_update(
            query_namespace["query"],
            query_namespace["limit"],
            update=update_file_path,
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            makehtml=query_namespace["makehtml"],
        )

    def noexecute(self, query_namespace):
       
        result_dict = self.rxivist(query_namespace.query, size=10)
        results = result_dict[NEW_RESULTS]
        totalhits = results[TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)
