class pygetpapers:
    def __init__(self, **kwargs):
        pass

    def postquery(self, headers, payload):
        import xmltodict
        import requests
        import time
        print("*/Making the Request to get all hits*/")
        start = time.time()
        r = requests.post(
            'https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST', data=payload, headers=headers)
        stop = time.time()
        print("*/Got the Content */")
        print(f"Time elapsed: {stop-start}")
        return xmltodict.parse(r.content)

    def buildquery(self, cursormark, pageSize, query, synonym=True,):
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        payload = {'query': query, 'format': format, 'resultType': 'core',
                   'cursorMark': cursormark, 'pageSize': pageSize, 'synonym': synonym, 'format': 'xml', 'sort_PMCID': 'y'}
        print("*/Building the Query*/")
        return {'headers': headers, 'payload': payload}

    def webscrapepmc(self, query, pmccount, onlyresearcharticles=False, onlypreprints=False, onlyreviews=False):
        from selenium import webdriver
        import time
        import os
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
                        print('Scraping paper no.', a)
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
                        print("Only found so many papers.")
                    webdriver.quit()
                    didquit = True
                    break
            elif not(didquit):
                webdriver.quit()
                break
            time.sleep(2)

        directory_url = os.path.join(
            str(os.getcwd()), 'papers')
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        self.writepickle(os.path.join(
            str(os.getcwd()), 'papers', 'europe_pmc.pickle'),  dict(pmcdict))
        return dict(pmcdict)

    def europepmc(self, query, size, synonym=True, externalfile=True, fulltext=True, **kwargs):
        import requests
        import xmltodict
        import lxml.etree
        import lxml
        import os
        import json
        size = int(size)
        content = [[]]
        nextCursorMark = ['*', ]
        morepapers = True
        number_of_papers_there = 0
        # change synonym to no otherwise yes is the default
        # The code regarding the size of the query currently only works till 100 terms. This is on purpose and I will add Function to access next cursormark which is basically next page of the resultant of the query once I have enough permision and knowledge

        while number_of_papers_there <= size and morepapers == True:
            queryparams = self.buildquery(
                nextCursorMark[-1], 1000, query, synonym=synonym)
            builtquery = self.postquery(
                queryparams['headers'], queryparams['payload'])
            if "nextCursorMark" in builtquery["responseWrapper"]:
                nextCursorMark.append(
                    builtquery["responseWrapper"]["nextCursorMark"])
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
                    print("Could not find more papers")
                    break

            else:
                morepapers = False
                print("Could not find more papers")
        if number_of_papers_there > size:
            content[0] = content[0][0:size]
        return content

    # this is the function that will the the result from search and will download and save the files.
    def makecsv(self, searchvariable, makecsv=False, makejson=False):
        import pandas_read_xml as pdx
        import xmltodict
        import pandas as pd
        import lxml.etree
        import json
        import pickle
        import os
        resultant_dict = {}
        for paper_number, papers in enumerate(searchvariable):
            output_dict = json.loads(json.dumps(papers))

            for paper in output_dict:

                if "pmcid" in paper:
                    paper_number += 1
                    print("Reading Dictionary for paper", paper_number)
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
                        print("journalInfo not found for paper", paper_number)
                    try:
                        resultant_dict[paper["pmcid"]
                                       ]["authorinfo"] = paper["authorList"]["author"][0]['fullName']
                    except:
                        print("Author list not found for paper", paper_number)
                    try:
                        resultant_dict[paper["pmcid"]
                                       ]["title"] = paper["title"]
                    except:
                        print("Title not found for paper", paper_number)

                    print('Wrote the important Attrutes to a dictionary')

        pickleurl = os.path.join(
            str(os.getcwd()), 'papers', 'europe_pmc.pickle')
        directory_url = os.path.join(
            str(os.getcwd()), 'papers')

        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        self.writepickle(pickleurl, resultant_dict)
        resultant_dict_for_csv = resultant_dict
        for paper in resultant_dict_for_csv:
            resultant_dict_for_csv[paper].pop("downloaded")
        df = pd.DataFrame.from_dict(resultant_dict_for_csv,)
        df_transposed = df.T
        if makecsv:
            df_transposed.to_csv(os.path.join(
                str(os.getcwd()), 'papers', 'europe_pmc.csv'))
        if makejson:
            self.makejson(os.path.join(
                str(os.getcwd()), 'papers', 'europe_pmc.json'), searchvariable)
        return searchvariable

    def getxml(self, pmcid):
        import requests
        print("*/Making the Request to get full text xml*/")

        r = requests.get(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML")
        print("*/Done*/")

        return r.content

    def getsupplementaryfiles(self, pmcid):
        import requests
        r = requests.get(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles")
        return r

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

    def writepickle(self, destination, content):
        import pickle
        import os
        with open(destination, 'wb') as f:
            pickle.dump(content, f, pickle.HIGHEST_PROTOCOL)

    def makejson(self, path, final_xml_dict):
        import json
        with open(path, 'w') as fp:
            json.dump(final_xml_dict, fp)

    def makexmlfiles(self, final_xml_dict, getpdf=False, makejson=False, makecsv=False):
        import requests
        import lxml.etree
        import lxml
        import pickle
        import pandas as pd
        import os
        import time
        print("*/Writing the xml papers to memory*/")
        for paper_number, paper in enumerate(final_xml_dict):
            start = time.time()
            paper_number += 1
            pmcid = paper
            tree = self.getxml(pmcid)
            destination_url = os.path.join(str(os.getcwd()),
                                           'papers', pmcid, "fulltext.xml")
            directory_url = os.path.join(str(os.getcwd()), 'papers', pmcid)
            pickle_url = os.path.join(
                str(os.getcwd()), 'papers', pmcid, f"{pmcid}.pickle")
            jsonurl = os.path.join(
                str(os.getcwd()), 'papers', pmcid, f"{pmcid}.json")
            if final_xml_dict[paper]["downloaded"] == False:
                self.writexml(directory_url, destination_url, tree)
                print(
                    f"*/Wrote the xml paper {paper_number} at {destination_url}/")
                final_xml_dict[paper]["downloaded"] = True
                if makejson:
                    self.makejson(os.path.join(
                        str(os.getcwd()), 'papers', 'europe_pmc.json'), final_xml_dict)
            if final_xml_dict[paper]["pdfdownloaded"] == False:
                pdf_destination = os.path.join(
                    str(os.getcwd()), 'papers', pmcid, f"{pmcid}.pdf")
                if getpdf:
                    if "pdflinks" in final_xml_dict[paper]:
                        if len(final_xml_dict[paper]["pdflinks"]) > 0:
                            self.writepdf(
                                final_xml_dict[paper]["pdflinks"], pdf_destination)
                            final_xml_dict[paper]["pdfdownloaded"] = True
                            print(
                                f"Wrote the pdf file for {paper_number} at {pdf_destination}")
            if final_xml_dict[paper]["jsondownloaded"] == False:
                if makejson:
                    self.makejson(jsonurl, final_xml_dict[paper])
                    final_xml_dict[paper]["jsondownloaded"] = True
            if final_xml_dict[paper]["csvmade"] == False:
                if makecsv:
                    df = pd.Series(final_xml_dict[paper]).to_frame(
                        'Info_By_EuropePMC_Api')
                    df.to_csv(os.path.join(
                        str(os.getcwd()), 'papers', pmcid, f"{pmcid}.csv"))
                    final_xml_dict[paper]["csvmade"] = True
            self.writepickle(pickle_url, final_xml_dict[paper])
            self.writepickle(os.path.join(
                str(os.getcwd()), 'papers', 'europe_pmc.pickle'), final_xml_dict)
            stop = time.time()
            print(f"Time elapsed: {stop-start}")
            print(f"*/Updating the pickle*/", '\n')

    def readpickleddata(self, path):
        import pandas as pd
        object = pd.read_pickle(f'{path}')
        return object

    def apipaperdownload(self, query, size, onlymakepickle=False, getpdf=False, makejson=False, makecsv=False):
        import os
        query_result = self.europepmc(query, size)
        self.makecsv(query_result, makecsv=makecsv, makejson=makejson)

        if not(onlymakepickle):
            read_pickled = self.readpickleddata(os.path.join(
                str(os.getcwd()), 'papers', 'europe_pmc.pickle'))
            self.makexmlfiles(read_pickled, getpdf=getpdf,
                              makejson=makejson, makecsv=makecsv)

    def scrapingpaperdownload(self, query, size, onlyresearcharticles=False, onlypreprints=False, onlyreviews=False, onlymakepickle=False):
        query_result = self.webscrapepmc(
            query, size, onlyresearcharticles=onlyresearcharticles, onlypreprints=onlypreprints, onlyreviews=onlyreviews)

        if not(onlymakepickle):
            self.makexmlfiles(query_result)

    def updatecorpus(self, query, original_pickle, size, onlymakepickle=False, getpdf=False, makejson=False, makecsv=False):
        import os
        query_result = self.europepmc(query, size, update=original_pickle)
        self.makecsv(query_result, makecsv=makecsv, makejson=makejson)
        if not(onlymakepickle):
            read_pickled = self.readpickleddata(os.path.join(
                str(os.getcwd()), 'papers', 'europe_pmc.pickle'))
            self.makexmlfiles(read_pickled, getpdf=getpdf,
                              makejson=makejson, makecsv=makecsv)

    def handlecli(self):
        import argparse
        import os
        parser = argparse.ArgumentParser(
            description="Welcome to Pygetpapers. -h or --help for help")
        parser.add_argument("-q", "--query",
                            type=str, help="query string transmitted to repository API. Eg. 'Artificial Intelligence' or 'Plant Parts'. To escape special characters within the quotes, use backslash. The query to be quoted in either single or double quotes. ")
        parser.add_argument("-k", "--limit", default=100,
                            type=int, help="maximum number of hits (default: 100)")
        parser.add_argument("-o", "--output",
                            type=str, help="output directory (Default: current working directory)", default=os.getcwd())
        parser.add_argument("-v", "--onlyquery", action='store_true',
                            help="Saves pickle file containing the result of the query in storage. The pickle file can be given to --frompickle to download the papers later.")
        parser.add_argument("-f", "--frompickle", default=False,
                            type=str, help="Reads the picke and makes the xml files. Takes the path to the pickle as the input")
        parser.add_argument("-p", "--downloadpdf", default=False, action='store_true',
                            help="Downloads full text pdf files for the papers. Works only with --api method.")
        parser.add_argument("-j", "--makejson", default=False, action='store_true',
                            help="Stores the per-document metadata as json. Works only with --api method.")
        parser.add_argument("-c", "--makecsv", default=False, action='store_true',
                            help="Stores the per-document metadata as csv. Works only with --api method.")
        parser.add_argument("-u", "--update", default=False,
                            type=str,
                            help="Updates the corpus by downloading new papers. Requires -k or --limit (If not provided, default will be used) and -q or --query (must be provided) to be given. Takes the path to the pickle as the input.")
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
        args = parser.parse_args()

        if os.path.exists(args.output):
            os.chdir(args.output)
        else:
            os.makedirs(args.output)
            os.chdir(args.output)

        if args.frompickle:
            import os
            read_pickled = self.readpickleddata(args.frompickle)
            os.chdir(os.path.dirname(os.path.dirname(args.frompickle)))
            self.makexmlfiles(read_pickled, getpdf=args.downloadpdf,
                              makejson=args.makejson, makecsv=args.makecsv)
        elif args.update:
            read_pickled = self.readpickleddata(args.update)
            os.chdir(os.path.dirname(os.path.dirname(args.update)))
            self.updatecorpus(args.query, read_pickled, args.limit, getpdf=args.downloadpdf,
                              makejson=args.makejson, makecsv=args.makecsv)

        else:
            self.apipaperdownload(args.query, args.limit,
                                  onlymakepickle=args.onlyquery, getpdf=args.downloadpdf, makejson=args.makejson, makecsv=args.makecsv)
        # Have to check with EuropePMC's policy about webscraping

        '''
        elif args.webscraping:
            self.scrapingpaperdownload(args.query, args.limit, onlyresearcharticles=args.onlyresearcharticles,
                                       onlypreprints=args.onlypreprints, onlyreviews=args.onlyreviews, onlymakepickle=args.onlyquery)
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
