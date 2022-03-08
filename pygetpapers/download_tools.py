import configparser
import copy
import glob
import io
import json
import logging
import ntpath
import os
import time
from urllib import request
import xml.etree.ElementTree as ET
import zipfile
from time import gmtime, strftime
import pandas as pd
import requests
import xmltodict
from dict2xml import dict2xml
from tqdm import tqdm
from lxml import etree
from pathlib import Path
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
    """Generic tools for retrieving literature. Several are called by each repository"""

    def __init__(self, api=None):
        """Reads the configuration file for the api

        :param api: Name of api as described in the configuration file
        :type api: string
        """
        self.config = self.setup_config_file(CONFIG_INI)
        if api:
            self.set_up_config_variables(self.config,api)

    def set_up_config_variables(self, config, api):
        """Sets class variable reading the configuration file for the provided api

        :param config: configparser object for the configuration file
        :type config: configparser object
        :param api: Name of api as described in the configuration file
        :type api: string
        """
        self.query_url = config.get(api, query_url)
        self.citationurl = config.get(api, CITATIONURL)
        self.referencesurl = config.get(api, REFERENCESURL)
        self.xmlurl = config.get(api, XMLURL)
        self.zipurl = config.get(api, ZIPURL)
        self.suppurl = config.get(api, SUPPURL)

    def setup_config_file(self,config_ini):
        """Reads config_ini file and returns configparser object

        :param config_ini: path of configuration file
        :type config_ini: string
        :return: configparser object for the configuration file
        :rtype: configparser object
        """
        with open(
            os.path.join(os.path.dirname(__file__), config_ini)
        ) as file_handler:
            config_file = file_handler.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_string(config_file)
        return config

    def gets_result_dict_for_query(self, headers, data):
        """Queries query_url provided in configuration file for the given headers and payload and returns result in the form of a python dictionary

        :param headers: headers given to the request
        :type headers: dict
        :param payload: payload given to the request
        :type payload: dict
        :return: result in the form of a python dictionary
        :rtype: dictionary
        """
        logging.debug("*/RESTful request for fulltext.xml (D)*/")
        request_handler = self.post_query(
            self.query_url, data=data, headers=headers)
        parser = etree.XMLParser(recover=True)
        e= etree.fromstring(request_handler.content, parser=parser)
        xmlstr = etree.tostring(e, encoding='utf8', method='xml')
        dict_to_return = xmltodict.parse(xmlstr)
        return dict_to_return

    def post_query(self,url, data=None, headers=None):  
        """Queries url

        :param headers: headers given to the request
        :type headers: dict
        :param payload: payload given to the request
        :type payload: dict
        :return: result in the form of a python dictionary
        :rtype: dictionary
        """      
        start = time.time()
        request_handler = requests.post(url,data=data, headers=headers)
        stop = time.time()
        logging.debug("*/Got the Query Result */")
        logging.debug("Time elapsed: %s", (stop - start))
        return request_handler

    @staticmethod
    def check_or_make_directory(directory_url):
        """Makes directory if doesn't already exist

        :param directory_url: path to directory
        :type directory_url: string
        """
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)

    @staticmethod
    def write_or_append_to_csv(df_transposed, csv_path="europe_pmc.csv"):
        """write pandas dataframe to given csv file

        :param df_transposed: dataframe to save
        :type df_transposed: pandas dataframe
        :param csv_path: path to csv file, defaults to "europe_pmc.csv"
        :type csv_path: str, optional
        """
        path = os.path.join(str(os.getcwd()), csv_path)
        if os.path.exists(path):
            df_transposed.to_csv(path, mode="a", header=False)
        else:
            df_transposed.to_csv(path)

    def writexml(self, destination_url, xml_content):
        """writes xml content to given destination_url

        :param destination_url: path to dump xml content
        :type destination_url: string
        :param xml_content: xml content 
        :type xml_content: byte string
        """
        directory_url = self.get_parent_directory(destination_url)
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        with open(destination_url, "wb") as file_handler:
            file_handler.write(xml_content)

    @staticmethod
    def removing_added_attributes_from_dictionary(resultant_dict):
        """ pygetpapers adds some attributes like "pdfdownloaded" to track the progress of downloads for a particular corpus. When we are exporting data to a csv file, we dont want these terms to appear.
        So this funtion makes a copy of the given dictionary, removes the added attributes from dictionaries inside the given dict and returns the new dictionary.


        :param resultant_dict: given parent dictionary
        :type resultant_dict: dictionary
        :return: dictionary with additional attributes removed from the child dictionaries 
        :rtype: dictionary
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
    def queries_the_url_and_writes_response_to_destination(url, destination):
        """ queries the url and writes response to destination

        :param url: url to query
        :type url: string
        :param destination: destination to save response to
        :type destination: string
        """
        with open(destination, "wb") as file:
            response = requests.get(url)
            file.write(response.content)

    @staticmethod
    def dumps_json_to_given_path(path, json_dict,filemode="w"):
        """ dumps json dict to given path

        :param path: path to dump dict 
        :type path: string
        :param json_dict: json dictionary 
        :type json_dict: dictionary
        :param filemode: file mode, defaults to "w"
        :type filemode: string, optional
        """
        with open(path, filemode, encoding="utf-8") as file_handler:
            json.dump(json_dict, file_handler)

    @staticmethod
    def _eupmc_clean_dict_for_csv(paperdict):
        dict_to_write = dict(paperdict)
        dict_to_write.pop(PDF_DOWNLOADED)
        dict_to_write.pop(JSONDOWNLOADED)
        dict_to_write.pop(CSVMADE)
        return dict_to_write

    @staticmethod
    def _make_dataframe_for_paper_dict(result, metadata_dictionary):
        dict_for_df = {k: [v] for k, v in metadata_dictionary[result].items()}
        df_for_paper = pd.DataFrame(dict_for_df)
        return df_for_paper

    @staticmethod
    def _conditions_to_download(paperdict):
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
    def _make_clickable(link):
        tag_to_return = f'<a target="_blank" href="{link}">Link</a>'
        if str(link) == "nan":
            tag_to_return = "Not Found"
        return tag_to_return

    def get_request_endpoint_for_citations(self, identifier, source):
        """Gets endpoint to get citations from the configuration file 

        :param identifier: unique identifier present in the url for the particular paper
        :type identifier: string
        :param source: which repository to get the citations from 
        :type source: string
        :return: request_handler.content
        :rtype: bytes
        """
        request_handler = requests.get(
            self.citationurl.format(source=source, identifier=identifier)
        )
        return request_handler.content

    def get_request_endpoint_for_references(self, identifier, source):
        """Gets endpoint to get references from the configuration file 

        :param identifier: unique identifier present in the url for the particular paper
        :type identifier: string
        :param source: which repository to get the citations from 
        :type source: string
        :return: request_handler.content
        :rtype: bytes
        """
        request_handler = requests.get(
            self.referencesurl.format(source=source, identifier=identifier)
        )
        return request_handler.content

    @staticmethod
    def _add_scrollbar(text):
        return f'<div id="table">{text}</div>'

    def make_html_from_dataframe(self, dataframe, path_to_save):
        """Makes html page from the pandas given dataframe

        :param dataframe: pandas dataframe to convert to html
        :type dataframe: pandas dataframe
        :param path_to_save: path to save the dataframe to
        :type path_to_save: string
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
        with open(path_to_save, "w", encoding="utf-8") as file_handler:
            file_handler.write(html_with_pagination)

    def make_references(self, paperid, identifier, path_to_save):
        """Writes references for the given paperid from source to reference url

        :param identifier: identifier for the paper
        :type identifier: string
        :param source: source to get references from
        :type source: string
        :param path_to_save: path to store the references
        :type path_to_save: string
        """
        getreferences = self.get_request_endpoint_for_references(paperid, identifier)
        self.writexml(path_to_save, getreferences)

    def make_citations(self, source, citationurl, identifier):
        """Retreives URL for the citations for the given paperid, gets the xml, writes to citationurl

        :param source: which repository to get the citations from
        :type source: which repository to get the citations from 
        :param citationurl: path to save the citations to 
        :type citationurl: string
        :param identifier: unique identifier present in the url for the particular paper
        :type identifier: string
        """
        getcitations = self.get_request_endpoint_for_citations(identifier, source)
        self.writexml(citationurl, getcitations)

    @staticmethod
    def readjsondata(path):
        """reads json from path and returns python dictionary
        """
        with open(path) as file_handler:
            dict_from_json = json.load(file_handler)
        return dict_from_json

    @staticmethod
    def _log_making_xml():
        logging.debug(
            "*/saving xml to per-document directories (CTrees) (D)*/")
        loggingurl = os.path.join(str(os.getcwd()), "*", "fulltext.xml")
        logging.info("Saving XML files to %s", loggingurl)
        logging.debug("*/Making the Request to get full text xml*/")

    def get_request_endpoint_for_xml(self, identifier):
        """Gets endpoint to full text xml from the configuration file 

        :param identifier: unique identifier present in the url for the particular paper
        :type identifier: string
        :return: request_handler.content
        :rtype: bytes
        """
        request_handler = requests.get(self.xmlurl.format(identifier=identifier))
        return request_handler.content

    def get_parent_directory(self,path):
        """Returns path of the parent directory for given path

        :param path: path of the file
        :type path: string
        :return: path of the parent directory
        :rtype: string
        """
        path = Path(path)
        return path.parent.absolute()

    def getsupplementaryfiles(
        self, identifier, path_to_save, from_ftp_end_point=False
    ):
        """Retrieves supplementary files for the given paper (according to identifier) and saves to path_to_save

        :param identifier: unique identifier present in the url for the particular paper
        :type identifier: string
        :param path_to_save: path to save the supplementary files to
        :type path_to_save: string
        :param from_ftp_end_point: to get the results from eupmc ftp endpoint
        :type from_ftp_end_point: bool, optional
        """
        url, log_key = self._get_url_for_zip_file(identifier, from_ftp_end_point)
        directory_url = self.get_parent_directory(path_to_save)
        request_handler = requests.get(url)
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        file_exits = self.check_if_content_is_zip(request_handler)
        if file_exits:
            self.extract_zip_files(
                request_handler.content, path_to_save)
        else:
            logging.warning("%s files not found for %s", log_key, identifier)

    def check_if_content_is_zip(self, request_handler):
        """Checks if content in request object is a zip

        :param request_handler: request object for the given zip
        :type request_handler: request object
        :return: if zip file exits
        :rtype: bool
        """
        file_exits=False
        for chunk in request_handler.iter_content(chunk_size=128):
            if len(chunk) > 0:
                file_exits = True
                break
        return file_exits

    def _get_url_for_zip_file(self, identifier, from_ftp_end_point):
        if from_ftp_end_point:
            key = "PMCxxxx" + identifier[-3:]
            url = self.zipurl.format(key=key, identifier=identifier)
            log_key = "zip"
        else:
            url = self.suppurl.format(identifier=identifier)
            log_key = SUPPLEMENTARY
        return url,log_key

    def extract_zip_files(self, byte_content_to_extract_from, destination_url):
        """Extracts zip file to destination_url

        :param byte_content_to_extract_from: byte content to extract from
        :type byte_content_to_extract_from: bytes
        :param destination_url: path to save the extracted zip files to
        :type destination_url: string
        """
        try:
            z = zipfile.ZipFile(io.BytesIO(byte_content_to_extract_from))
            self.check_or_make_directory(destination_url)
            z.extractall(destination_url)
            logging.info("Extracted the files for this paper")
        except zipfile.BadZipFile as exception:
            logging.warning("files not found for this paper")
            logging.debug(exception)

    def _make_initial_columns_for_paper_dict(self, key_for_dict, resultant_dict):
        resultant_dict[key_for_dict] = {}
        self._add_download_status_keys(key_for_dict, resultant_dict)
        return resultant_dict

    @staticmethod
    def _add_download_status_keys(key_for_dict, resultant_dict):
        resultant_dict[key_for_dict][DOWNLOADED] = False
        resultant_dict[key_for_dict][PDF_DOWNLOADED] = False
        resultant_dict[key_for_dict][JSONDOWNLOADED] = False
        resultant_dict[key_for_dict][CSVMADE] = False
        resultant_dict[key_for_dict][HTMLMADE] = False

    def make_csv_for_dict(self, metadata_dictionary, name_main_result_file, name_result_file_for_paper):
        """
        Writes csv content for the given dictionary to disk 

        :param metadata_dictionary: dictionary to write the content for
        :type metadata_dictionary: dict
        :param name_main_result_file: name of the main result file (eg. eupmc-results.xml)
        :type name_main_result_file: string
        :param name_result_file_for_paper: name of the result file for a paper
        :type name_result_file_for_paper: string
        """
        logging.info("Making csv files for metadata at %s", os.getcwd())
        df = self._get_dataframe_without_additional_pygetpapers_attributes(metadata_dictionary)
        self.write_or_append_to_csv(df, name_main_result_file)
        self._make_csv_xml_or_html(name_result_file_for_paper,metadata_dictionary,makecsv=True)

    def _make_csv_xml_or_html(self,name_result_file_for_paper,metadata_dictionary,makecsv=False,makexml=False,makehtml=False):
        """Write csv, html or html content for papers in metadata_dictionary

        :param name_result_file_for_paper: name of the result file for a paper
        :type name_result_file_for_paper: string
        :param metadata_dictionary: Dictionary containing papers
        :type metadata_dictionary: dict
        :param makecsv: whether to get csv 
        :type makecsv: bool
        :param makehtml: whether to get html 
        :type makehtml: bool
        :param makexml: whether to get xml 
        :type makexml: bool
        """
        paper = 0
        dict_to_use = self.removing_added_attributes_from_dictionary(metadata_dictionary)
        for result in tqdm(dict_to_use):
            paper += 1
            result_encoded = self.url_encode_id(result)
            url = os.path.join(os.getcwd(), result_encoded, name_result_file_for_paper)
            self.check_or_make_directory(
                os.path.join(os.getcwd(), result_encoded))
            df_for_paper = self._make_dataframe_for_paper_dict(
                result, dict_to_use)
            if makecsv:
                self.write_or_append_to_csv(df_for_paper, url)
                metadata_dictionary[result][CSVMADE] = True
                logging.debug("Wrote csv files for paper %s", paper)
            if makehtml:
                self.make_html_from_dataframe(df_for_paper, url)
                metadata_dictionary[result][HTMLMADE] = True
                logging.debug("Wrote html files for paper %s", paper)
            if makexml:
                total_xml_of_paper = dict2xml(
                dict_to_use[result], wrap="root", indent="   "
                )
                xmlurl_of_paper = os.path.join(
                    os.getcwd(), result_encoded, name_result_file_for_paper)
                with open(xmlurl_of_paper, "w", encoding="utf-8") as file_handler:
                    file_handler.write(total_xml_of_paper)
                logging.debug("Wrote xml files for paper %s", paper)

    def make_html_for_dict(self, metadata_dictionary, name_main_result_file, name_result_file_for_paper):
        """Writes html content for the given dictionary to disk 

        :param metadata_dictionary: dictionary to write the content for
        :type metadata_dictionary: dict
        :param name_main_result_file: name of the main result file (eg. eupmc-results.xml)
        :type name_main_result_file: string
        :param name_result_file_for_paper: name of the result file for a paper
        :type name_result_file_for_paper: string
        """
        logging.info("Making html files for metadata at %s", os.getcwd())
        htmlurl = os.path.join(os.getcwd(), name_main_result_file)
        df = self._get_dataframe_without_additional_pygetpapers_attributes(metadata_dictionary)
        self.make_html_from_dataframe(df, htmlurl)
        self._make_csv_xml_or_html(name_result_file_for_paper,metadata_dictionary,makehtml=True)


    def _get_dataframe_without_additional_pygetpapers_attributes(self, metadata_dictionary):
        dict_to_use = self.removing_added_attributes_from_dictionary(metadata_dictionary)
        df = pd.DataFrame.from_dict(dict_to_use)
        return df

    def make_xml_for_dict(self, metadata_dictionary, name_main_result_file, name_result_file_for_paper):
        """Writes xml content for the given dictionary to disk 

        :param metadata_dictionary: dictionary to write the content for
        :type metadata_dictionary: dict
        :param name_main_result_file: name of the main result file (eg. eupmc-results.xml)
        :type name_main_result_file: string
        :param name_result_file_for_paper: name of the result file for a paper
        :type name_result_file_for_paper: string
        """
        dict_to_use = self.removing_added_attributes_from_dictionary(metadata_dictionary)
        total_xml = dict2xml(dict_to_use, wrap="root", indent="   ")
        logging.info("Making xml files for metadata at %s", os.getcwd())
        xmlurl = os.path.join(os.getcwd(), name_main_result_file)
        with open(xmlurl, "w", encoding="utf-8") as file_handler:
            file_handler.write(total_xml)
        paper = 0
        self._make_csv_xml_or_html(name_result_file_for_paper,metadata_dictionary,paper,makexml=True)

    def handle_creation_of_csv_html_xml(
        self, makecsv, makehtml, makexml, metadata_dictionary, name
    ):
        """Writes csv, html, xml for given conditions

        :param makecsv: whether to get csv 
        :type makecsv: bool
        :param makehtml: whether to get html 
        :type makehtml: bool
        :param makexml: whether to get xml 
        :type makexml: bool
        :param metadata_dictionary: dictionary to write the content for
        :type metadata_dictionary: dict
        :param name: name of the file to save
        :type name: string
        """
        
        if makecsv:
            self.make_csv_for_dict(
               metadata_dictionary, f"{name}s.csv", f"{name}.csv")
        if makehtml:
            self.make_html_for_dict(
                metadata_dictionary, f"{name}s.html", f"{name}.html")
        if makexml:
            self.make_xml_for_dict(metadata_dictionary, f"{name}s.xml", f"{name}.xml")

    @staticmethod
    def url_encode_id(doi_of_paper):
        """Encodes the doi of paper in a file savable name

        :param doi_of_paper: doi 
        :type doi_of_paper: string
        :return: url encoded doi
        :rtype: string
        """
        url_encoded_doi_of_paper = doi_of_paper.replace(
            "\\", "_").replace("/", "_")
        return url_encoded_doi_of_paper

    @staticmethod
    def get_version():
        """Gets version from the configuration file

        :return: version of pygetpapers as described in the configuration file
        :rtype: string
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
    def _make_dict_from_list(metadata_list, paper_key):
        
        paper_by_key = {}
        for paper in metadata_list:
            paper_by_key[paper[paper_key]] = paper
        return paper_by_key

    def _make_metadata_json_files_for_paper(self, returned_dict, updated_dict, paper_key, name_of_file):
        
        self.dumps_json_to_given_path(f"{name_of_file}s.json", updated_dict)
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
                self.dumps_json_to_given_path(path_to_save_metadata, dict_of_paper)
                logging.debug(
                    "Wrote metadata file for the paper %s", paper_numer)

    def _adds_new_results_to_metadata_dictionary(
        self, cursor_mark, previous_metadata_dictionary, total_number_of_results, update=None
    ):
        
        new_dict_to_return = {
            TOTAL_JSON_OUTPUT: previous_metadata_dictionary,
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
        """Gets the url of metadata file (eg. eupmc-results.json) from the current working directory

        :return: path of the master metadata file
        :rtype: string
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

    