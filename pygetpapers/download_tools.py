class download_tools:
    """ """

    def __init__(self, api):
        import configparser
        import logging
        import os
        with open(os.path.join(os.path.dirname(__file__), "config.ini")) as f:
            config_file = f.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_string(config_file)

        try:
            self.posturl = config.get(api, "posturl")
            self.citationurl = config.get(api, "citationurl")
            self.referencesurl = config.get(api, "referencesurl")
            self.xmlurl = config.get(api, "xmlurl")
            self.zipurl = config.get(api, "zipurl")
            self.suppurl = config.get(api, "suppurl")
        except:
            logging.debug('API using wrapper')

    def postquery(self, headers, payload):
        """

        :param headers: headers that will be sent to eupmc rest api
        :param payload: payload that will be sent to eupmc rest api
        :returns: Python dictionary containting the output got from eupmc rest api

        """

        import xmltodict
        import logging
        import requests
        import time
        logging.debug("*/RESTful request for fulltext.xml (D)*/")
        start = time.time()
        r = requests.post(
            self.posturl, data=payload, headers=headers)
        stop = time.time()
        logging.debug("*/Got the Query Result */")
        logging.debug(f"Time elapsed: {stop - start}")
        return xmltodict.parse(r.content)

    def check_or_make_directory(self, directory_url):
        """Checks if the directory exists. If not, makes the directory

        :param directory_url: directory url to check

        """
        import os
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)

    def buildquery(self, cursormark, pageSize, query, synonym=True,):
        """

        :param cursormark: the cursonmark for the rest api page. The first cursormark of query result is '*'
        :param pageSize: the size of each page in the output.
        :param query: the query passed on to payload
        :param synonym: whether synonym should be or not (Default value = True)
        :returns: headers': headers, 'payload': payload}
        :rtype: Python dictionary containting headers and payload in the format

        """

        import logging
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        payload = {'query': query, 'resultType': 'core',
                   'cursorMark': cursormark, 'pageSize': pageSize, 'synonym': synonym, 'format': 'xml', 'sort_PMCID': 'y'}
        logging.debug("*/submitting RESTful query (I)*/")
        return {'headers': headers, 'payload': payload}

    def write_or_append_to_csv(self, df_transposed):
        """Writes the csv file or appends to an existing one

        :param df_transposed: dataframe to write

        """
        import os
        path = os.path.join(str(os.getcwd()), 'europe_pmc.csv')
        if os.path.exists(path):
            df_transposed.to_csv(path, mode='a', header=False)
        else:
            df_transposed.to_csv(path)

    def writexml(self, directory_url, destination_url, content):
        """writes xml to the destination

        :param directory_url: directory containg destination
        :param destination_url: path to write the xml to
        :param content: xml content

        """
        import os
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        with open(destination_url, 'wb') as f:
            f.write(content)

    def make_dict_for_csv(self, resultant_dict):
        """removes the fields downloaded, pdfdownloaded,csvmade for the resultant_dict to be written to a csv

        :param resultant_dict: dictionary to remove the fields
        :returns: resultant_dict_for_csv

        """
        resultant_dict_for_csv = resultant_dict
        for paper in resultant_dict_for_csv:
            paper_dict = resultant_dict_for_csv[paper]
            paper_dict.pop("downloaded")
            paper_dict.pop("pdfdownloaded")
            paper_dict.pop("jsondownloaded")
            paper_dict.pop("csvmade")
        return resultant_dict_for_csv

    def writepdf(self, url, destination):
        """Writes pdf from url to destination

        :param url: Url to get pdf from
        :param destination: destination to write pdf to

        """
        import requests
        with open(destination, "wb") as file:
            response = requests.get(url)
            file.write(response.content)

    def makejson(self, path, final_xml_dict):
        """Writes json of final_xml_dict to path

        :param path: path to write json to
        :param final_xml_dict: python dictionary to make the json from

        """
        import json
        append_write = 'w'
        with open(path, append_write) as fp:
            json.dump(final_xml_dict, fp)

    def clean_dict_for_csv(self, paperdict):
        """Removes the fields pdfdownloaded , jsondownloaded , csvmade from dictionary of paper

        :param paperdict: dictionary to remove fields from

        """
        dict_to_write = dict(paperdict)
        dict_to_write.pop('pdfdownloaded')
        dict_to_write.pop('jsondownloaded')
        dict_to_write.pop('csvmade')
        return dict_to_write

    def conditions_to_download(self, paperdict):
        """Writes the conditions to download pdf, json and csv

        :param paperdict: dictionary to write rules for

        """
        condition_to_down = paperdict["downloaded"] == False
        condition_to_download_pdf = paperdict["pdfdownloaded"] == False
        condition_to_download_json = paperdict["jsondownloaded"] == False
        condition_to_download_csv = paperdict["csvmade"] == False
        condition_to_html = paperdict["htmlmade"] == False
        return condition_to_down, condition_to_download_csv, condition_to_download_json, condition_to_download_pdf, condition_to_html

    def make_clickable(self, link):
        """Returns a <a> Html String

        :param link: link for href

        """
        if str(link) == "nan":
            return "Not Found"
        else:
            return f'<a target="_blank" href="{link}">Link</a>'

    def getcitations(self, pmcid, source):
        """Gets citations for the paper of pmcid

        :param pmcid: pmcid to get the citations
        :param source: source to get the citations from
        :returns: citations xml

        """
        import requests
        r = requests.get((self.citationurl).format(
            source=source, pmcid=pmcid))
        return r.content

    def getreferences(self, pmcid, source):
        """Gets references for the paper of pmcid

        :param pmcid: pmcid to get the references
        :param source: source to get the references from
        :returns: references xml

        """
        import requests
        r = requests.get(
            (self.referencesurl).format(source=source, pmcid=pmcid))
        return r.content

    def add_scrollbar(self, text):
        """Makes div scrollable

        :param text: text to wrap

        """
        return f'<div id="table">{text}</div>'

    def make_html_from_dataframe(self, dataframe, url):
        """Writes html from pandas dataframe

        :param dataframe: Dataframe to make html from
        :param url: URL to write html to

        """
        import pandas as pd
        import logging
        dataframe = dataframe.T
        dataframe = dataframe.drop(columns=['full', 'htmlmade'])
        if "htmllinks" in dataframe:
            try:
                dataframe['htmllinks'] = dataframe['htmllinks'].apply(
                    lambda x: self.make_clickable(x))
            except:
                pass
        if "pdflinks" in dataframe:
            try:
                dataframe['pdflinks'] = dataframe['pdflinks'].apply(
                    lambda x: self.make_clickable(x))
            except:
                pass
        try:
            dataframe['abstract'] = dataframe['abstract'].apply(
                lambda x: self.add_scrollbar(x))
        except:
            logging.warning("abstract empty")
        base_html = """
    <!doctype html>
    <html>
      <head>
          <meta http-equiv="Content-type" content="text/html; charset=utf-8">
          <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/2.2.2/jquery.min.js"></script>
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
        with open(url, 'w', encoding='utf-8') as f:
            f.write(html_with_pagination)

    def make_html_from_dict(self, dict_to_write_html_from, url):
        """Writes html from python dictionary

        :param dict_to_write_html_from: dict to make html from
        :param url: URL to write html to

        """
        import pandas as pd
        df = pd.Series(dict_to_write_html_from).to_frame(
            dict_to_write_html_from['full']['pmcid'])
        self.make_html_from_dataframe(df, url)

    def readjsondata(self, path):
        """Reads json from path and returns python dictionary

        :param path: path to read the json from
        :returns: python dictionary for the json

        """
        import json
        with open(path) as f:
            object = json.load(f)
        return object

    def log_making_xml(self):
        """Logs that the xmls are being written"""
        import logging
        import os
        logging.debug(
            "*/saving xml to per-document directories (CTrees) (D)*/")
        loggingurl = os.path.join(
            str(os.getcwd()), '*', 'fulltext.xml')
        logging.info(
            f"Saving XML files to {loggingurl}")
        logging.debug("*/Making the Request to get full text xml*/")

    def getxml(self, pmcid):
        """Makes a query for the pmcid xml to eupmc rest.

        :param pmcid: pmcid of the paper to query for
        :returns: query result

        """
        import requests
        r = requests.get(
            (self.xmlurl).format(pmcid=pmcid))
        return r.content

    def getsupplementaryfiles(self, pmcid, directory_url, destination_url, fromFtpEndpoint=False):
        """Downloads the supplemetary marks for the paper having pmcid

        :param pmcid: pmcid to get the supplementary files
        :param directory_url: directory containg destination
        :param destination_url: path to write the supplementary files to
        :param fromFtpEndpoint: Default value = False)

        """
        import requests
        import os
        import logging
        import zipfile
        import io

        log_key = "supplementary"
        if fromFtpEndpoint:
            key = "PMCxxxx" + pmcid[-3:]
            path = self.zipurl.format(key=key, pmcid=pmcid)
            log_key = "zip"
        else:
            path = self.suppurl.format(pmcid=pmcid)
        r = requests.get(path)
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        file_exits = False
        for chunk in r.iter_content(chunk_size=128):
            if len(chunk) > 0:
                file_exits = True
                break
        if file_exits:
            self.extract_zip_files(r, destination_url, log_key, pmcid)
        else:
            logging.warning(f"{log_key} files not found for {pmcid}")

    def extract_zip_files(self, r, destination_url, log_key, pmcid):
        """

        :param r: param destination_url:
        :param log_key: param pmcid:
        :param destination_url: param pmcid:
        :param pmcid: 

        """
        import logging
        import zipfile
        import io
        try:
            z = zipfile.ZipFile(io.BytesIO(r.content))
            self.check_or_make_directory(destination_url)
            z.extractall(destination_url)
            logging.info(f"Wrote {log_key} files for {pmcid}")
        except:
            logging.warning(f"{log_key} files not found for {pmcid}")
