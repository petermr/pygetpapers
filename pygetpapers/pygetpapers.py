class pygetpapers:

    def __init__(self, **kwargs):
        import os
        self.LOGGING_URL = os.path.join(str(os.getcwd()), '*', 'fulltext.xml')
        self.EUPMCJSON = os.path.join(str(os.getcwd()), 'eupmc_results.json')
        self.EUPMCCSVURL = os.path.join(str(os.getcwd()), 'europe_pmc.csv')
        self.TITLE = "title"
        self.AUTHORINFO = "authorinfo"
        self.JOURNALTITLE = "journaltitle"
        self.PDFLINKS = "pdflinks"
        self.HTMLLINKS = "htmllinks"
        self.PMCID = "pmcid"
        self.RESPONSE_WRAPPER = "responseWrapper"
        self.CURSOR_MARK = "nextCursorMark"
        self.directory_url = os.path.join(
            str(os.getcwd()))

    def postquery(self, headers, payload):
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

    def buildquery(self, cursormark, pageSize, query, synonym=True, ):
        import logging
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        payload = {'query': query, 'format': format, 'resultType': 'core',
                   'cursorMark': cursormark, 'pageSize': pageSize, 'synonym': synonym, 'format': 'xml',
                   'sort_self.PMCID': 'y'}
        logging.debug("*/submitting RESTful query (I)*/")
        return {'headers': headers, 'payload': payload}

    def webscrapepmc(self, query, pmccount, onlyresearcharticles=False, onlypreprints=False, onlyreviews=False):
        from selenium import webdriver
        import time
        import os
        import logging
        from selenium import webdriver
        import chromedriver_autoinstaller
        chromedriver_autoinstaller.install()
        pmcdict = {}
        size = int(pmccount)
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        webdriver = webdriver.Chrome(
            chrome_options=options
        )
        a = 0
        url = self.build_webscrape_query(
            onlypreprints, onlyresearcharticles, onlyreviews, query)
        webdriver.get(url)
        while len(pmcdict) <= size:
            time.sleep(2)
            # retrive url in headless browser
            # time.sleep(3)
            should_break = False
            results = webdriver.find_elements_by_xpath(
                "//ul[@class='separated-list']/li/div/p[3]/span")
            a, should_break = self.traverse_webscaped_information_to_get_pmcids(
                a, pmcdict, results, should_break, size)
            if a < size:
                self.go_to_next_page_of_eupmc(size, webdriver)
            elif should_break == True:
                break
            elif not (should_break):
                webdriver.quit()
                break
            time.sleep(2)

        self.check_or_make_dir()
        self.makejson(os.path.join(
            str(os.getcwd()), 'eupmc_results.json'), dict(pmcdict))
        return dict(pmcdict)

    def check_or_make_dir(self):
        import os
        if not os.path.isdir(self.directory_url):
            os.makedirs(self.directory_url)

    def go_to_next_page_of_eupmc(self, size, webdriver):
        import time
        import logging
        try:
            time.sleep(2)
            webdriver.find_element_by_xpath(
                "//span[contains(text(), 'Next')]").click()
        except:
            if size > 25:
                logging.info("Only found so many papers.")
            webdriver.quit()
            should_break = True

    def traverse_webscaped_information_to_get_pmcids(self, a, pmcdict, results, should_break, size):
        import logging
        for result in results:
            pmcid = result.text
            if 'PMC' in pmcid:
                a += 1
                if len(pmcdict) < size:
                    logging.info(f'Scraping paper no. {a}')
                    self.add_paper_pmcid_to_pmcdict(pmcdict, pmcid)
                else:
                    should_break = True
        return a, should_break

    def add_paper_pmcid_to_pmcdict(self, pmcdict, pmcid):
        name = pmcid.split()
        cleanedpmcid = name[-1]
        pmcdict[cleanedpmcid] = {}
        pmcdict[cleanedpmcid]["downloaded"] = False

    def build_webscrape_query(self, onlypreprints, onlyresearcharticles, onlyreviews, query):
        if onlyresearcharticles:
            url = f"https://europepmc.org/search?query=%28%22{query}%22%20AND%20%28%28HAS_FT%3AY%20AND%20OPEN_ACCESS%3AY%29%29%20AND%20%28%28%28SRC%3AMED%20OR%20SRC%3APMC%20OR%20SRC%3AAGR%20OR%20SRC%3ACBA%29%20NOT%20%28PUB_TYPE%3A%22Review%22%29%29%29%29%20AND%20%28%28%28SRC%3AMED%20OR%20SRC%3APMC%20OR%20SRC%3AAGR%20OR%20SRC%3ACBA%29%20NOT%20%28PUB_TYPE%3A%22Review%22%29%29%29"
        elif onlypreprints:
            url = f"https://europepmc.org/search?query={query}%20AND%20%28SRC%3APPR%29&page=1"
        elif onlyreviews:
            url = f"https://europepmc.org/search?query={query}%20%20AND%20%28PUB_TYPE%3AREVIEW%29&page=1"
        else:
            url = f'https://europepmc.org/search?query={query}%20%28IN_EPMC%3Ay%29%20AND%20%28OPEN_ACCESS%3Ay%29&page=1'
        return url

    def europepmc(self, query, size, synonym=True, externalfile=True, fulltext=True, **kwargs):
        import logging
        import json
        size = int(size)
        content = [[]]
        nextCursorMark = ['*', ]
        morepapers = True
        number_of_papers_there = 0

        Condition_to_look_for_papers = number_of_papers_there <= size and morepapers == True
        while Condition_to_look_for_papers:
            queryparams = self.buildquery(
                nextCursorMark[-1], 1000, query, synonym=synonym)
            builtquery = self.postquery(
                queryparams['headers'], queryparams['payload'])
            if self.CURSOR_MARK in builtquery[("%s" % self.RESPONSE_WRAPPER)]:
                nextCursorMark.append(
                    builtquery[self.RESPONSE_WRAPPER][self.CURSOR_MARK])
                self.reporttotalhits(builtquery)
                output_dict = json.loads(json.dumps(builtquery))
                try:
                    for paper in output_dict[self.RESPONSE_WRAPPER]["resultList"]["result"]:
                        number_of_papers_there = self.handle_update__and_addition_of_paper_to_dict(content, kwargs,
                                                                                                   number_of_papers_there,
                                                                                                   paper, size)
                except:
                    morepapers = False
                    logging.warning("Could not find more papers")
                    break
            else:
                morepapers = False
                logging.warning("Could not find more papers")
        if number_of_papers_there > size:
            content[0] = content[0][0:size]
        return content

    def handle_update__and_addition_of_paper_to_dict(self, content, kwargs, number_of_papers_there, paper, size):
        if "update" in kwargs:
            if ("%s" % self.PMCID) in paper and paper[self.PMCID] not in kwargs["update"]:
                number_of_papers_there = self.add_paper_to_content(content, number_of_papers_there,
                                                                   paper, size)
        else:
            if self.PMCID in paper:
                number_of_papers_there = self.add_paper_to_content(content, number_of_papers_there,
                                                                   paper, size)
        return number_of_papers_there

    def reporttotalhits(self, builtquery):
        import logging
        totalhits = builtquery[self.RESPONSE_WRAPPER]["hitCount"]
        logging.info(f"Total Hits are {totalhits}")

    def add_paper_to_content(self, content, number_of_papers_there, paper, size):
        if number_of_papers_there <= size:
            content[0].append(paper)
            number_of_papers_there += 1
        return number_of_papers_there

    # this is the function that will the the result from search and will download and save the files.
    def makecsv(self, searchvariable, makecsv=False, update=False):
        import json
        import logging
        resultant_dict = {}
        for paper_number, papers in enumerate(searchvariable):
            output_dict = json.loads(json.dumps(papers))
            for paper in output_dict:
                if self.PMCID in paper:
                    paperpmcid = self.write_meta_data_for_a_paper(
                        paper, paper_number, resultant_dict)
                    logging.debug(
                        f'Wrote Meta Data to a dictionary that will be written to all the chosen metadata file formats for paper {paperpmcid}')
        if update:
            resultant_dict.update(update)
        self.check_or_make_dir()
        self.makejson(self.EUPMCJSON, resultant_dict)
        resultant_dict_for_csv = resultant_dict
        for paper in resultant_dict_for_csv:
            self.pop_download_rows(resultant_dict_for_csv[paper])
        df_transposed = self.make_dataframe_from_dict(resultant_dict_for_csv)
        if makecsv:
            self.write_or_append_to_csv(df_transposed)
        return searchvariable

    def make_dataframe_from_dict(self, resultant_dict_for_csv):
        df = pd.DataFrame.from_dict(resultant_dict_for_csv, )
        df_transposed = df.T
        return df_transposed

    def write_or_append_to_csv(self, df_transposed):
        import os
        if os.path.exists(self.EUPMCCSVURL):
            df_transposed.to_csv(self.EUPMCCSVURL, mode='a', header=False)
        else:
            df_transposed.to_csv(self.EUPMCCSVURL)

    def write_meta_data_for_a_paper(self, paper, paper_number, resultant_dict):
        import logging
        paper_number += 1
        logging.debug(
            f"Reading Query Result for paper {paper_number}")
        pdfurl = []
        htmlurl = []
        self.add_html_pdf_urls_for_paper_dict(htmlurl, paper, pdfurl)
        pmcidarray = paper["pmcid"]
        resultant_dict[pmcidarray] = {}
        dict_for_paper = self.initial_parameters_for_dict_for_papers(
            paper, resultant_dict)
        self.conditions_to_check_if_fields_paper_dict(
            dict_for_paper, htmlurl, paper, paper_number, pdfurl)
        paperpmcid = pmcidarray
        return paperpmcid

    def add_html_pdf_urls_for_paper_dict(self, htmlurl, paper, pdfurl):
        for x in paper["fullTextUrlList"]["fullTextUrl"]:
            if x["documentStyle"] == "pdf" and x["availability"] == "Open access":
                pdfurl.append(x["url"])

            if x["documentStyle"] == "html" and x["availability"] == "Open access":
                htmlurl.append(x["url"])

    def conditions_to_check_if_fields_paper_dict(self, dict_for_paper, htmlurl, paper, paper_number, pdfurl):
        import logging
        if ("%s" % self.HTMLLINKS) in dict_for_paper:
            dict_for_paper[self.HTMLLINKS] = htmlurl[0]
        if ("%s" % self.PDFLINKS) in dict_for_paper:
            dict_for_paper[self.PDFLINKS] = pdfurl[0]
        if ("%s" % self.JOURNALTITLE) in dict_for_paper:
            dict_for_paper[self.JOURNALTITLE] = paper["journalInfo"]["journal"][self.TITLE]
        else:
            logging.warning(
                "journalInfo not found for paper", paper_number)
        if self.AUTHORINFO in dict_for_paper:
            dict_for_paper[("%s" % self.AUTHORINFO)
                           ] = paper["authorList"]["author"][0]['fullName']
        else:
            logging.warning(
                f"Author list not found for paper {paper_number}")
        if self.TITLE in dict_for_paper:
            dict_for_paper[("%s" % self.TITLE)] = paper[self.TITLE]
        else:
            logging.warning(
                f"Title not found for paper {paper_number}")

    def initial_parameters_for_dict_for_papers(self, paper, resultant_dict):
        dict_for_paper = resultant_dict[paper["pmcid"]]
        dict_for_paper["downloaded"] = False
        dict_for_paper["pdfdownloaded"] = False
        dict_for_paper["jsondownloaded"] = False
        dict_for_paper["csvmade"] = False
        dict_for_paper["full"] = paper
        return dict_for_paper

    def pop_download_rows(self, dictionary):
        dictionary.pop("downloaded")
        dictionary.pop("pdfdownloaded")
        dictionary.pop("jsondownloaded")
        dictionary.pop("csvmade")

    def getxml(self, pmcid):
        import requests
        import logging
        r = requests.get(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML")
        return r.content

    def getsupplementaryfiles(self, pmcid, directory_url, destination_url):
        import requests
        import os
        import logging
        r = requests.get(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles", stream=True)
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        with open(destination_url, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        logging.debug(f"Wrote supplementary files for {pmcid}")

    def getreferences(self, pmcid, source):
        import requests
        import logging
        r = requests.get(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{pmcid}/references?page=1&pageSize=1000&format=xml")
        return r.content

    def getcitations(self, pmcid, source):
        import requests
        r = requests.get(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{pmcid}/citations?page=1&pageSize=1000&format=xml")
        return r.content

    '''
    def getdatabaselinks(self, pmcid):
        import requests
        import logging
        r = requests.get(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles")
        return r

    def getdatalinks(self, pmcid):
        import requests
        import logging
        r = requests.get(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles")
        return r
    '''

    def writexml(self, directory_url, destination_url, content):
        import os
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        with open(destination_url, 'wb') as f:
            f.write(content)

    def writepdf(self, url, destination):
        import requests
        with open(destination, "wb") as file:
            response = requests.get(url)
            file.write(response.content)

    def makejson(self, path, final_xml_dict):
        import json
        append_write = 'w'
        with open(path, append_write) as fp:
            json.dump(final_xml_dict, fp)

    def makexmlfiles(self, final_xml_dict, getpdf=False, makecsv=False, makexml=False, references=False,
                     citations=False, supplementaryFiles=False):
        import logging
        import pandas as pd
        import os
        import time
        self.log_if_xml_is_being_written(makexml)
        for paper_number, paper in enumerate(final_xml_dict):
            start = time.time()
            paper_number += 1
            pmcid = paper
            tree = self.getxml(pmcid)
            urls = self.make_destination_urls(pmcid)
            paper_ = final_xml_dict[paper]
            condition_to_download_json, condition_to_download_paper, condition_to_download_pdf_of_paper, condition_to_make_csv = self.make_conditions_to_download(
                getpdf, makecsv, makexml, paper_)
            if references:
                self.make_references(
                    urls["directory_url"], paper_, pmcid, references, urls["referenceurl"])
            if citations:
                self.makecitations(
                    citations, urls["citationurl"], urls["directory_url"], paper_, pmcid)
            if supplementaryFiles:
                self.getsupplementaryfiles(
                    paper_["full"]["id"], urls["directory_url"], urls["supplementaryfilesurl"])

            if not os.path.isdir(urls["directory_url"]):
                os.makedirs(urls["directory_url"])
            if condition_to_download_paper:
                self.writexml(urls["directory_url"],
                              urls["destination_url"], tree)
                logging.info(
                    f"*/Wrote xml for {pmcid}/")
                paper_["downloaded"] = True
            if condition_to_download_pdf_of_paper:
                self.writepdf(
                    paper_["pdflinks"], urls["pdf_destination"])
                paper_["pdfdownloaded"] = True
                logging.info(
                    f"Wrote the pdf file for {pmcid}")
            else:
                logging.info(
                    f"Could not find the pdf url for {pmcid}")
            dict_to_write = dict(paper_)
            self.pop_download_rows(dict_to_write)
            if condition_to_download_json:
                self.makejson(urls["jsonurl"], dict_to_write)
                paper_["jsondownloaded"] = True
            if condition_to_make_csv:
                df = pd.Series(dict_to_write).to_frame(
                    'Info_By_EuropePMC_Api')
                df.to_csv(os.path.join(
                    str(os.getcwd()), pmcid, "fulltext.csv"))
                paper_["csvmade"] = True
            self.makejson(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'), final_xml_dict)
            stop = time.time()
            logging.debug(f"Time elapsed: {stop - start}")
            logging.debug(f"*/Updating the json*/\n")

    def make_conditions_to_download(self, getpdf, makecsv, makexml, paper_):
        condition_to_download_json = paper_["jsondownloaded"] == False
        condition_to_make_csv = paper_["csvmade"] == False and makecsv
        condition_to_download_paper = paper_["downloaded"] == False and makexml
        condition_to_download_pdf_of_paper = paper_[
            "pdfdownloaded"] == False and getpdf and "pdflinks" in paper_ and len(
            paper_["pdflinks"]) > 0
        return condition_to_download_json, condition_to_download_paper, condition_to_download_pdf_of_paper, condition_to_make_csv

    def make_destination_urls(self, pmcid):
        import os
        directory_url = os.path.join(str(os.getcwd()), pmcid)
        destination_url = os.path.join(
            directory_url, "fulltext.xml")
        jsonurl = os.path.join(
            directory_url, "eupmc_result.json")
        referenceurl = os.path.join(
            directory_url, "references.xml")
        citationurl = os.path.join(
            directory_url, "citation.xml")
        supplementaryfilesurl = os.path.join(
            directory_url, "supplementaryfiles.zip")
        pdf_destination = os.path.join(
            str(os.getcwd()), pmcid, "fulltext.pdf")
        return {"citationurl": citationurl, "destination_url": destination_url, "directory_url": directory_url,
                "jsonurl": jsonurl, "referenceurl": referenceurl, "supplementaryfilesurl": supplementaryfilesurl,
                "pdf_destination": pdf_destination}

    def makecitations(self, citations, citationurl, directory_url, paper_, pmcid):
        import logging
        getcitations = self.getcitations(
            paper_["full"]["id"], citations)
        self.writexml(directory_url, citationurl, getcitations)
        logging.info(f"Made Citations for {pmcid}")

    def make_references(self, directory_url, paper_, pmcid, references, referenceurl):
        import logging
        getreferences = self.getreferences(
            paper_["full"]["id"], references)
        self.writexml(directory_url, referenceurl, getreferences)
        logging.info(f"Made references for {pmcid}")

    def log_if_xml_is_being_written(self, makexml):
        import logging
        if makexml:
            logging.debug(
                "*/saving xml to per-document directories (CTrees) (D)*/")
            loggingurl = self.LOGGING_URL
            logging.info(
                f"Saving XML files to {loggingurl}")
            logging.debug("*/Making the Request to get full text xml*/")

    def readjsondata(self, path):
        import json
        with open(path) as f:
            object = json.load(f)
        return object

    def apipaperdownload(self, query, size, onlymakejson=False, getpdf=False, makecsv=False, makexml=False,
                         references=False, citations=False, supplementaryFiles=False, synonym=True):
        import os
        query_result = self.europepmc(query, size, synonym=synonym)
        self.makecsv(query_result, makecsv=makecsv)

        if not (onlymakejson):
            read_json = self.readjsondata(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'))
            self.makexmlfiles(read_json, getpdf=getpdf, makecsv=makecsv, makexml=makexml,
                              references=references, citations=citations, supplementaryFiles=supplementaryFiles)

    def scrapingpaperdownload(self, query, size, onlyresearcharticles=False, onlypreprints=False, onlyreviews=False,
                              onlymakejson=False, makexml=False, references=False, citations=False,
                              supplementaryFiles=False, synonym=True):
        query_result = self.webscrapepmc(
            query, size, onlyresearcharticles=onlyresearcharticles, onlypreprints=onlypreprints,
            onlyreviews=onlyreviews)

        if not (onlymakejson):
            self.makexmlfiles(query_result, makexml=makexml,
                              references=references, citations=citations, supplementaryFiles=supplementaryFiles)

    def updatecorpus(self, query, original_json, size, onlymakejson=False, getpdf=False, makecsv=False, makexml=False,
                     references=False, citations=False, supplementaryFiles=False, synonym=True):
        import os
        query_result = self.europepmc(
            query, size, update=original_json, synonym=synonym)
        self.makecsv(query_result, makecsv=makecsv,
                     update=original_json)
        if not (onlymakejson):
            read_json = self.readjsondata(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'))
            self.makexmlfiles(read_json, getpdf=getpdf,
                              makecsv=makecsv, makexml=makexml, references=references, citations=citations,
                              supplementaryFiles=supplementaryFiles)

    def noexecute(self, query, size, synonym=True):
        import logging
        builtqueryparams = self.buildquery(
            '*', 25, query, synonym=synonym)
        result = self.postquery(
            builtqueryparams['headers'], builtqueryparams['payload'])
        totalhits = result['responseWrapper']['hitCount']
        logging.info(f'Total number of hits for the query are {totalhits}')

    def handlecli(self):
        version = "0.0.2.1"
        import argparse
        import os
        import logging
        import sys
        parser = argparse.ArgumentParser(
            description=f"Welcome to Pygetpapers version {version}. -h or --help for help")
        parser.add_argument("-v", "--version",
                            default=False, action="store_true", help="output the version number")
        parser.add_argument("-q", "--query",
                            type=str, default=False,
                            help="query string transmitted to repository API. Eg. 'Artificial Intelligence' or 'Plant Parts'. To escape special characters within the quotes, use backslash. The query to be quoted in either single or double quotes. ")

        parser.add_argument("-o", "--output",
                            type=str, help="output directory (Default: current working directory)", default=os.getcwd())
        parser.add_argument("-x", "--xml", default=False, action='store_true',
                            help="download fulltext XMLs if available")
        parser.add_argument("-p", "--pdf", default=False, action='store_true',
                            help="download fulltext PDFs if available")
        parser.add_argument("-s", "--supp", default=False, action='store_true',
                            help="download supplementary files if available	")
        parser.add_argument("--references",
                            type=str, default=False,
                            help="Download references if available. Requires source for references (AGR,CBA,CTX,ETH,HIR,MED,PAT,PMC,PPR).")
        parser.add_argument("-n", "--noexecute", default=False, action='store_true',
                            help="report how many results match the query, but don't actually download anything")

        parser.add_argument("--citations", type=str, default=False,
                            help="Download citations if available. Requires source for citations (AGR,CBA,CTX,ETH,HIR,MED,PAT,PMC,PPR).")
        parser.add_argument(
            "-l", '--loglevel',
            default="info",
            help=(
                "Provide logging level. "
                "Example --log warning <<info,warning,debug,error,critical>>', default='info'"),
        )
        parser.add_argument("-f", "--logfile", default=False,
                            type=str,
                            help="save log to specified file in output directory as well as printing to terminal")
        parser.add_argument("-k", "--limit", default=100,
                            type=int, help="maximum number of hits (default: 100)")

        parser.add_argument('-r', "--restart", default=False,
                            type=str,
                            help="Reads the json and makes the xml files. Takes the path to the json as the input")

        parser.add_argument("-u", "--update", default=False,
                            type=str,
                            help="Updates the corpus by downloading new papers. Requires -k or --limit (If not provided, default will be used) and -q or --query (must be provided) to be given. Takes the path to the json as the input.")
        parser.add_argument("--onlyquery", action='store_true',
                            help="Saves json file containing the result of the query in storage. The json file can be given to --restart to download the papers later.")
        parser.add_argument("-c", "--makecsv", default=False, action='store_true',
                            help="Stores the per-document metadata as csv. Works only with --api method.")
        parser.add_argument("--synonym", default=False, action='store_true',
                            help="Results contain synonyms as well.")
        '''
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--api', action='store_true',
                           help="Get papers using the official EuropePMC api")
        # Have to check with EuropePMC's policy about webscraping
        group.add_argument('--webscraping', action='store_true',
                           help="Get papers using the scraping EuropePMC. Also supports getting only research papers, preprints or review papers.")
        cogroup = parser.add_mutually_exclusive_group()
        cogroup.add_argument('--onlyresearcharticles',
                             action='store_true', help="Get only research papers (Only works with --webscraping)")
        cogroup.add_argument(
            '--onlypreprints', action='store_true', help="Get only preprints  (Only works with --webscraping)")
        cogroup.add_argument(
            '--onlyreviews', action='store_true', help="Get only review papers  (Only works with --webscraping)")
        '''
        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit()
        args = parser.parse_args()

        if os.path.exists(args.output):
            os.chdir(args.output)
        else:
            os.makedirs(args.output)
            os.chdir(args.output)
        levels = {
            'critical': logging.CRITICAL,
            'error': logging.ERROR,
            'warn': logging.WARNING,
            'warning': logging.WARNING,
            'info': logging.INFO,
            'debug': logging.DEBUG
        }
        level = levels.get(args.loglevel.lower())
        if args.logfile:
            self.handle_logging_to_file(args, level)

        else:
            logging.basicConfig(
                level=level, format='%(levelname)s: %(message)s')

        if not args.query:
            logging.warning('Please specify a query')
            sys.exit(1)
        if args.noexecute:
            self.noexecute(args.query, 100, synonym=args.synonym)
        elif args.version:
            logging.info(version)
        elif args.restart:
            self.handle_restart(args)
        elif args.update:
            read_json = self.readjsondata(args.update)
            os.chdir(os.path.dirname(args.update))
            self.updatecorpus(args.query, read_json, args.limit, getpdf=args.pdf,
                              makecsv=args.makecsv, makexml=args.xml, references=args.references,
                              citations=args.citations, supplementaryFiles=args.supp, synonym=args.synonym)
        else:
            if args.query:
                self.apipaperdownload(args.query, args.limit,
                                      onlymakejson=args.onlyquery, getpdf=args.pdf, makecsv=args.makecsv,
                                      makexml=args.xml, references=args.references, citations=args.citations,
                                      supplementaryFiles=args.supp, synonym=args.synonym)
        # Have to check with EuropePMC's policy about webscraping

        '''
        elif args.webscraping:
            self.scrapingpaperdownload(args.query, args.limit, onlyresearcharticles=args.onlyresearcharticles,
                                       onlypreprints=args.onlypreprints, onlyreviews=args.onlyreviews, onlymakejson=args.onlyquery)
        '''

    def handle_restart(self, args):
        import os
        import logging
        read_json = self.readjsondata(args.restart)
        os.chdir(os.path.dirname(os.path.dirname(args.restart)))
        self.makexmlfiles(read_json, getpdf=args.pdf, makecsv=args.makecsv, makexml=args.xml,
                          references=args.references, citations=args.citations, supplementaryFiles=args.supp)

    def handle_logging_to_file(self, args, level):
        import logging
        logging.basicConfig(filename=args.logfile,
                            level=level, filemode='w')
        console = logging.StreamHandler()
        console.setLevel(level)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)
        logging.info(f'Making log file at {args.logfile}')


def main():
    callpygetpapers = pygetpapers()
    callpygetpapers.handlecli()


# This is one approach of going about with things
'''

callgetpapers = pygetpapers()
query = "artificial intelligence"
numberofpapers = 210
callgetpapers.apipaperdownload(query, numberofpapers)
callgetpapers.scrapingpaperdownload(
    query, numberofpapers, onlyresearcharticles=True)
callgetpapers.scrapingpaperdownload(query, numberofpapers, onlyreviews=True)
callgetpapers.scrapingpaperdownload(query, numberofpapers)
'''

if __name__ == "__main__":
    main()
