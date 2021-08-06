import time
import os
import json
import logging
import requests
import sys
from tqdm import tqdm
from pygetpapers.download_tools import DownloadTools


class Rxiv:
    """Rxiv class which handles Biorxiv and Medrxiv repository"""

    def __init__(self):
        """initiate Rxiv class"""
        self.download_tools = DownloadTools("rxiv")
        self.get_url = self.download_tools.posturl

    def rxiv(
        self,
        interval,
        size,
        source="biorxiv",
        update=None,
        makecsv=False,
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
        :param makehtml: [description], defaults to False
        :type makehtml: bool, optional
        :return: [description]
        :rtype: [type]
        """
        if update:
            cursor_mark = update["cursor_mark"]
        else:
            cursor_mark = 0
        total_number_of_results = 0
        total_papers_list = []
        logging.info("Making Request to rxiv")
        while len(total_papers_list) < size:
            total_number_of_results, total_papers_list, papers_list = self.make_request_add_papers(
                cursor_mark,
                interval,
                source,
                total_number_of_results,
                total_papers_list,
            )
            if len(papers_list) == 0:
                logging.warning("No more papers found")
                break
            cursor_mark += 1
        json_return_dict = {}
        paper_counter = 0
        while len(json_return_dict) < len(total_papers_list):
            if update:
                if total_papers_list[paper_counter]["doi"] not in update["total_json_output"]:
                    json_return_dict[total_papers_list[paper_counter]
                                     ["doi"]] = total_papers_list[paper_counter]
            else:
                json_return_dict[total_papers_list[paper_counter]
                                 ["doi"]] = total_papers_list[paper_counter]
            paper_counter += 1

        for paper in json_return_dict:
            self.download_tools.add_keys_for_conditions(
                paper, json_return_dict)
        result_dict = self.download_tools.make_dict_to_return(
            cursor_mark, json_return_dict, total_number_of_results, update=update)

        return_dict = result_dict["new_results"]["total_json_output"]
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv=makecsv,
            makehtml=makehtml,
            makexml=False,
            return_dict=return_dict,
            name="rxiv_result",
        )
        return result_dict

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
        self.make_request_url_for_rxiv(cursor_mark, interval, source)
        request_handler = self.post_request()
        request_dict = json.loads(request_handler.text)
        papers_list = request_dict["collection"]
        if "total" in request_dict["messages"][0]:
            total_number_of_results = request_dict["messages"][0]["total"]
        total_papers_list += papers_list
        return total_number_of_results, total_papers_list, papers_list

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
            logging.warning("Update will not work if date not provided")
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
        os.chdir(os.path.dirname(update))
        update = self.download_tools.readjsondata(update)
        logging.info("Reading old json metadata file")
        self.download_and_save_results(
            interval,
            size,
            update=update,
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
        update=False,
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
        :param update: [description], defaults to False
        :type update: bool, optional
        :param makecsv: [description], defaults to False
        :type makecsv: bool, optional
        :param makexml: [description], defaults to False
        :type makexml: bool, optional
        :param makehtml: [description], defaults to False
        :type makehtml: bool, optional
        """
        if update and type(interval) == int:
            logging.warning("Update will not work if date not provided")
            sys.exit(1)
        result_dict = self.rxiv(
            interval,
            size,
            update=update,
            source=source,
            makecsv=makecsv,
            makehtml=makehtml,
        )
        if makexml:
            logging.info("Making xml for paper")
            dict_of_papers = result_dict["new_results"]["total_json_output"]
            self.make_xml_for_rxiv(
                dict_of_papers, "jatsxml", "doi", "fulltext.xml")
        self.download_tools.make_json_files_for_paper(
            result_dict["new_results"], updated_dict=result_dict["updated_dict"], key_in_dict="doi", name_of_file="rxiv_result"
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
        result_dict = self.rxiv(
            time_interval, size=10, source=source)
        totalhits = result_dict["new_results"]["total_hits"]
        logging.info("Total number of hits for the query are %s", totalhits)
