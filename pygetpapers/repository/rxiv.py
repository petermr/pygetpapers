import json
import logging
import os
import time

import requests
from tqdm import tqdm

from pygetpapers.download_tools import DownloadTools
from pygetpapers.pgexceptions import PygetpapersError
from pygetpapers.repositoryinterface import RepositoryInterface

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
DATE_OR_NUMBER_OF_PAPERS = "date_or_number_of_papers"


class Rxiv(RepositoryInterface):
    """Biorxiv and Medrxiv repositories
    
    At present (2022-03) the API appears only to support date searches. 
    The `rxivist` system is layered on top and supports fuller queries

"""

    def __init__(self,api="biorxiv"):
        """initiate Rxiv class"""
        self.download_tools = DownloadTools(api)
        self.doi_done = []

    def rxiv(
            self,
            query,
            cutoff_size,
            source=BIORXIV,
            update=None,
            makecsv=False,
            makehtml=False,
    ):
        
        if update:
            cursor_mark = update[CURSOR_MARK]
        else:
            cursor_mark = 0
        total_number_of_results = 0
        total_papers_list = []
        logging.info("Making Request to rxiv")
        while len(total_papers_list) <= cutoff_size:
            total_number_of_results, total_papers_list, papers_list = self.make_request_add_papers(
                query,
                cursor_mark,
                source,
                total_number_of_results,
                total_papers_list,
            )
            if len(papers_list) == 0:
                logging.warning("No more papers found")
                break
            cursor_mark += 1
        total_result_list = total_papers_list[:cutoff_size]
        json_metadata_dictionary = self.download_tools._make_dict_from_list(
            total_result_list, paper_key=DOI
        )
        for paper in json_metadata_dictionary:
            self.download_tools._add_download_status_keys(
                paper, json_metadata_dictionary)
        result_dict = self.download_tools._adds_new_results_to_metadata_dictionary(
            cursor_mark, json_metadata_dictionary, total_number_of_results, update=update)

        metadata_dictionary = result_dict[NEW_RESULTS][TOTAL_JSON_OUTPUT]
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv=makecsv,
            makehtml=makehtml,
            makexml=False,
            metadata_dictionary=metadata_dictionary,
            name=RXIV_RESULT,
        )
        return result_dict

    def make_request_add_papers(
            self, interval, cursor_mark, source, total_number_of_results, total_papers_list
    ):
        print("interval",interval)
        self.make_request_url_for_rxiv(cursor_mark, interval, source)
        request_handler = self.download_tools.post_query(self.get_url)
        request_dict = json.loads(request_handler.text)
        papers_list = request_dict[COLLECTION]
        final_list = []
        for paper in papers_list:
            if paper[DOI] not in self.doi_done:
                final_list.append(paper)
                self.doi_done.append(paper[DOI])
        if TOTAL in request_dict[MESSAGES][0]:
            total_number_of_results = request_dict[MESSAGES][0][TOTAL]
        total_papers_list += final_list
        return total_number_of_results, total_papers_list, final_list

    def make_request_url_for_rxiv(self, cursor_mark, interval, source):
        print(interval)
        if type(interval) == int:
            self.get_url = "https://api.biorxiv.org/details/{source}/{interval}".format(
                source=source, interval=interval
            )
        else:
            self.get_url = self.download_tools.query_url.format(
                source=source, interval=interval, cursor=cursor_mark
            )

    def rxiv_update(
            self,
            interval,
            cutoff_size,
            source=BIORXIV,
            update=None,
            makecsv=False,
            makexml=False,
            makehtml=False,
    ):
        
        os.chdir(os.path.dirname(update))
        update = self.download_tools.readjsondata(update)
        logging.info("Reading old json metadata file")
        self.download_and_save_results(
            interval,
            cutoff_size,
            update=update,
            source=source,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )

    def download_and_save_results(
            self,
            query,
            cutoff_size,
            source,
            update=False,
            makecsv=False,
            makexml=False,
            makehtml=False,
    ):
        
        if update and type(query) == int:
            raise PygetpapersError("Update will not work if date not provided")

        result_dict = self.rxiv(
            query,
            cutoff_size,
            update=update,
            source=source,
            makecsv=makecsv,
            makehtml=makehtml,
        )
        if makexml:
            logging.info("Making xml for paper")
            dict_of_papers = result_dict[NEW_RESULTS][TOTAL_JSON_OUTPUT]
            self.make_xml_for_rxiv(
                dict_of_papers, JATSXML, DOI, FULLTEXT_XML)
        self.download_tools._make_metadata_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], paper_key=DOI,
            name_of_file=RXIV_RESULT
        )

    def make_xml_for_rxiv(
            self, dict_of_papers, xml_identifier, paper_id_identifier, filename
    ):

        for paper in tqdm(dict_of_papers):
            dict_of_paper = dict_of_papers[paper]
            xml_url = dict_of_paper[xml_identifier]
            doi_of_paper = dict_of_paper[paper_id_identifier]
            url_encoded_doi_of_paper = self.download_tools.url_encode_id(
                doi_of_paper)
            self.download_tools.check_or_make_directory(
                url_encoded_doi_of_paper)
            path_to_save_xml = os.path.join(
                str(os.getcwd()), url_encoded_doi_of_paper, filename
            )
            self.download_tools.queries_the_url_and_writes_response_to_destination(
                xml_url, path_to_save_xml)

    def noexecute(self, query_namespace):
        
        time_interval = query_namespace["query"]
        source = query_namespace["api"]
        result_dict = self.rxiv(
            time_interval, cutoff_size=10, source=source)
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)

    def update(self, query_namespace):
        
        update_file_path = self.download_tools.get_metadata_results_file()
        logging.info(
            "Please ensure that you are providing the same --api as the one in the corpus or you "
            "may get errors")
        self.rxiv_update(
            query_namespace["query"],
            query_namespace["limit"],
            source=query_namespace["api"],
            update=update_file_path,
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            makehtml=query_namespace["makehtml"],
        )

    def apipaperdownload(self, query_namespace):
        
        self.download_and_save_results(
            query_namespace["query"],
            query_namespace["limit"],
            query_namespace["api"],
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            makehtml=query_namespace["makehtml"],
        )
