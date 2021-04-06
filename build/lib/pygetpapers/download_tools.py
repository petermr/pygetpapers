class download_tools:
    def __init__(self):
        pass

    def postquery(self, headers, payload):
        """
        :param headers: headers that will be sent to eupmc rest api

        :param payload: payload that will be sent to eupmc rest api

        :return: Python dictionary containting the output got from eupmc rest api
        """

        import xmltodict
        import logging
        import requests
        import time
        logging.debug("*/RESTful request for fulltext.xml (D)*/")
        start = time.time()
        r = requests.post(
            'https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST', data=payload, headers=headers)
        stop = time.time()
        logging.debug("*/Got the Query Result */")
        logging.debug(f"Time elapsed: {stop - start}")
        return xmltodict.parse(r.content)

    def check_or_make_directory(self, directory_url):
        '''
        Checks if the directory exists. If not, makes the directory

        :param directory_url: directory url to check
        '''
        import os
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)

    def buildquery(self, cursormark, pageSize, query, synonym=True,):
        '''
        :param cursormark: the cursonmark for the rest api page. The first cursormark of query result is '*'

        :param pageSize: the size of each page in the output.

        :param query: the query passed on to payload

        :param synonym: whether synonym should be or not

        :return: Python dictionary containting headers and payload in the format: {'headers': headers, 'payload': payload}
        '''

        import logging
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        payload = {'query': query, 'resultType': 'core',
                   'cursorMark': cursormark, 'pageSize': pageSize, 'synonym': synonym, 'format': 'xml', 'sort_PMCID': 'y'}
        logging.debug("*/submitting RESTful query (I)*/")
        return {'headers': headers, 'payload': payload}

    def write_or_append_to_csv(self, df_transposed):
        '''
        Writes the csv file or appends to an existing one

        :param df_transposed: dataframe to write
        '''
        import os
        path = os.path.join(str(os.getcwd()), 'europe_pmc.csv')
        if os.path.exists(path):
            df_transposed.to_csv(path, mode='a', header=False)
        else:
            df_transposed.to_csv(path)

    def writexml(self, directory_url, destination_url, content):
        '''
        writes xml to the destination

        :param directory_url: directory containg destination

        :param destination_url: path to write the xml to

        :param content: xml content
        '''
        import os
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        with open(destination_url, 'wb') as f:
            f.write(content)

    def make_dict_for_csv(self, resultant_dict):
        '''
        removes the fields downloaded, pdfdownloaded,csvmade for the resultant_dict to be written to a csv

        :param resultant_dict: dictionary to remove the fields

        :return: resultant_dict_for_csv
        '''
        resultant_dict_for_csv = resultant_dict
        for paper in resultant_dict_for_csv:
            paper_dict = resultant_dict_for_csv[paper]
            paper_dict.pop("downloaded")
            paper_dict.pop("pdfdownloaded")
            paper_dict.pop("jsondownloaded")
            paper_dict.pop("csvmade")
        return resultant_dict_for_csv

    def writepdf(self, url, destination):
        '''
        Writes pdf from url to destination

        :param url: Url to get pdf from

        :param destination: destination to write pdf to
        '''
        import requests
        with open(destination, "wb") as file:
            response = requests.get(url)
            file.write(response.content)

    def makejson(self, path, final_xml_dict):
        '''
        Writes json of final_xml_dict to path

        :param path: path to write json to

        :param final_xml_dict: python dictionary to make the json from
        '''
        import json
        append_write = 'w'
        with open(path, append_write) as fp:
            json.dump(final_xml_dict, fp)

    def clean_dict_for_csv(self, paperdict):
        '''
        Removes the fields pdfdownloaded , jsondownloaded , csvmade from dictionary of paper

        :param paperdict: dictionary to remove fields from
        '''
        dict_to_write = dict(paperdict)
        dict_to_write.pop('pdfdownloaded')
        dict_to_write.pop('jsondownloaded')
        dict_to_write.pop('csvmade')
        return dict_to_write

    def conditions_to_download(self, paperdict):
        '''
        Writes the conditions to download pdf, json and csv

        :param paperdict: dictionary to write rules for
        '''
        condition_to_down = paperdict["downloaded"] == False
        condition_to_download_pdf = paperdict["pdfdownloaded"] == False
        condition_to_download_json = paperdict["jsondownloaded"] == False
        condition_to_download_csv = paperdict["csvmade"] == False
        return condition_to_down, condition_to_download_csv, condition_to_download_json, condition_to_download_pdf

    def readjsondata(self, path):
        '''
        Reads json from path and returns python dictionary

        :param path: path to read the json from

        :return: python dictionary for the json
        '''
        import json
        with open(path) as f:
            object = json.load(f)
        return object

    def log_making_xml(self):
        '''
        Logs that the xmls are being written
        '''
        import logging
        import os
        logging.debug(
            "*/saving xml to per-document directories (CTrees) (D)*/")
        loggingurl = os.path.join(
            str(os.getcwd()), '*', 'fulltext.xml')
        logging.info(
            f"Saving XML files to {loggingurl}")
        logging.debug("*/Making the Request to get full text xml*/")
