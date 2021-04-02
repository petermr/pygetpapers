class download_tools:
    def __init__(self):
        pass

    def postquery(self, headers, payload, url):
        import xmltodict
        import logging
        import requests
        import time
        logging.debug("*/RESTful request for fulltext.xml (D)*/")
        start = time.time()
        r = requests.post(
            url, data=payload, headers=headers)
        stop = time.time()
        logging.debug("*/Got the Query Result */")
        logging.debug(f"Time elapsed: {stop-start}")
        return xmltodict.parse(r.content)

    def check_or_make_directory(self, directory_url):
        import os
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)

    def buildquery(self, cursormark, pageSize, query, synonym=True,):
        import logging
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        payload = {'query': query, 'format': format, 'resultType': 'core',
                   'cursorMark': cursormark, 'pageSize': pageSize, 'synonym': synonym, 'format': 'xml', 'sort_PMCID': 'y'}
        logging.debug("*/submitting RESTful query (I)*/")
        return {'headers': headers, 'payload': payload}

    def write_or_append_to_csv(self, df_transposed, path):
        import os
        if os.path.exists(path):
            df_transposed.to_csv(path, mode='a', header=False)
        else:
            df_transposed.to_csv(path)

    def writexml(self, directory_url, destination_url, content):
        import os
        import logging
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        with open(destination_url, 'wb') as f:
            f.write(content)

    def make_dict_for_csv(self, resultant_dict):
        resultant_dict_for_csv = resultant_dict
        for paper in resultant_dict_for_csv:
            paper_dict = resultant_dict_for_csv[paper]
            paper_dict.pop("downloaded")
            paper_dict.pop("pdfdownloaded")
            paper_dict.pop("jsondownloaded")
            paper_dict.pop("csvmade")
        return resultant_dict_for_csv

    def writepdf(self, url, destination):
        import os
        import requests
        import logging
        with open(destination, "wb") as file:
            response = requests.get(url)
            file.write(response.content)

    def makejson(self, path, final_xml_dict):
        import json
        import os
        import logging
        append_write = 'w'
        with open(path, append_write) as fp:
            json.dump(final_xml_dict, fp)

    def clean_dict_for_csv(self, paperdict):
        dict_to_write = dict(paperdict)
        dict_to_write.pop('pdfdownloaded')
        dict_to_write.pop('jsondownloaded')
        dict_to_write.pop('csvmade')
        return dict_to_write

    def conditions_to_download(self, paperdict):
        condition_to_down = paperdict["downloaded"] == False
        condition_to_download_pdf = paperdict["pdfdownloaded"] == False
        condition_to_download_json = paperdict["jsondownloaded"] == False
        condition_to_download_csv = paperdict["csvmade"] == False
        return condition_to_down, condition_to_download_csv, condition_to_download_json, condition_to_download_pdf

    def make_citations(self, citations, citationurl, directory_url, paperid):
        getcitations = self.getcitations(
            paperid, citations)
        self.writexml(directory_url, citationurl, getcitations)

    def make_references(self, directory_url, paperid, references, referenceurl):
        getreferences = self.getreferences(
            paperid, references)
        self.writexml(directory_url, referenceurl, getreferences)

    def readjsondata(self, path):
        import json
        import logging
        with open(path) as f:
            object = json.load(f)
        return object

    def log_making_xml(self):
        import os
        import logging
        logging.debug(
            "*/saving xml to per-document directories (CTrees) (D)*/")
        loggingurl = os.path.join(
            str(os.getcwd()), '*', 'fulltext.xml')
        logging.info(
            f"Saving XML files to {loggingurl}")
        logging.debug("*/Making the Request to get full text xml*/")
