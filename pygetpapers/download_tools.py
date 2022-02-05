import configparser
import copy
import glob
import io
import json
import logging
import ntpath
import os
import time
import xml.etree.ElementTree as ET
import zipfile
from time import gmtime, strftime
import pandas as pd
import requests
import xmltodict
from dict2xml import dict2xml
from tqdm import tqdm
from lxml import etree

from pygetpapers.pgexceptions import PygetpapersError

PYGETPAPERS = "pygetpapers"

NEW_RESULTS = "new_results"

UPDATED_DICT = "updated_dict"

CURSOR_MARK = "cursor_mark"

TOTAL_HITS = "total_hits"

TOTAL_JSON_OUTPUT = "total_json_output"

JSONDOWNLOADED = "jsondownloaded"

HTMLMADE = "htmlmade"

CSVMADE = "csvmade"

PDF_DOWNLOADED = "pdfdownloaded"

DOWNLOADED = "downloaded"

SUPPLEMENTARY = "supplementary"

PMCID = "pmcid"

ABSTRACT = "abstract"

PDFLINKS = "pdflinks"

HTMLLINKS = "htmllinks"

PDFDOWNLOADED = "pdfdownloaded"

SUPPURL = "suppurl"

ZIPURL = "zipurl"

XMLURL = "xmlurl"

REFERENCESURL = "referencesurl"

CITATIONURL = "citationurl"

query_url = "query_url"

CONFIG_INI = "config.ini"

RESULTS_JSON = "results.json"

TERM = "term"

ENTRY = 'entry'



