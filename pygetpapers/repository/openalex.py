import json
import logging
import os
import time

import requests

from pygetpapers.download_tools import DownloadTools
from pygetpapers.repositoryinterface import RepositoryInterface
from tqdm import tqdm

TOTAL_HITS = "total_hits"

NEW_RESULTS = "new_results"

UPDATED_DICT = "updated_dict"

OPENALEX_RESULT = "openalex-result"

DOI = "doi"

QUERY = "query"
FULLTEXT_PDF = "fulltext.pdf"
PDFDOWNLOADED = "pdfdownloaded"

TOTAL_RESULTS = "total_results"

RESULTS = "results"

TOTAL_JSON_OUTPUT = "total_json_output"

CURSOR_MARK = "cursor_mark"

OPENALEX = "openalex"
PDF_URL = "pdf_url"


class OpenAlex(RepositoryInterface):
    """OpenAlex wrapper for accessing OpenAlex API

    OpenAlex is a free and open catalog of the world's scholarly papers, researchers, journals, and institutions.
    """

    def __init__(self):
        self.download_tools = DownloadTools("openalex")
        self.get_url = self.download_tools.query_url

    def openalex(
        self,
        query,
        size,
        update=None,
        makecsv=False,
        makexml=False,
        makehtml=False,
        getpdf=False,
        startdate=None,
        enddate=None,
    ):
        if update:
            cursor_mark = update[CURSOR_MARK]
        else:
            cursor_mark = "*"
        total_number_of_results = size
        total_papers_list = []
        logging.info("Making Request to OpenAlex")
        while len(total_papers_list) < size:
            total_number_of_results, total_papers_list, papers_list, metadata_list = (
                self.make_request_add_papers(
                    query,
                    cursor_mark,
                    total_number_of_results,
                    total_papers_list,
                    startdate,
                    enddate,
                )
            )

            cursor_mark = metadata_list["next_cursor"]
            if len(papers_list) == 0:
                logging.warning("Could not find more papers")
                break

        total_result_list = total_papers_list[:size]
        json_return_dict = self.download_tools._make_dict_from_list(
            total_result_list, paper_key=DOI
        )
        for paper in json_return_dict:
            self.download_tools._add_download_status_keys(paper, json_return_dict)
        if getpdf:
            self.download_pdf(json_return_dict)
        result_dict = self.download_tools._adds_new_results_to_metadata_dictionary(
            cursor_mark, json_return_dict, total_number_of_results, update=update
        )
        new_dict_to_return = result_dict[NEW_RESULTS]
        return_dict = new_dict_to_return[TOTAL_JSON_OUTPUT]
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv=makecsv,
            makehtml=makehtml,
            makexml=makexml,
            metadata_dictionary=return_dict,
            name=OPENALEX_RESULT,
        )
        return result_dict

    def send_post_request(
        self, query, cursor_mark="*", page_size=20, startdate=None, enddate=None
    ):

        url_to_request = self.get_url.format(
            query=query, cursor=cursor_mark, page_size=page_size
        )
        if startdate or enddate:
            if startdate:
                url_to_request += "&filter=from_publication_date:{}".format(startdate)
            if enddate:
                url_to_request += "&filter=to_publication_date:{}".format(enddate)
        print(url_to_request)
        start = time.time()
        request_handler = requests.get(url_to_request)
        stop = time.time()
        logging.debug("*/Got the Query Result */")
        logging.debug("Time elapsed: %s", (stop - start))
        return request_handler

    def make_request_add_papers(
        self,
        query,
        cursor_mark,
        total_number_of_results,
        total_papers_list,
        startdate,
        enddate,
    ):

        request_handler = self.send_post_request(
            query,
            cursor_mark,
            startdate=startdate,
            enddate=enddate,
        )
        request_dict = json.loads(request_handler.text)

        metadata_list = request_dict["meta"]
        papers_list = request_dict[RESULTS]
        if TOTAL_RESULTS in request_dict:
            total_number_of_results = request_dict[TOTAL_RESULTS]
        total_papers_list += papers_list
        return total_number_of_results, total_papers_list, papers_list, metadata_list

    def download_pdf(self, metadata_dictionary):
        """Downloads pdfs for papers in metadata dictionary

        :param metadata_dictionary: metadata dictionary for papers
        :type metadata_dictionary: dict
        """
        logging.info("Downloading Pdfs for papers")
        for result in tqdm(metadata_dictionary):
            best_oa_location = metadata_dictionary[result].get("best_oa_location", None)
            if best_oa_location is None:
                continue
            pdf_url = best_oa_location.get(PDF_URL, None)
            if pdf_url is None:
                continue
            self.download_tools.check_or_make_directory(
                os.path.join(os.getcwd(), result)
            )
            pdf_path = os.path.join(os.getcwd(), result, FULLTEXT_PDF)
            self.download_tools.queries_the_url_and_writes_response_to_destination(
                pdf_url, pdf_path
            )
            metadata_dictionary[result][PDFDOWNLOADED] = True

    def download_and_save_results(
        self,
        query,
        size,
        update=False,
        makecsv=False,
        makexml=False,
        makehtml=False,
        getpdf=False,
        startdate=None,
        enddate=None,
    ):

        result_dict = self.openalex(
            query,
            size,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
            getpdf=getpdf,
            startdate=startdate,
            enddate=enddate,
        )
        self.download_tools._make_metadata_json_files_for_paper(
            result_dict[NEW_RESULTS],
            updated_dict=result_dict[UPDATED_DICT],
            paper_key=DOI,
            name_of_file=OPENALEX_RESULT,
        )

    def apipaperdownload(self, query_namespace):

        self.download_and_save_results(
            query_namespace["query"],
            query_namespace["limit"],
            update=None,
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            makehtml=query_namespace["makehtml"],
            getpdf=query_namespace["pdf"],
            startdate=query_namespace.get("startdate", None),
            enddate=query_namespace.get("enddate", None),
        )

    def update(self, query_namespace):

        update_file_path = self.download_tools.get_metadata_results_file()
        logging.info(
            "Please ensure that you are providing the same --api as the one in the corpus or you "
            "may get errors"
        )
        os.chdir(os.path.dirname(update_file_path))
        logging.info("Reading old json metadata file")
        self.download_and_save_results(
            query_namespace["query"],
            query_namespace["limit"],
            update=update_file_path,
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            makehtml=query_namespace["makehtml"],
        )

    def noexecute(self, query_namespace):

        result_dict = self.openalex(query_namespace["query"], size=10)

        results = result_dict[NEW_RESULTS]
        totalhits = result_dict["meta"]["count"]
        logging.info("Total number of hits for the query are %s", totalhits)
