import time
import os
import json
import logging
import requests
from tqdm import tqdm
from pygetpapers.download_tools import DownloadTools


class Rxiv:
    """Rxiv class which handles Biorxiv and Medrxiv repository"""

    def __init__(self):
        """[summary]"""
        self.download_tools = DownloadTools("rxiv")
        self.get_url = self.download_tools.posturl

    def rxiv(
        self,
        interval,
        size,
        source="biorxiv",
        update=None,
        makecsv=False,
        makexml=False,
        makehtml=False,
    ):
        """[summary]

        :param interval: [description]
        :type interval: [type]
        :param size: [description]
        :type size: [type]
        :param source: [description], defaults to "biorxiv"
        :type source: str, optional
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
            cursor_mark = update["cursor_mark"]
        else:
            cursor_mark = 0
        total_number_of_results = size
        total_papers_list = []
        while len(total_papers_list) < size:
            total_number_of_results, total_papers_list = self.make_request_add_papers(
                cursor_mark,
                interval,
                source,
                total_number_of_results,
                total_papers_list,
            )
            if len(total_papers_list) ==0:
                logging.warning("No more papers found")
                break
            cursor_mark += 1
        total_result_list = total_papers_list[:size]
        json_return_dict = self.download_tools.make_dict_from_returned_list(
            total_result_list, key_in_dict="doi"
        )
        for paper in json_return_dict:
            self.download_tools.add_keys_for_conditions(
                paper, json_return_dict)
        dict_to_return = self.download_tools.make_dict_to_return(
            cursor_mark, json_return_dict, total_number_of_results, update
        )
        return_dict = dict_to_return["total_json_output"]
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv=makecsv,
            makehtml=makehtml,
            makexml=False,
            return_dict=return_dict,
            name="rxiv-result",
        )
        return dict_to_return

    def make_request_add_papers(
        self, cursor_mark, interval, source, total_number_of_results, total_papers_list
    ):
        """[summary]

        :param cursor_mark: [description]
        :type cursor_mark: [type]
        :param interval: [description]
        :type interval: [type]
        :param source: [description]
        :type source: [type]
        :param total_number_of_results: [description]
        :type total_number_of_results: [type]
        :param total_papers_list: [description]
        :type total_papers_list: [type]
        :return: [description]
        :rtype: [type]
        """
        logging.info("Making Request to rxiv")
        self.make_request_url_for_rxiv(cursor_mark, interval, source)
        request_handler = self.post_request()
        request_dict = json.loads(request_handler.text)
        papers_list = request_dict["collection"]
        if "total" in request_dict["messages"][0]:
            total_number_of_results = request_dict["messages"][0]["total"]
        total_papers_list += papers_list
        return total_number_of_results, total_papers_list

    def post_request(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        start = time.time()
        request_handler = requests.post(self.get_url)
        stop = time.time()
        logging.debug("*/Got the Query Result */")
        logging.debug("Time elapsed: %s", (stop - start))
        return request_handler

    def make_request_url_for_rxiv(self, cursor_mark, interval, source):
        """[summary]

        :param cursor_mark: [description]
        :type cursor_mark: [type]
        :param interval: [description]
        :type interval: [type]
        :param source: [description]
        :type source: [type]
        """
        if type(interval) == int:
            self.get_url = "https://api.biorxiv.org/details/{source}/{interval}".format(
                source=source, interval=interval
            )
        else:
            self.get_url = self.download_tools.posturl.format(
                source=source, interval=interval, cursor=cursor_mark
            )

    def rxiv_update(
        self,
        interval,
        size,
        source="biorxiv",
        update=None,
        makecsv=False,
        makexml=False,
        makehtml=False,
    ):
        """[summary]

        :param interval: [description]
        :type interval: [type]
        :param size: [description]
        :type size: [type]
        :param source: [description], defaults to "biorxiv"
        :type source: str, optional
        :param update: [description], defaults to None
        :type update: [type], optional
        :param makecsv: [description], defaults to False
        :type makecsv: bool, optional
        :param makexml: [description], defaults to False
        :type makexml: bool, optional
        :param makehtml: [description], defaults to False
        :type makehtml: bool, optional
        """
        update = self.download_tools.readjsondata(update)
        logging.info("Reading old json metadata file")
        self.download_and_save_results(
            interval,
            size,
            source=source,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )

    def download_and_save_results(
        self,
        interval,
        size,
        source,
        makecsv=False,
        makexml=False,
        makehtml=False,
    ):
        """[summary]

        :param interval: [description]
        :type interval: [type]
        :param size: [description]
        :type size: [type]
        :param source: [description]
        :type source: [type]
        :param makecsv: [description], defaults to False
        :type makecsv: bool, optional
        :param makexml: [description], defaults to False
        :type makexml: bool, optional
        :param makehtml: [description], defaults to False
        :type makehtml: bool, optional
        """
        returned_result = self.rxiv(
            interval,
            size,
            source=source,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        if makexml:
            logging.info("Making xml for paper")
            dict_of_papers = returned_result["total_json_output"]
            self.make_xml_for_rxiv(
                dict_of_papers, "jatsxml", "doi", "fulltext.xml")
        self.download_tools.make_json_files_for_paper(
            returned_result, key_in_dict="doi", name_of_file="rxiv-result"
        )

    def make_xml_for_rxiv(
        self, dict_of_papers, xml_identifier, paper_id_identifier, filename
    ):
        """[summary]

        :param dict_of_papers: [description]
        :type dict_of_papers: [type]
        :param xml_identifier: [description]
        :type xml_identifier: [type]
        :param paper_id_identifier: [description]
        :type paper_id_identifier: [type]
        :param filename: [description]
        :type filename: [type]
        """
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
            self.download_tools.write_content_to_destination(
                xml_url, path_to_save_xml)

    def noexecute(self, time_interval, source):
        """[summary]

        :param time_interval: [description]
        :type time_interval: [type]
        :param source: [description]
        :type source: [type]
        """
        returned_result = self.rxiv(time_interval, size=10, source=source)
        totalhits = returned_result["total_hits"]
        logging.info("Total number of hits for the query are %s", totalhits)