class DownloadTools:
    """Generic tools for retrieving literature"""

    def __init__(self, api=False):
        """[summary]

        :param api: [description], defaults to False
        :type api: bool, optional
        """
        self.config = self.setup_config_file(CONFIG_INI)
        if api:
            self.set_up_config_variables(self.config,api)

    def set_up_config_variables(self, config, api):
        """[summary]

        :param api: [description]
        :type api: [type]
        """
        self.query_url = config.get(api, query_url)
        self.citationurl = config.get(api, CITATIONURL)
        self.referencesurl = config.get(api, REFERENCESURL)
        self.xmlurl = config.get(api, XMLURL)
        self.zipurl = config.get(api, ZIPURL)
        self.suppurl = config.get(api, SUPPURL)

    def setup_config_file(self,config_ini):
        """[summary]

        :param config_ini: [description]
        :type config_ini: [type]
        :return: [description]
        :rtype: [type]
        """
        with open(
            os.path.join(os.path.dirname(__file__), config_ini)
        ) as file_handler:
            config_file = file_handler.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_string(config_file)
        return config

    def postquery(self, headers, payload):
        """[summary]

        :param headers: [description]
        :type headers: [type]
        :param payload: [description]
        :type payload: [type]
        :return: [description]
        :rtype: [type]
        """
        logging.debug("*/RESTful request for fulltext.xml (D)*/")
        start = time.time()
        request_handler = requests.post(
            self.query_url, data=payload, headers=headers)
        stop = time.time()
        logging.debug("*/Got the Query Result */")
        logging.debug("Time elapsed: %s", (stop - start))
        parser = etree.XMLParser(recover=True)
        e= etree.fromstring(request_handler.content, parser=parser)
        xmlstr = etree.tostring(e, encoding='utf8', method='xml')
        dict_to_return = xmltodict.parse(xmlstr)
        return dict_to_return

    @staticmethod
    def check_or_make_directory(directory_url):
        """[summary]

        :param directory_url: [description]
        :type directory_url: [type]
        """
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)

    @staticmethod
    def buildquery(
        cursormark,
        page_size,
        query,
        synonym=True,
    ):
        """[summary]

        :param cursormark: [description]
        :type cursormark: [type]
        :param page_size: [description]
        :type page_size: [type]
        :param query: [description]
        :type query: [type]
        :param synonym: [description], defaults to True
        :type synonym: bool, optional
        :return: [description]
        :rtype: [type]
        :rtype: [type]
        """
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        payload = {
            "query": query,
            "resultType": "core",
            "cursorMark": cursormark,
            "pageSize": page_size,
            "synonym": synonym,
            "format": "xml",
            "sort_PMCID": "y",
        }
        logging.debug("*/submitting RESTful query (I)*/")
        return {"headers": headers, "payload": payload}

    @staticmethod
    def write_or_append_to_csv(df_transposed, name="europe_pmc.csv"):
        """[summary]

        :param df_transposed: [description]
        :type df_transposed: [type]
        :param name: [description], defaults to "europe_pmc.csv"
        :type name: str, optional
        """
        path = os.path.join(str(os.getcwd()), name)
        if os.path.exists(path):
            df_transposed.to_csv(path, mode="a", header=False)
        else:
            df_transposed.to_csv(path)

    @staticmethod
    def writexml(directory_url, destination_url, content):
        """[summary]

        :param directory_url: [description]
        :type directory_url: [type]
        :param destination_url: [description]
        :type destination_url: [type]
        :param content: [description]
        :type content: [type]
        """
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        with open(destination_url, "wb") as file_handler:
            file_handler.write(content)

    @staticmethod
    def make_dict_for_csv(resultant_dict):
        """[summary]

        :param resultant_dict: [description]
        :type resultant_dict: [type]
        :return: [description]
        :rtype: [type]
        """
        resultant_dict_for_csv = copy.deepcopy(resultant_dict)
        for paper in resultant_dict_for_csv:
            paper_dict = resultant_dict_for_csv[paper]
            if DOWNLOADED in paper_dict:
                paper_dict.pop(DOWNLOADED)
            if PDFDOWNLOADED in paper_dict:
                paper_dict.pop(PDFDOWNLOADED)
            if JSONDOWNLOADED in paper_dict:
                paper_dict.pop(JSONDOWNLOADED)
            if CSVMADE in paper_dict:
                paper_dict.pop(CSVMADE)
            if HTMLMADE in paper_dict:
                paper_dict.pop(HTMLMADE)
        return resultant_dict_for_csv

    @staticmethod
    def write_content_to_destination(url, destination):
        """[summary]

        :param url: [description]
        :type url: [type]
        :param destination: [description]
        :type destination: [type]
        """
        with open(destination, "wb") as file:
            response = requests.get(url)
            file.write(response.content)

    @staticmethod
    def makejson(path, final_xml_dict):
        """[summary]

        :param path: [description]
        :type path: [type]
        :param final_xml_dict: [description]
        :type final_xml_dict: [type]
        """
        append_write = "w"
        with open(path, append_write, encoding="utf-8") as file_handler:
            json.dump(final_xml_dict, file_handler)

    @staticmethod
    def clean_dict_for_csv(paperdict):
        """[summary]

        :param paperdict: [description]
        :type paperdict: [type]
        :return: [description]
        :rtype: [type]
        """
        dict_to_write = dict(paperdict)
        dict_to_write.pop(PDF_DOWNLOADED)
        dict_to_write.pop(JSONDOWNLOADED)
        dict_to_write.pop(CSVMADE)
        return dict_to_write

    @staticmethod
    def make_dataframe_for_paper_dict(result, return_dict):
        """[summary]

        :param result: [description]
        :type result: [type]
        :param return_dict: [description]
        :type return_dict: [type]
        :return: [description]
        :rtype: [type]
        """
        dict_for_df = {k: [v] for k, v in return_dict[result].items()}
        df_for_paper = pd.DataFrame(dict_for_df)
        return df_for_paper

    @staticmethod
    def conditions_to_download(paperdict):
        """[summary]

        :param paperdict: [description]
        :type paperdict: [type]
        :return: [description]
        :rtype: [type]
        """
        condition_to_down = False
        condition_to_download_pdf = False
        condition_to_download_json = False
        condition_to_download_csv = False
        condition_to_html = False
        if not paperdict[DOWNLOADED]:
            condition_to_down = True
        if not paperdict[PDFDOWNLOADED]:
            condition_to_download_pdf = True
        if not paperdict[JSONDOWNLOADED]:
            condition_to_download_json = True
        if not paperdict[CSVMADE]:
            condition_to_download_csv = True
        if not paperdict[HTMLMADE]:
            condition_to_html = True
        return (
            condition_to_down,
            condition_to_download_csv,
            condition_to_download_json,
            condition_to_download_pdf,
            condition_to_html,
        )

    @staticmethod
    def make_clickable(link):
        """[summary]

        :param link: [description]
        :type link: [type]
        :return: [description]
        :rtype: [type]
        """
        tag_to_return = f'<a target="_blank" href="{link}">Link</a>'
        if str(link) == "nan":
            tag_to_return = "Not Found"
        return tag_to_return

    def getcitations(self, pmcid, source):
        """[summary]

        :param pmcid: [description]
        :type pmcid: [type]
        :param source: [description]
        :type source: [type]
        :return: [description]
        :rtype: [type]
        """
        request_handler = requests.get(
            self.citationurl.format(source=source, pmcid=pmcid)
        )
        return request_handler.content

    def getreferences(self, pmcid, source):
        """[summary]

        :param pmcid: [description]
        :type pmcid: [type]
        :param source: [description]
        :type source: [type]
        :return: [description]
        :rtype: [type]
        """
        request_handler = requests.get(
            self.referencesurl.format(source=source, pmcid=pmcid)
        )
        return request_handler.content

    @staticmethod
    def add_scrollbar(text):
        """[summary]

        :param text: [description]
        :type text: [type]
        :return: [description]
        :rtype: [type]
        """
        return f'<div id="table">{text}</div>'

    def make_html_from_dataframe(self, dataframe, url):
        """
        """
        dataframe = dataframe.T
        
        base_html = """
    <!doctype html>
    <html>
      <head>
          <meta http-equiv="Content-type" content="text/html; charset=utf-8">
          <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/2.2.2/jquery.min.js">
          </script>
          <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.16/css/jquery.dataTables.css">
          <script type="text/javascript" src="https://cdn.datatables.net/1.10.16/js/jquery.dataTables.js"></script>
          <style>
          # table {
              height: 250px;
              overflow-y:scroll;
          }
          </style>
      </head>
      <body>%s<script type="text/javascript">$(document).ready(function(){$('table').DataTable({
      "pageLength": 20
      });});</script>
      </body>
    </html>
    """
        html = dataframe.to_html(escape=False)
        html_with_pagination = base_html % html
        with open(url, "w", encoding="utf-8") as file_handler:
            file_handler.write(html_with_pagination)

    def make_html_from_dict(self, dict_to_write_html_from, url):
        """[summary]

        :param dict_to_write_html_from: [description]
        :type dict_to_write_html_from: [type]
        :param url: [description]
        :type url: [type]
        """
        df = pd.Series(dict_to_write_html_from).to_frame(
            dict_to_write_html_from[PMCID]
        )
        self.make_html_from_dataframe(df, url)

    def make_references(self, directory_url, paperid, source, referenceurl):
        """[summary]

        :param directory_url: [description]
        :type directory_url: [type]
        :param paperid: [description]
        :type paperid: [type]
        :param source: [description]
        :type source: [type]
        :param referenceurl: [description]
        :type referenceurl: [type]
        """
        getreferences = self.getreferences(paperid, source)
        self.writexml(directory_url, referenceurl, getreferences)

    def make_citations(self, source, citationurl, directory_url, paperid):
        """[summary]

        :param source: [description]
        :type source: [type]
        :param citationurl: [description]
        :type citationurl: [type]
        :param directory_url: [description]
        :type directory_url: [type]
        :param paperid: [description]
        :type paperid: [type]
        """
        getcitations = self.getcitations(paperid, source)
        self.writexml(directory_url, citationurl, getcitations)

    @staticmethod
    def readjsondata(path):
        """[summary]

        :param path: [description]
        :type path: [type]
        :return: [description]
        :rtype: [type]
        """
        with open(path) as file_handler:
            dict_from_json = json.load(file_handler)
        return dict_from_json

    @staticmethod
    def log_making_xml():
        """[summary]
        """
        logging.debug(
            "*/saving xml to per-document directories (CTrees) (D)*/")
        loggingurl = os.path.join(str(os.getcwd()), "*", "fulltext.xml")
        logging.info("Saving XML files to %s", loggingurl)
        logging.debug("*/Making the Request to get full text xml*/")

    def getxml(self, pmcid):
        """[summary]

        :param pmcid: [description]
        :type pmcid: [type]
        :return: [description]
        :rtype: [type]
        """
        request_handler = requests.get(self.xmlurl.format(pmcid=pmcid))
        return request_handler.content

    def getsupplementaryfiles(
        self, pmcid, directory_url, destination_url, from_ftp_end_point=False
    ):
        """[summary]

        :param pmcid: [description]
        :type pmcid: [type]
        :param directory_url: [description]
        :type directory_url: [type]
        :param destination_url: [description]
        :type destination_url: [type]
        :param from_ftp_end_point: [description], defaults to False
        :type from_ftp_end_point: bool, optional
        """
        log_key = SUPPLEMENTARY
        if from_ftp_end_point:
            key = "PMCxxxx" + pmcid[-3:]
            path = self.zipurl.format(key=key, pmcid=pmcid)
            log_key = "zip"
        else:
            path = self.suppurl.format(pmcid=pmcid)
        request_handler = requests.get(path)
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        file_exits = False
        for chunk in request_handler.iter_content(chunk_size=128):
            if len(chunk) > 0:
                file_exits = True
                break
        if file_exits:
            self.extract_zip_files(
                request_handler, destination_url, log_key, pmcid)
        else:
            logging.warning("%s files not found for %s", log_key, pmcid)

    def extract_zip_files(self, request_handler, destination_url, log_key, pmcid):
        """[summary]

        :param request_handler: [description]
        :type request_handler: [type]
        :param destination_url: [description]
        :type destination_url: [type]
        :param log_key: [description]
        :type log_key: [type]
        :param pmcid: [description]
        :type pmcid: [type]
        """
        try:
            z = zipfile.ZipFile(io.BytesIO(request_handler.content))
            self.check_or_make_directory(destination_url)
            z.extractall(destination_url)
            logging.info("Wrote %s files for %s", log_key, log_key)
        except PygetpapersError as exception:
            logging.warning("%s files not found for %s", log_key, pmcid)
            logging.debug(exception)

    def make_initial_columns_for_paper_dict(self, key_for_dict, resultant_dict):
        """[summary]

        :param key_for_dict: [description]
        :type key_for_dict: [type]
        :param resultant_dict: [description]
        :type resultant_dict: [type]
        :return: [description]
        :rtype: [type]
        """
        resultant_dict[key_for_dict] = {}
        self.add_download_status_keys(key_for_dict, resultant_dict)
        return resultant_dict

    @staticmethod
    def add_download_status_keys(key_for_dict, resultant_dict):
        """[summary]

        :param key_for_dict: [description]
        :type key_for_dict: [type]
        :param resultant_dict: [description]
        :type resultant_dict: [type]
        """
        resultant_dict[key_for_dict][DOWNLOADED] = False
        resultant_dict[key_for_dict][PDF_DOWNLOADED] = False
        resultant_dict[key_for_dict][JSONDOWNLOADED] = False
        resultant_dict[key_for_dict][CSVMADE] = False
        resultant_dict[key_for_dict][HTMLMADE] = False

    def make_csv_for_dict(self, df, return_dict, output_main, output_paper):
        """[summary]

        :param df: [description]
        :type df: [type]
        :param return_dict: [description]
        :type return_dict: [type]
        :param output_main: [description]
        :type output_main: [type]
        :param output_paper: [description]
        :type output_paper: [type]
        """
        logging.info("Making csv files for metadata at %s", os.getcwd())
        paper = 0
        self.write_or_append_to_csv(df, output_main)
        dict_to_use = self.make_dict_for_csv(return_dict)
        for result in tqdm(dict_to_use):
            paper += 1
            result_encoded = self.url_encode_id(result)
            url = os.path.join(os.getcwd(), result_encoded, output_paper)
            self.check_or_make_directory(
                os.path.join(os.getcwd(), result_encoded))
            df_for_paper = self.make_dataframe_for_paper_dict(
                result, dict_to_use)
            self.write_or_append_to_csv(df_for_paper, url)
            return_dict[result][CSVMADE] = True
            logging.debug("Wrote csv files for paper %s", paper)

    def make_html_for_dict(self, df, return_dict, output_main, output_paper):
        """[summary]

        :param df: [description]
        :type df: [type]
        :param return_dict: [description]
        :type return_dict: [type]
        :param output_main: [description]
        :type output_main: [type]
        :param output_paper: [description]
        :type output_paper: [type]
        """
        logging.info("Making html files for metadata at %s", os.getcwd())
        paper = 0
        htmlurl = os.path.join(os.getcwd(), output_main)
        self.make_html_from_dataframe(df, htmlurl)
        for result in tqdm(return_dict):
            paper += 1
            result_encoded = self.url_encode_id(result)
            url = os.path.join(os.getcwd(), result_encoded, output_paper)
            self.check_or_make_directory(
                os.path.join(os.getcwd(), result_encoded))
            df_for_paper = self.make_dataframe_for_paper_dict(
                result, return_dict)
            self.make_html_from_dataframe(df_for_paper, url)
            return_dict[result][HTMLMADE] = True
            logging.debug("Wrote xml files for paper %s", paper)

    def make_xml_for_dict(self, return_dict, output_main, output_paper):
        """[summary]

        :param return_dict: [description]
        :type return_dict: [type]
        :param output_main: [description]
        :type output_main: [type]
        :param output_paper: [description]
        :type output_paper: [type]
        """
        dict_to_use = self.make_dict_for_csv(return_dict)
        total_xml = dict2xml(dict_to_use, wrap="root", indent="   ")
        logging.info("Making xml files for metadata at %s", os.getcwd())
        xmlurl = os.path.join(os.getcwd(), output_main)
        with open(xmlurl, "w", encoding="utf-8") as file_handler:
            file_handler.write(total_xml)
        paper = 0
        for result in tqdm(dict_to_use):
            paper += 1
            total_xml_of_paper = dict2xml(
                dict_to_use[result], wrap="root", indent="   "
            )
            result_encoded = self.url_encode_id(result)
            xmlurl_of_paper = os.path.join(
                os.getcwd(), result_encoded, output_paper)

            self.check_or_make_directory(
                os.path.join(os.getcwd(), result_encoded))

            with open(xmlurl_of_paper, "w", encoding="utf-8") as file_handler:
                file_handler.write(total_xml_of_paper)

            logging.debug("Wrote xml files for paper %s", paper)

    def handle_creation_of_csv_html_xml(
        self, makecsv, makehtml, makexml, return_dict, name
    ):
        """[summary]

        :param makecsv: [description]
        :type makecsv: [type]
        :param makehtml: [description]
        :type makehtml: [type]
        :param makexml: [description]
        :type makexml: [type]
        :param return_dict: [description]
        :type return_dict: [type]
        :param name: [description]
        :type name: [type]
        """
        dict_to_use = self.make_dict_for_csv(return_dict)
        df = pd.DataFrame.from_dict(dict_to_use)
        if makecsv:
            self.make_csv_for_dict(
                df, return_dict, f"{name}s.csv", f"{name}.csv")
        if makehtml:
            self.make_html_for_dict(
                df, return_dict, f"{name}s.html", f"{name}.html")
        if makexml:
            self.make_xml_for_dict(return_dict, f"{name}s.xml", f"{name}.xml")

    @staticmethod
    def url_encode_id(doi_of_paper):
        """[summary]

        :param doi_of_paper: [description]
        :type doi_of_paper: [type]
        :return: [description]
        :rtype: [type]
        """
        url_encoded_doi_of_paper = doi_of_paper.replace(
            "\\", "_").replace("/", "_")
        return url_encoded_doi_of_paper

    @staticmethod
    def get_version():
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        with open(
            os.path.join(os.path.dirname(__file__), "config.ini")
        ) as file_handler:
            config_file = file_handler.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_string(config_file)
        version = config.get("pygetpapers", "version")
        return version

    @staticmethod
    def make_dict_from_list(metadata_list, paper_key):
        """[summary]

        :param metadata_list: [description]
        :type metadata_list: [type]
        :param paper_key: [description]
        :type paper_key: [type]
        :return: [description]
        :rtype: [type]
        """
        paper_by_key = {}
        for paper in metadata_list:
            paper_by_key[paper[paper_key]] = paper
        return paper_by_key

    def make_json_files_for_paper(self, returned_dict, updated_dict, paper_key, name_of_file):
        """[summary]

        :param returned_dict: [description]
        :type returned_dict: [type]
        :param updated_dict: [description]
        :type updated_dict: [type]
        :param paper_key: [description]
        :type paper_key: [type]
        :param name_of_file: [description]
        :type name_of_file: [type]
        """
        self.makejson(f"{name_of_file}s.json", updated_dict)
        logging.info("Wrote metadata file for the query")
        paper_numer = 0
        logging.info("Writing metadata file for the papers at %s",
                     str(os.getcwd()))
        total_dict = returned_dict["total_json_output"]
        for paper in tqdm(total_dict):
            dict_of_paper = total_dict[paper]
            if not dict_of_paper[JSONDOWNLOADED]:
                paper_numer += 1
                doi_of_paper = dict_of_paper[paper_key]
                url_encoded_doi_of_paper = self.url_encode_id(doi_of_paper)
                self.check_or_make_directory(url_encoded_doi_of_paper)
                path_to_save_metadata = os.path.join(
                    str(os.getcwd()
                        ), url_encoded_doi_of_paper, f"{name_of_file}.json"
                )
                dict_of_paper[JSONDOWNLOADED] = True
                self.makejson(path_to_save_metadata, dict_of_paper)
                logging.debug(
                    "Wrote metadata file for the paper %s", paper_numer)

    def make_dict_to_return(
        self, cursor_mark, paper_by_key, total_number_of_results, update=None
    ):
        """[summary]

        :param cursor_mark: [description]
        :type cursor_mark: [type]
        :param paper_by_key: [description]
        :type paper_by_key: [type]
        :param total_number_of_results: [description]
        :type total_number_of_results: [type]
        :param update: [description], defaults to None
        :type update: [type], optional
        :return: [description]
        :rtype: [type]
        """
        new_dict_to_return = {
            TOTAL_JSON_OUTPUT: paper_by_key,
            TOTAL_HITS: total_number_of_results,
            CURSOR_MARK: cursor_mark,
        }

        dict_to_return_with_previous = copy.deepcopy(new_dict_to_return)
        if update:

            dict_to_return_with_previous[TOTAL_JSON_OUTPUT].update(
                update[TOTAL_JSON_OUTPUT]
            )
        return {UPDATED_DICT: dict_to_return_with_previous, NEW_RESULTS: new_dict_to_return}

    def get_metadata_results_file(self):
        """[summary]

        :raises PygetpapersError: [description]
        :return: [description]
        :rtype: [type]
        """
        list_of_metadata_jsons = glob.glob(os.path.join(os.getcwd(), "*.json"))
        meta_data_results_file_path = None
        for file in list_of_metadata_jsons:
            metadata_file = ntpath.basename(file)
            if metadata_file.endswith(RESULTS_JSON):
                meta_data_results_file_path = file
        if not meta_data_results_file_path:
            raise PygetpapersError(
                "Corpus not existing in this directory. Please rerun the query without --update or --restart")
        return meta_data_results_file_path

    