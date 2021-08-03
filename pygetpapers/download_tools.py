import configparser
import json
import time
import zipfile
import io
import copy
import os
import logging
import requests
import pandas as pd
import xmltodict
from tqdm import tqdm
from dict2xml import dict2xml


class DownloadTools:
    """Generic tools for retrieving literature"""

    def __init__(self, api):
        """[summary]

        :param api: [description]
        :type api: [type]
        """
        with open(
            os.path.join(os.path.dirname(__file__), "config.ini")
        ) as file_handler:
            config_file = file_handler.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_string(config_file)

        self.posturl = config.get(api, "posturl")
        self.citationurl = config.get(api, "citationurl")
        self.referencesurl = config.get(api, "referencesurl")
        self.xmlurl = config.get(api, "xmlurl")
        self.zipurl = config.get(api, "zipurl")
        self.suppurl = config.get(api, "suppurl")

    def postquery(self, headers, payload):
        """

        :param headers: headers that will be sent to eupmc rest api
        :param payload: payload that will be sent to eupmc rest api
        :returns: Python dictionary containting the output got from eupmc rest api

        """
        logging.debug("*/RESTful request for fulltext.xml (D)*/")
        start = time.time()
        request_handler = requests.post(
            self.posturl, data=payload, headers=headers)
        stop = time.time()
        logging.debug("*/Got the Query Result */")
        logging.debug("Time elapsed: %s", (stop - start))
        return xmltodict.parse(request_handler.content)

    @staticmethod
    def check_or_make_directory(directory_url):
        """Checks if the directory exists. If not, makes the directory

        :param directory_url: directory url to check

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
        """

        :param cursormark: the cursonmark for the rest api page.
        :param page_size: the size of each page in the output.
        :param query: the query passed on to payload
        :param synonym: whether synonym should be or not (Default value = True)
        :returns: headers': headers, 'payload': payload}
        :rtype: Python dictionary containting headers and payload in the format

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
        """Writes the csv file or appends to an existing one

        :param df_transposed: dataframe to write
        :param name: Default value = 'europe_pmc.csv')

        """
        path = os.path.join(str(os.getcwd()), name)
        if os.path.exists(path):
            df_transposed.to_csv(path, mode="a", header=False)
        else:
            df_transposed.to_csv(path)

    @staticmethod
    def writexml(directory_url, destination_url, content):
        """writes xml to the destination

        :param directory_url: directory containg destination
        :param destination_url: path to write the xml to
        :param content: xml content

        """
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        with open(destination_url, "wb") as file_handler:
            file_handler.write(content)

    @staticmethod
    def make_dict_for_csv(resultant_dict):
        """removes the fields downloaded, pdfdownloaded,csvmade for the resultant_dict

        :param resultant_dict: dictionary to remove the fields
        :returns: resultant_dict_for_csv

        """
        resultant_dict_for_csv = copy.deepcopy(resultant_dict)
        for paper in resultant_dict_for_csv:
            paper_dict = resultant_dict_for_csv[paper]
            if "downloaded" in paper_dict:
                paper_dict.pop("downloaded")
            if "pdfdownloaded" in paper_dict:
                paper_dict.pop("pdfdownloaded")
            if "jsondownloaded" in paper_dict:
                paper_dict.pop("jsondownloaded")
            if "csvmade" in paper_dict:
                paper_dict.pop("csvmade")
            if "htmlmade" in paper_dict:
                paper_dict.pop("htmlmade")
        return resultant_dict_for_csv

    @staticmethod
    def write_content_to_destination(url, destination):
        """Writes content from url to destination

        :param url: Url to get content from
        :param destination: destination to write content to

        """
        with open(destination, "wb") as file:
            response = requests.get(url)
            file.write(response.content)

    @staticmethod
    def makejson(path, final_xml_dict):
        """Writes json of final_xml_dict to path

        :param path: path to write json to
        :param final_xml_dict: python dictionary to make the json from

        """
        append_write = "w"
        with open(path, append_write, encoding="utf-8") as file_handler:
            json.dump(final_xml_dict, file_handler)

    @staticmethod
    def clean_dict_for_csv(paperdict):
        """Removes the fields pdfdownloaded , jsondownloaded , csvmade from dictionary of paper

        :param paperdict: dictionary to remove fields from

        """
        dict_to_write = dict(paperdict)
        dict_to_write.pop("pdfdownloaded")
        dict_to_write.pop("jsondownloaded")
        dict_to_write.pop("csvmade")
        return dict_to_write

    @staticmethod
    def make_dataframe_for_paper_dict(result, return_dict):
        """

        :param result: 
        :param return_dict:

        """
        dict_for_df = {k: [v] for k, v in return_dict[result].items()}
        df_for_paper = pd.DataFrame(dict_for_df)
        return df_for_paper

    @staticmethod
    def conditions_to_download(paperdict):
        """Writes the conditions to download pdf, json and csv

        :param paperdict: dictionary to write rules for

        """
        condition_to_down = False
        condition_to_download_pdf = False
        condition_to_download_json = False
        condition_to_download_csv = False
        condition_to_html = False
        if not paperdict["downloaded"]:
            condition_to_down = True
        if not paperdict["pdfdownloaded"]:
            condition_to_download_pdf = True
        if not paperdict["jsondownloaded"]:
            condition_to_download_json = True
        if not paperdict["csvmade"]:
            condition_to_download_csv = True
        if not paperdict["htmlmade"]:
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
        """Returns a <a> Html String

        :param link: link for href

        """
        tag_to_return = f'<a target="_blank" href="{link}">Link</a>'
        if str(link) == "nan":
            tag_to_return = "Not Found"
        return tag_to_return

    def getcitations(self, pmcid, source):
        """Gets citations for the paper of pmcid

        :param pmcid: pmcid to get the citations
        :param source: source to get the citations from
        :returns: citations xml

        """
        request_handler = requests.get(
            self.citationurl.format(source=source, pmcid=pmcid)
        )
        return request_handler.content

    def getreferences(self, pmcid, source):
        """Gets references for the paper of pmcid

        :param pmcid: pmcid to get the references
        :param source: source to get the references from
        :returns: references xml

        """
        request_handler = requests.get(
            self.referencesurl.format(source=source, pmcid=pmcid)
        )
        return request_handler.content

    @staticmethod
    def add_scrollbar(text):
        """Makes div scrollable

        :param text: text to wrap

        """
        return f'<div id="table">{text}</div>'

    def make_html_from_dataframe(self, dataframe, url):
        """Writes html from pandas dataframe

        :param dataframe: Dataframe to make html from
        :param url: URL to write html to

        """
        dataframe = dataframe.T
        try:
            dataframe = dataframe.drop(columns=["full", "htmlmade"])
        except Exception as exception:
            logging.debug(exception)
        if "htmllinks" in dataframe:
            try:
                dataframe["htmllinks"] = dataframe["htmllinks"].apply(
                    lambda x: self.make_clickable(x)
                )
            except Exception as exception:
                logging.debug(exception)
        if "pdflinks" in dataframe:
            try:
                dataframe["pdflinks"] = dataframe["pdflinks"].apply(
                    lambda x: self.make_clickable(x)
                )
            except Exception as exception:
                logging.debug(exception)
        try:
            dataframe["abstract"] = dataframe["abstract"].apply(
                lambda x: self.add_scrollbar(x)
            )
        except Exception as exception:
            logging.debug(exception)
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
        """Writes html from python dictionary

        :param dict_to_write_html_from: dict to make html from
        :param url: URL to write html to

        """
        df = pd.Series(dict_to_write_html_from).to_frame(
            dict_to_write_html_from["full"]["pmcid"]
        )
        self.make_html_from_dataframe(df, url)

    def make_references(self, directory_url, paperid, source, referenceurl):
        """Downloads the references for the paper with pmcid (paperid) to reference url

        :param directory_url: directory containing referenceurl
        :param paperid: pmc id of the paper
        :param source: source to get the citations from
        :param referenceurl: path to write the references to

        """
        getreferences = self.getreferences(paperid, source)
        self.writexml(directory_url, referenceurl, getreferences)

    def make_citations(self, source, citationurl, directory_url, paperid):
        """Downloads the citations for the paper with pmcid (paperid) to citation url

        :param source: source to get the citations from
        :param citationurl: path to write the citations to
        :param directory_url: directory containing citationurl
        :param paperid: pmc id of the paper

        """
        getcitations = self.getcitations(paperid, source)
        self.writexml(directory_url, citationurl, getcitations)

    @staticmethod
    def readjsondata(path):
        """Reads json from path and returns python dictionary

        :param path: path to read the json from
        :returns: python dictionary for the json

        """
        with open(path) as file_handler:
            dict_from_json = json.load(file_handler)
        return dict_from_json

    @staticmethod
    def log_making_xml():
        """Logs that the xmls are being written"""

        logging.debug(
            "*/saving xml to per-document directories (CTrees) (D)*/")
        loggingurl = os.path.join(str(os.getcwd()), "*", "fulltext.xml")
        logging.info("Saving XML files to %s", loggingurl)
        logging.debug("*/Making the Request to get full text xml*/")

    def getxml(self, pmcid):
        """Makes a query for the pmcid xml to eupmc rest.

        :param pmcid: pmcid of the paper to query for
        :returns: query result

        """
        request_handler = requests.get(self.xmlurl.format(pmcid=pmcid))
        return request_handler.content

    def getsupplementaryfiles(
        self, pmcid, directory_url, destination_url, from_ftp_end_point=False
    ):
        """Downloads the supplemetary marks for the paper having pmcid

        :param pmcid: pmcid to get the supplementary files
        :param directory_url: directory containg destination
        :param destination_url: path to write the supplementary files to
        :param from_ftp_end_point: Default value = False)

        """

        log_key = "supplementary"
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
        """

        :param request_handler: param destination_url:
        :param log_key: param pmcid:
        :param destination_url: param pmcid:
        :param pmcid:

        """
        try:
            z = zipfile.ZipFile(io.BytesIO(request_handler.content))
            self.check_or_make_directory(destination_url)
            z.extractall(destination_url)
            logging.info("Wrote %s files for %s", log_key, log_key)
        except Exception as exception:
            logging.warning("%s files not found for %s", log_key, pmcid)
            logging.debug(exception)

    def make_initial_columns_for_paper_dict(self, key_for_dict, resultant_dict):
        """Writes the json and csv for searchvaraible dict

        :param key_for_dict: id of the paper for which fields will be created
        :param resultant_dict: dict in which the fields will be created
        :returns: dict with the initial fields created for pmcid

        """
        resultant_dict[key_for_dict] = {}
        self.add_keys_for_conditions(key_for_dict, resultant_dict)
        return resultant_dict

    @staticmethod
    def add_keys_for_conditions(key_for_dict, resultant_dict):
        """[summary]

        :param key_for_dict: [description]
        :type key_for_dict: [type]
        :param resultant_dict: [description]
        :type resultant_dict: [type]
        """
        resultant_dict[key_for_dict]["downloaded"] = False
        resultant_dict[key_for_dict]["pdfdownloaded"] = False
        resultant_dict[key_for_dict]["jsondownloaded"] = False
        resultant_dict[key_for_dict]["csvmade"] = False
        resultant_dict[key_for_dict]["htmlmade"] = False

    def make_csv_for_dict(self, df, return_dict, output_main, output_paper):
        """

        :param df:
        :param return_dict:
        :param output_main:
        :param output_paper:

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
            return_dict[result]["csvmade"] = True
            logging.debug("Wrote csv files for paper %s", paper)

    def make_html_for_dict(self, df, return_dict, output_main, output_paper):
        """

        :param df:
        :param return_dict:
        :param output_main:
        :param output_paper:

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
            return_dict[result]["htmlmade"] = True
            logging.debug("Wrote xml files for paper %s", paper)

    def make_xml_for_dict(self, return_dict, output_main, output_paper):
        """

        :param return_dict:
        :param output_main:
        :param output_paper:

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
        with open(
            os.path.join(os.path.dirname(__file__), "config.ini")
        ) as file_handler:
            config_file = file_handler.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_string(config_file)
        version = config.get("pygetpapers", "version")
        return version

    @staticmethod
    def make_dict_from_returned_list(total_json_output, key_in_dict):
        """[summary]

        :param total_json_output: [description]
        :type total_json_output: [type]
        :param key_in_dict: [description]
        :type key_in_dict: [type]
        :return: [description]
        :rtype: [type]
        """
        json_return_dict = {}
        for paper in total_json_output:
            json_return_dict[paper[key_in_dict]] = paper
        return json_return_dict

    def make_json_files_for_paper(self, returned_dict, updated_dict, key_in_dict, name_of_file):
        """[summary]

        :param returned_dict: [description]
        :type returned_dict: [type]
        :param key_in_dict: [description]
        :type key_in_dict: [type]
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
            if not dict_of_paper["jsondownloaded"]:
                paper_numer += 1
                doi_of_paper = dict_of_paper[key_in_dict]
                url_encoded_doi_of_paper = self.url_encode_id(doi_of_paper)
                self.check_or_make_directory(url_encoded_doi_of_paper)
                path_to_save_metadata = os.path.join(
                    str(os.getcwd()
                        ), url_encoded_doi_of_paper, f"{name_of_file}.json"
                )
                dict_of_paper["jsondownloaded"] = True
                self.makejson(path_to_save_metadata, dict_of_paper)
                logging.debug(
                    "Wrote metadata file for the paper %s", paper_numer)

    def make_dict_to_return(
        self, cursor_mark, json_return_dict, total_number_of_results, update=None
    ):
        """[summary]

        :param cursor_mark: [description]
        :type cursor_mark: [type]
        :param json_return_dict: [description]
        :type json_return_dict: [type]
        :param total_number_of_results: [description]
        :type total_number_of_results: [type]
        :param update: [description]
        :type update: [type]
        :return: [description]
        :rtype: [type]
        """
        new_dict_to_return = {
            "total_json_output": json_return_dict,
            "total_hits": total_number_of_results,
            "cursor_mark": cursor_mark,
        }

        dict_to_return_with_previous = copy.deepcopy(new_dict_to_return)
        if update:

            dict_to_return_with_previous["total_json_output"].update(
                update["total_json_output"]
            )
        return {"updated_dict": dict_to_return_with_previous, "new_results": new_dict_to_return}
