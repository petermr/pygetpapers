class pygetpapers:

    def __init__(self, **kwargs):
        pass

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
        logging.debug(f"Time elapsed: {stop-start}")
        return xmltodict.parse(r.content)

    def buildquery(self, cursormark, pageSize, query, synonym=True,):
        import logging
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        payload = {'query': query, 'format': format, 'resultType': 'core',
                   'cursorMark': cursormark, 'pageSize': pageSize, 'synonym': synonym, 'format': 'xml', 'sort_PMCID': 'y'}
        logging.debug("*/submitting RESTful query (I)*/")
        return {'headers': headers, 'payload': payload}

    def webscrapepmc(self, query, pmccount, onlyresearcharticles=False, onlypreprints=False, onlyreviews=False):
        from selenium import webdriver
        import time
        import os
        import logging

        from selenium import webdriver
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
        from selenium.webdriver.common.alert import Alert
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.common.exceptions import TimeoutException
        from selenium.webdriver.chrome.options import Options
        from selenium import webdriver
        import chromedriver_autoinstaller
        didquit = False
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
        if onlyresearcharticles:
            url = f"https://europepmc.org/search?query=%28%22{query}%22%20AND%20%28%28HAS_FT%3AY%20AND%20OPEN_ACCESS%3AY%29%29%20AND%20%28%28%28SRC%3AMED%20OR%20SRC%3APMC%20OR%20SRC%3AAGR%20OR%20SRC%3ACBA%29%20NOT%20%28PUB_TYPE%3A%22Review%22%29%29%29%29%20AND%20%28%28%28SRC%3AMED%20OR%20SRC%3APMC%20OR%20SRC%3AAGR%20OR%20SRC%3ACBA%29%20NOT%20%28PUB_TYPE%3A%22Review%22%29%29%29"
        elif onlypreprints:
            url = f"https://europepmc.org/search?query={query}%20AND%20%28SRC%3APPR%29&page=1"
        elif onlyreviews:
            url = f"https://europepmc.org/search?query={query}%20%20AND%20%28PUB_TYPE%3AREVIEW%29&page=1"
        else:
            url = f'https://europepmc.org/search?query={query}%20%28IN_EPMC%3Ay%29%20AND%20%28OPEN_ACCESS%3Ay%29&page=1'
        webdriver.get(url)
        while len(pmcdict) <= size:
            time.sleep(2)
            # retrive url in headless browser
            # time.sleep(3)
            results = webdriver.find_elements_by_xpath(
                "//ul[@class='separated-list']/li/div/p[3]/span")
            for result in results:
                pmcid = result.text
                if 'PMC' in pmcid:
                    a += 1
                    if len(pmcdict) < size:
                        logging.info(f'Scraping paper no. {a}')
                        name = pmcid.split()
                        pmcdict[name[-1]] = {}
                        pmcdict[name[-1]]["downloaded"] = False
                    else:
                        break
            if a < size:
                try:
                    time.sleep(2)
                    webdriver.find_element_by_xpath(
                        "//span[contains(text(), 'Next')]").click()
                except:
                    if size > 25:
                        logging.info("Only found so many papers.")
                    webdriver.quit()
                    didquit = True
                    break
            elif not(didquit):
                webdriver.quit()
                break
            time.sleep(2)

        directory_url = os.path.join(
            str(os.getcwd()))
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        self.makejson(os.path.join(
            str(os.getcwd()), 'eupmc_results.json'),  dict(pmcdict))
        return dict(pmcdict)

    def europepmc(self, query, size, synonym=True, externalfile=True, fulltext=True, **kwargs):
        import requests
        import xmltodict
        import lxml.etree
        import logging
        import lxml
        import os
        import json
        size = int(size)
        content = [[]]
        nextCursorMark = ['*', ]
        morepapers = True
        number_of_papers_there = 0

        while number_of_papers_there <= size and morepapers == True:
            queryparams = self.buildquery(
                nextCursorMark[-1], 1000, query, synonym=synonym)
            builtquery = self.postquery(
                queryparams['headers'], queryparams['payload'])
            if "nextCursorMark" in builtquery["responseWrapper"]:
                nextCursorMark.append(
                    builtquery["responseWrapper"]["nextCursorMark"])
                totalhits = builtquery["responseWrapper"]["hitCount"]
                logging.info(f"Total Hits are {totalhits}")
                output_dict = json.loads(json.dumps(builtquery))
                try:
                    for paper in output_dict["responseWrapper"]["resultList"]["result"]:

                        if "update" in kwargs:
                            if "pmcid" in paper and paper["pmcid"] not in kwargs["update"]:
                                if number_of_papers_there <= size:
                                    content[0].append(paper)
                                    number_of_papers_there += 1
                        else:
                            if "pmcid" in paper:
                                if number_of_papers_there <= size:
                                    content[0].append(paper)

                                    number_of_papers_there += 1

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

    # this is the function that will the the result from search and will download and save the files.
    def makecsv(self, searchvariable, makecsv=False, update=False):
        import pandas_read_xml as pdx
        import xmltodict
        import pandas as pd
        import lxml.etree
        import json
        import os
        import logging
        resultant_dict = {}
        for paper_number, papers in enumerate(searchvariable):
            output_dict = json.loads(json.dumps(papers))

            for paper in output_dict:

                if "pmcid" in paper:
                    paper_number += 1
                    logging.debug(
                        f"Reading Query Result for paper {paper_number}")
                    pdfurl = []
                    htmlurl = []
                    for x in paper["fullTextUrlList"]["fullTextUrl"]:
                        if x["documentStyle"] == "pdf" and x["availability"] == "Open access":
                            pdfurl.append(x["url"])

                        if x["documentStyle"] == "html" and x["availability"] == "Open access":
                            htmlurl.append(x["url"])
                    resultant_dict[paper["pmcid"]] = {}
                    resultant_dict[paper["pmcid"]
                                   ]["downloaded"] = False
                    resultant_dict[paper["pmcid"]
                                   ]["pdfdownloaded"] = False
                    resultant_dict[paper["pmcid"]
                                   ]["jsondownloaded"] = False
                    resultant_dict[paper["pmcid"]
                                   ]["csvmade"] = False
                    resultant_dict[paper["pmcid"]]["full"] = paper
                    try:
                        resultant_dict[paper["pmcid"]
                                       ]["htmllinks"] = htmlurl[0]
                    except:
                        pass

                    try:
                        resultant_dict[paper["pmcid"]
                                       ]["pdflinks"] = pdfurl[0]
                    except:
                        pass
                    try:
                        resultant_dict[paper["pmcid"]
                                       ]["journaltitle"] = paper["journalInfo"]["journal"]["title"]
                    except:
                        logging.warning(
                            "journalInfo not found for paper", paper_number)
                    try:
                        resultant_dict[paper["pmcid"]
                                       ]["authorinfo"] = paper["authorList"]["author"][0]['fullName']
                    except:
                        logging.warning(
                            f"Author list not found for paper {paper_number}")
                    try:
                        resultant_dict[paper["pmcid"]
                                       ]["title"] = paper["title"]
                    except:
                        logging.warning(
                            f"Title not found for paper {paper_number}")
                    paperpmcid = paper["pmcid"]
                    logging.debug(
                        f'Wrote Meta Data to a dictionary that will be written to all the chosen metadata file formats for paper {paperpmcid}')
        if update:
            resultant_dict.update(update)
        directory_url = os.path.join(
            str(os.getcwd()))
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        self.makejson(os.path.join(
            str(os.getcwd()), 'eupmc_results.json'), resultant_dict)
        resultant_dict_for_csv = resultant_dict
        for paper in resultant_dict_for_csv:
            resultant_dict_for_csv[paper].pop("downloaded")
            resultant_dict_for_csv[paper].pop("pdfdownloaded")
            resultant_dict_for_csv[paper].pop("jsondownloaded")
            resultant_dict_for_csv[paper].pop("csvmade")

        df = pd.DataFrame.from_dict(resultant_dict_for_csv,)
        df_transposed = df.T
        if makecsv:
            if os.path.exists(os.path.join(
                    str(os.getcwd()), 'europe_pmc.csv')):
                df_transposed.to_csv(os.path.join(
                    str(os.getcwd()), 'europe_pmc.csv'), mode='a', header=False)
            else:
                df_transposed.to_csv(os.path.join(
                    str(os.getcwd()), 'europe_pmc.csv'))

        return searchvariable

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
        import logging
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
        import logging
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        with open(destination_url, 'wb') as f:
            f.write(content)

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

    def makexmlfiles(self, final_xml_dict, getpdf=False, makecsv=False, makexml=False, references=False, citations=False, supplementaryFiles=False):
        import logging
        import requests
        import logging
        import lxml.etree
        import lxml
        import pandas as pd
        import os
        import time
        if makexml:
            logging.debug(
                "*/saving xml to per-document directories (CTrees) (D)*/")
            loggingurl = os.path.join(
                str(os.getcwd()), '*', 'fulltext.xml')
            logging.info(
                f"Saving XML files to {loggingurl}")
            logging.debug("*/Making the Request to get full text xml*/")

        for paper_number, paper in enumerate(final_xml_dict):
            start = time.time()
            paper_number += 1
            pmcid = paper
            tree = self.getxml(pmcid)
            destination_url = os.path.join(
                str(os.getcwd()), pmcid, "fulltext.xml")
            directory_url = os.path.join(str(os.getcwd()), pmcid)

            jsonurl = os.path.join(
                str(os.getcwd()), pmcid, "eupmc_result.json")
            referenceurl = os.path.join(
                str(os.getcwd()), pmcid, "references.xml")
            citationurl = os.path.join(
                str(os.getcwd()), pmcid, "citation.xml")
            supplementaryfilesurl = os.path.join(
                str(os.getcwd()), pmcid, "supplementaryfiles.zip")
            if references:
                getreferences = self.getreferences(
                    final_xml_dict[paper]["full"]["id"], references)
                self.writexml(directory_url, referenceurl, getreferences)
                logging.info(f"Made references for {pmcid}")
            if citations:
                getcitations = self.getcitations(
                    final_xml_dict[paper]["full"]["id"], citations)
                self.writexml(directory_url, citationurl, getcitations)
                logging.info(f"Made Citations for {pmcid}")
            if supplementaryFiles:
                self.getsupplementaryfiles(
                    final_xml_dict[paper]["full"]["id"], directory_url, supplementaryfilesurl)
            if not os.path.isdir(directory_url):
                os.makedirs(directory_url)
            if final_xml_dict[paper]["downloaded"] == False:
                if makexml:
                    self.writexml(directory_url, destination_url, tree)
                    logging.info(
                        f"*/Wrote xml for {pmcid}/")
                    final_xml_dict[paper]["downloaded"] = True

            if final_xml_dict[paper]["pdfdownloaded"] == False:
                pdf_destination = os.path.join(
                    str(os.getcwd()), pmcid, "fulltext.pdf")
                if getpdf:
                    if "pdflinks" in final_xml_dict[paper]:
                        if len(final_xml_dict[paper]["pdflinks"]) > 0:
                            self.writepdf(
                                final_xml_dict[paper]["pdflinks"], pdf_destination)
                            final_xml_dict[paper]["pdfdownloaded"] = True
                            logging.info(
                                f"Wrote the pdf file for {pmcid}")
            dict_to_write = dict(final_xml_dict[paper])
            dict_to_write.pop('pdfdownloaded')
            dict_to_write.pop('jsondownloaded')
            dict_to_write.pop('csvmade')
            if final_xml_dict[paper]["jsondownloaded"] == False:
                self.makejson(jsonurl, dict_to_write)
                final_xml_dict[paper]["jsondownloaded"] = True
            if final_xml_dict[paper]["csvmade"] == False:
                if makecsv:
                    df = pd.Series(dict_to_write).to_frame(
                        'Info_By_EuropePMC_Api')
                    df.to_csv(os.path.join(
                        str(os.getcwd()), pmcid, "fulltext.csv"))
                    final_xml_dict[paper]["csvmade"] = True
            self.makejson(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'), final_xml_dict)
            stop = time.time()
            logging.debug(f"Time elapsed: {stop-start}")
            logging.debug(f"*/Updating the json*/\n")

    def readjsondata(self, path):
        import json
        import logging
        with open(path) as f:
            object = json.load(f)
        return object

    def apipaperdownload(self, query, size, onlymakejson=False, getpdf=False, makecsv=False, makexml=False, references=False, citations=False, supplementaryFiles=False):
        import os
        import logging
        query_result = self.europepmc(query, size)
        self.makecsv(query_result, makecsv=makecsv)

        if not(onlymakejson):
            read_json = self.readjsondata(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'))
            self.makexmlfiles(read_json, getpdf=getpdf, makecsv=makecsv, makexml=makexml,
                              references=references, citations=citations, supplementaryFiles=supplementaryFiles)

    def scrapingpaperdownload(self, query, size, onlyresearcharticles=False, onlypreprints=False, onlyreviews=False, onlymakejson=False, makexml=False, references=False, citations=False, supplementaryFiles=False):
        query_result = self.webscrapepmc(
            query, size, onlyresearcharticles=onlyresearcharticles, onlypreprints=onlypreprints, onlyreviews=onlyreviews)

        if not(onlymakejson):
            self.makexmlfiles(query_result, makexml=makexml,
                              references=references, citations=citations, supplementaryFiles=supplementaryFiles)

    def updatecorpus(self, query, original_json, size, onlymakejson=False, getpdf=False, makecsv=False, makexml=False, references=False, citations=False, supplementaryFiles=False):
        import os
        import logging
        query_result = self.europepmc(query, size, update=original_json)
        self.makecsv(query_result, makecsv=makecsv,
                     update=original_json)
        if not(onlymakejson):
            read_json = self.readjsondata(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'))
            self.makexmlfiles(read_json, getpdf=getpdf,
                              makecsv=makecsv, makexml=makexml, references=references, citations=citations, supplementaryFiles=supplementaryFiles)

    def noexecute(self, query, size):
        import logging
        import xmltodict
        import requests
        import time
        builtqueryparams = self.buildquery(
            '*', 25, query, synonym=True)
        result = self.postquery(
            builtqueryparams['headers'], builtqueryparams['payload'])
        totalhits = result['responseWrapper']['hitCount']
        logging.info(f'Total number of hits for the query are {totalhits}')

    def handlecli(self):
        version = "0.0.2"
        import argparse
        import os
        import logging
        import sys
        parser = argparse.ArgumentParser(
            description=f"Welcome to Pygetpapers version {version}. -h or --help for help")
        parser.add_argument("-v", "--version",
                            default=False, action="store_true", help="output the version number")
        parser.add_argument("-q", "--query",
                            type=str, default=False, help="query string transmitted to repository API. Eg. 'Artificial Intelligence' or 'Plant Parts'. To escape special characters within the quotes, use backslash. The query to be quoted in either single or double quotes. ")

        parser.add_argument("-o", "--output",
                            type=str, help="output directory (Default: current working directory)", default=os.getcwd())
        parser.add_argument("-x", "--xml", default=False, action='store_true',
                            help="download fulltext XMLs if available")
        parser.add_argument("-p", "--pdf", default=False, action='store_true',
                            help="download fulltext PDFs if available")
        parser.add_argument("-s", "--supp", default=False, action='store_true',
                            help="download supplementary files if available	")
        parser.add_argument("--references",
                            type=str, default=False, help="Download references if available. Requires source for references (AGR,CBA,CTX,ETH,HIR,MED,PAT,PMC,PPR).")
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
                            type=str, help="save log to specified file in output directory as well as printing to terminal")
        parser.add_argument("-k", "--limit", default=100,
                            type=int, help="maximum number of hits (default: 100)")

        parser.add_argument('-r', "--restart", default=False,
                            type=str, help="Reads the json and makes the xml files. Takes the path to the json as the input")

        parser.add_argument("-u", "--update", default=False,
                            type=str,
                            help="Updates the corpus by downloading new papers. Requires -k or --limit (If not provided, default will be used) and -q or --query (must be provided) to be given. Takes the path to the json as the input.")
        parser.add_argument("--onlyquery", action='store_true',
                            help="Saves json file containing the result of the query in storage. The json file can be given to --restart to download the papers later.")
        parser.add_argument("-c", "--makecsv", default=False, action='store_true',
                            help="Stores the per-document metadata as csv. Works only with --api method.")

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
            logging.basicConfig(filename=args.logfile,
                                level=level, filemode='w')
            console = logging.StreamHandler()

            console.setLevel(level)
            formatter = logging.Formatter('%(levelname)s: %(message)s')
            # tell the handler to use this format
            console.setFormatter(formatter)
            logging.getLogger().addHandler(console)
            logging.info(f'Making log file at {args.logfile}')

        else:
            logging.basicConfig(
                level=level, format='%(levelname)s: %(message)s')

        if not args.query:
            logging.warning('Please specify a query')
            sys.exit(1)

        if args.noexecute:
            self.noexecute(args.query, 100)
        elif args.version:
            logging.info(version)
        elif args.restart:
            import os
            import logging
            read_json = self.readjsondata(args.restart)
            os.chdir(os.path.dirname(os.path.dirname(args.restart)))
            self.makexmlfiles(read_json, getpdf=args.pdf, makecsv=args.makecsv, makexml=args.xml,
                              references=args.references, citations=args.citations, supplementaryFiles=args.supp)
        elif args.update:
            read_json = self.readjsondata(args.update)
            os.chdir(os.path.dirname(args.update))
            self.updatecorpus(args.query, read_json, args.limit, getpdf=args.pdf,
                              makecsv=args.makecsv, makexml=args.xml, references=args.references, citations=args.citations, supplementaryFiles=args.supp)
        else:
            if args.query:
                self.apipaperdownload(args.query, args.limit,
                                      onlymakejson=args.onlyquery, getpdf=args.pdf, makecsv=args.makecsv, makexml=args.xml, references=args.references, citations=args.citations, supplementaryFiles=args.supp)
        # Have to check with EuropePMC's policy about webscraping

        '''
        elif args.webscraping:
            self.scrapingpaperdownload(args.query, args.limit, onlyresearcharticles=args.onlyresearcharticles,
                                       onlypreprints=args.onlypreprints, onlyreviews=args.onlyreviews, onlymakejson=args.onlyquery)
        '''


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
