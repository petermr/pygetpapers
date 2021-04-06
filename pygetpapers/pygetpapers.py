from .download_tools import download_tools


class pygetpapers(download_tools):

    def __init__(self):
        """
        This function makes all the constants
        """
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

    def europepmc(self, query, size, synonym=True, **kwargs):
        """
        Makes the query to europepmc rest api then returns a python dictionary containing the research papers.

        :param query: the query passed on to payload

        :param size: total number of papers

        :param synonym: whether synonym should be or not

        :param kwargs: ensures that the output dict doesnt contain papers already there in update

        :return: Python dictionary containing the research papers.
        """

        import logging
        import json
        size = int(size)
        content = [[]]
        nextCursorMark = ['*', ]
        morepapers = True
        number_of_papers_there = 0

        while number_of_papers_there <= size and morepapers is True:
            queryparams = self.buildquery(
                nextCursorMark[-1], 1000, query, synonym=synonym)
            builtquery = super().postquery(
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

    def make_initial_columns_for_paper_dict(self, pmcid, resultant_dict):
        """
        :param pmcid: pmcid of the paper for which fields will be created

        :param resultant_dict: dict in which the fields will be created

        :return: dict with the initial fields created for pmcid
        """
        resultant_dict[pmcid] = {}
        resultant_dict[pmcid]["downloaded"] = False
        resultant_dict[pmcid]["pdfdownloaded"] = False
        resultant_dict[pmcid]["jsondownloaded"] = False
        resultant_dict[pmcid]["csvmade"] = False
        return resultant_dict

    # this is the function that will the the result from search and will download and save the files.
    def makecsv(self, searchvariable, makecsv=False, update=False):
        """
        Writes the json and *csv for searchvaraible dict

        :param searchvariable(dict): Python dictionary which contains all the research papers (given by europepmc())

        :param makecsv(bool): Weather to make csv files

        :param update(dict): if provided, will add the research papers to the searchvariable dict

        :return: searchvariable
        """
        import pandas as pd
        import json
        import os
        import logging
        resultant_dict = {}
        for paper_number, papers in enumerate(searchvariable):
            output_dict = json.loads(json.dumps(papers))
            for paper in output_dict:
                if self.PMCID in paper:
                    paper_number += 1
                    htmlurl, paperpmcid, pdfurl, resultant_dict = self.write_meta_data_for_paper(
                        paper, paper_number, resultant_dict)
                    self.add_fields_to_resultant_dict(
                        htmlurl, paper, paper_number, pdfurl, resultant_dict[paperpmcid])
                    logging.debug(
                        f'Wrote Meta Data to a dictionary that will be written to all the chosen metadata file formats for paper {paperpmcid}')
        if update:
            resultant_dict.update(update)
        directory_url = os.path.join(
            str(os.getcwd()))
        jsonurl = os.path.join(
            str(os.getcwd()), 'eupmc_results.json')
        super().check_or_make_directory(directory_url)
        self.makejson(jsonurl, resultant_dict)
        resultant_dict_for_csv = super().make_dict_for_csv(resultant_dict)
        df = pd.DataFrame.from_dict(resultant_dict_for_csv, )
        df_transposed = df.T
        if makecsv:
            super().write_or_append_to_csv(df_transposed)
        return searchvariable

    def write_meta_data_for_paper(self, paper, paper_number, resultant_dict):
        """
        Adds pdf and html url as well as makes the paper key in resultant_dict

        :param paper: python dictionary for the paper

        :param paper_number: paper number to log

        :param resultant_dict: dictionary to add paper as well as pdf,html url to

        :return: (htmlurl, paperpmcid, pdfurl, resultant_dict)
        """
        import logging
        logging.debug(
            f"Reading Query Result for paper {paper_number}")
        pdfurl = []
        htmlurl = []
        for x in paper["fullTextUrlList"]["fullTextUrl"]:
            if x["documentStyle"] == "pdf" and x["availability"] == "Open access":
                pdfurl.append(x["url"])

            if x["documentStyle"] == "html" and x["availability"] == "Open access":
                htmlurl.append(x["url"])
        paperpmcid = paper["pmcid"]
        resultant_dict = self.make_initial_columns_for_paper_dict(
            paperpmcid, resultant_dict)
        resultant_dict[paperpmcid]["full"] = paper
        return htmlurl, paperpmcid, pdfurl, resultant_dict

    def add_fields_to_resultant_dict(self, htmlurl, paper, paper_number, pdfurl, dict_for_paper):
        """
        Writes urls to dictionary

        :param htmlurl: list containing html urls for the paper

        :param paper: python dictionary of the paper

        :param paper_number: paper number to log

        :param pdfurl: list containing pdf urls for the paper

        :param dict_for_paper: python dictionary to write the urls to

        :return: dict_for_paper
        """
        import logging
        try:
            dict_for_paper[self.HTMLLINKS] = htmlurl[0]
        except:
            logging.warning(
                f"html url not found for paper {paper_number}")
        try:
            dict_for_paper["abstract"] = paper["abstractText"]
        except:
            logging.warning(
                f"Abstract not found for paper {paper_number}")

        try:
            dict_for_paper["Keywords"] = paper["keywordList"]["keyword"]
        except:
            logging.warning(
                f"Keywords not found for paper {paper_number}")
        try:
            dict_for_paper[self.PDFLINKS] = pdfurl[0]
        except:
            logging.warning(
                f"pdf url not found for paper {paper_number}")
        try:
            dict_for_paper[self.JOURNALTITLE] = paper["journalInfo"]["journal"][self.TITLE]
        except:
            logging.warning(
                f"journalInfo not found for paper {paper_number}")
        try:
            dict_for_paper[self.AUTHORINFO
                           ] = paper["authorList"]["author"][0]['fullName']
        except:
            logging.warning(
                f"Author list not found for paper {paper_number}")
        try:
            dict_for_paper[self.TITLE] = paper[self.TITLE]
        except:
            logging.warning(
                f"Title not found for paper {paper_number}")

    def getxml(self, pmcid):
        """
        Makes a query for the pmcid xml to eupmc rest.

        :param pmcid: pmcid of the paper to query for

        :return: query result
        """
        import requests
        r = requests.get(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML")
        return r.content

    def getsupplementaryfiles(self, pmcid, directory_url, destination_url):
        """
        Downloads the supplemetary marks for the paper having pmcid

        :param pmcid: pmcid to get the supplementary files

        :param directory_url: directory containg destination

        :param destination_url: path to write the supplementary files to
        """
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
        """
        Gets references for the paper of pmcid

        :param pmcid: pmcid to get the references

        :param source: source to get the references from

        :return: references xml

        """
        import requests
        r = requests.get(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{pmcid}/references?page=1&pageSize=1000&format=xml")
        return r.content

    def make_references(self, directory_url, paperid, source, referenceurl):
        '''
        Downloads the references for the paper with pmcid (paperid) to reference url

        :param directory_url: directory containing referenceurl

        :param paperid:  pmc id of the paper

        :param source: source to get the citations from

        :param referenceurl: path to write the references to
        '''
        getreferences = self.getreferences(
            paperid, source)
        self.writexml(directory_url, referenceurl, getreferences)

    def getcitations(self, pmcid, source):
        """
        Gets citations for the paper of pmcid

        :param pmcid: pmcid to get the citations

        :param source: source to get the citations from

        :return: citations xml

        """
        import requests
        r = requests.get(
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{pmcid}/citations?page=1&pageSize=1000&format=xml")
        return r.content

    def writexml(self, directory_url, destination_url, content):
        """
        writes xml to the destination

        :param directory_url: directory containg destination

        :param destination_url: path to write the xml to

        :param content: xml content
        """
        import os
        if not os.path.isdir(directory_url):
            os.makedirs(directory_url)
        with open(destination_url, 'wb') as f:
            f.write(content)

    def make_citations(self, source, citationurl, directory_url, paperid):
        '''
        Downloads the citations for the paper with pmcid (paperid) to citation url

        :param source: source to get the citations from

        :param citationurl: path to write the citations to

        :param directory_url: directory containing citationurl

        :param paperid: pmc id of the paper
        '''
        getcitations = self.getcitations(
            paperid, source)
        self.writexml(directory_url, citationurl, getcitations)

    def makexmlfiles(self, final_xml_dict, getpdf=False, makecsv=False, makexml=False, references=False,
                     citations=False, supplementaryFiles=False):
        """
        Writes the *pdf,*csv,*xml,*references,*citations,*supplementaryFiles for the individual papers

        :param final_xml_dict: Python dictionary containg all the papers

        :param getpdf(bool): Weather to make pdfs

        :param makecsv(bool): Weather to make csv for the metadata

        :param makexml(bool): Weather to make xml file for the paper

        :param references(bool): Weather to download references

        :param citations(bool): Weather to download citations

        :param supplementaryFiles(bool): Weather to download supplementary files

        """
        import logging
        import os
        import time
        if makexml:
            super().log_making_xml()
        paper_number = 0
        for paper in final_xml_dict:
            start = time.time()
            paper_number += 1
            pmcid = paper
            tree = self.getxml(pmcid)
            citationurl, destination_url, directory_url, jsonurl, referenceurl, supplementaryfilesurl = self.get_urls_to_write_to(
                pmcid)
            paperdict = final_xml_dict[paper]
            paperid = paperdict["full"]["id"]
            if references:
                self.make_references(directory_url, paperid,
                                     references, referenceurl)
                logging.info(f"Made references for {pmcid}")
            if citations:
                self.make_citations(citations, citationurl,
                                    directory_url, paperid)
                logging.info(f"Made Citations for {pmcid}")
            if supplementaryFiles:
                self.getsupplementaryfiles(
                    paperid, directory_url, supplementaryfilesurl)
                logging.info(f"Made Supplementary files for {pmcid}")
            if not os.path.isdir(directory_url):
                os.makedirs(directory_url)
            condition_to_down, condition_to_download_csv, condition_to_download_json, condition_to_download_pdf = super().conditions_to_download(
                paperdict)
            if condition_to_down:
                if makexml:
                    super().writexml(directory_url, destination_url, tree)
                    logging.info(f"*/Wrote xml for {pmcid}/")
                    paperdict["downloaded"] = True
            if condition_to_download_pdf:
                if getpdf:
                    pdf_destination = os.path.join(
                        str(os.getcwd()), pmcid, "fulltext.pdf")
                    if "pdflinks" in paperdict:
                        if len(paperdict["pdflinks"]) > 0:
                            super().writepdf(
                                paperdict["pdflinks"], pdf_destination)
                            paperdict["pdfdownloaded"] = True
                            logging.info(f"Wrote the pdf file for {pmcid}")
            dict_to_write = super().clean_dict_for_csv(paperdict)
            if condition_to_download_json:
                super().makejson(jsonurl, dict_to_write)
                paperdict["jsondownloaded"] = True
            if condition_to_download_csv:
                if makecsv:
                    self.make_csv(dict_to_write, pmcid)
                    paperdict["csvmade"] = True
            super().makejson(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'), final_xml_dict)
            stop = time.time()
            logging.debug(f"Time elapsed: {stop - start}")
            logging.debug(f"*/Updating the json*/\n")

    def make_csv(self, dict_to_write, pmcid):
        """
        Makes csv file for the dict_to_write (python dictionary for the fulltext).

        :param dict_to_write: Python dictionary to write the csv from

        :param pmcid: pmcid of the paper

        """
        import pandas as pd
        import os
        df = pd.Series(dict_to_write).to_frame(
            'Info_By_EuropePMC_Api')
        df.to_csv(os.path.join(
            str(os.getcwd()), pmcid, "fulltext.csv"))

    def conditions_to_download(self, paperdict):
        """
        Writes the conditions to download pdf, json and csv

        :param paperdict: dictionary to write rules for
        """
        condition_to_down = paperdict["downloaded"] is False
        condition_to_download_pdf = paperdict["pdfdownloaded"] is False
        condition_to_download_json = paperdict["jsondownloaded"] is False
        condition_to_download_csv = paperdict["csvmade"] is False
        return condition_to_down, condition_to_download_csv, condition_to_download_json, condition_to_download_pdf

    def get_urls_to_write_to(self, pmcid):
        """
        :param pmcid: pmcid to write the urls for

        :return: tuple containing urls where files for the fulltext will be written
        """
        import os
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
        return citationurl, destination_url, directory_url, jsonurl, referenceurl, supplementaryfilesurl

    def apipaperdownload(self, query, size, onlymakejson=False, getpdf=False, makecsv=False, makexml=False,
                         references=False, citations=False, supplementaryFiles=False, synonym=True):
        """
        Downloads and writes papers along with the metadata for the given query

        :param query: Query to download papers for

        :param size: Number of papers to be downloaded

        :param *onlymakejson(bool): Weather to only write the json files

        :param *getpdf(bool): Weather to make pdf files

        :param *makecsv(bool): Weather to make csv files

        :param *makexml(bool):Weather to make xml files

        :param *references: Source to get the references from

        :param *citations: Source to get the citations from

        :param *supplementaryFiles(bool): Weather to write supplementary files

        :param *synonym(bool): Weather to also get files with query as the synonym of the given query
        """
        import os
        query_result = self.europepmc(query, size, synonym=synonym)
        self.makecsv(query_result, makecsv=makecsv)

        if not (onlymakejson):
            read_json = super().readjsondata(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'))
            self.makexmlfiles(read_json, getpdf=getpdf, makecsv=makecsv, makexml=makexml,
                              references=references, citations=citations, supplementaryFiles=supplementaryFiles)

    def updatecorpus(self, query, original_json, size, onlymakejson=False, getpdf=False, makecsv=False, makexml=False,
                     references=False, citations=False, supplementaryFiles=False, synonym=True):
        """
        Updates the corpus with new papers

        :param query(str):  Query to download papers for

        :param original_json: Json of the original corpus in the form of python dictionary

        :param size(int): Number of new papers to download

        :param *onlymakejson(bool): Weather to only write json files

        :param *getpdf(bool): Weather to make pdf files

        :param *makecsv(bool): Weather to make csv files

        :param *makexml(bool): Weather to make xml files

        :param *references: Source to get the references from

        :param *citations: Source to get the citations from

        :param *supplementaryFiles(bool): Weather to write supplementary files

        :param *synonym(bool): Weather to also get files with query as the synonym of the given query

        """
        import os
        query_result = self.europepmc(
            query, size, update=original_json, synonym=synonym)
        self.makecsv(query_result, makecsv=makecsv,
                     update=original_json)
        if not onlymakejson:
            read_json = super().readjsondata(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'))
            self.makexmlfiles(read_json, getpdf=getpdf,
                              makecsv=makecsv, makexml=makexml, references=references, citations=citations,
                              supplementaryFiles=supplementaryFiles)

    def noexecute(self, query, synonym=True):
        """
        Tells how many hits found for the query

        :param query:

        :param synonym:
        """
        import logging
        builtqueryparams = super().buildquery(
            '*', 25, query, synonym=synonym)
        result = super().postquery(
            builtqueryparams['headers'], builtqueryparams['payload'])
        totalhits = result['responseWrapper']['hitCount']
        logging.info(f'Total number of hits for the query are {totalhits}')

    def handlecli(self):
        """
        Handles the command line interface using argparse
        """
        version = "0.0.3.1"
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
        parser.add_argument("-l", '--loglevel', default="info",
                            help="Provide logging level.  Example --log warning <<info,warning,debug,error,critical>>, default='info'")
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
                            help="Updates the corpus by downloading new papers. Takes the path of metadata json file of the orignal corpus as the input. Requires -k or --limit (If not provided, default will be used) and -q or --query (must be provided) to be given. Takes the path to the json as the input.")
        parser.add_argument("--onlyquery", action='store_true',
                            help="Saves json file containing the result of the query in storage. The json file can be given to --restart to download the papers later.")
        parser.add_argument("-c", "--makecsv", default=False, action='store_true',
                            help="Stores the per-document metadata as csv. Works only with --api method.")
        parser.add_argument("--synonym", default=False, action='store_true',
                            help="Results contain synonyms as well.")
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
            self.noexecute(args.query, synonym=args.synonym)
        elif args.version:
            logging.info(version)
        elif args.restart:
            import os
            import logging
            read_json = super().readjsondata(args.restart)
            os.chdir(os.path.dirname(os.path.dirname(args.restart)))
            self.makexmlfiles(read_json, getpdf=args.pdf, makecsv=args.makecsv, makexml=args.xml,
                              references=args.references, citations=args.citations, supplementaryFiles=args.supp)
        elif args.update:
            read_json = super().readjsondata(args.update)
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


def demo():
    """
    Shows demo to use the library to download papers
    """
    callgetpapers = pygetpapers()
    query = "artificial intelligence"
    numberofpapers = 210
    callgetpapers.apipaperdownload(query, numberofpapers)


def main():
    """
    Runs the CLI
    """
    callpygetpapers = pygetpapers()
    callpygetpapers.handlecli()


if __name__ == "__main__":
    main()
