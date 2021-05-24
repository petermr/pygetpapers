from logging import fatal
from pygetpapers.download_tools import download_tools
from pygetpapers.europe_pmc import europe_pmc


class pygetpapers():

    def __init__(self):
        """This function makes all the constants"""
        import os
        import configparser
        with open(os.path.join(os.path.dirname(__file__), "config.ini")) as f:
            config_file = f.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_string(config_file)
        self.version = config.get("pygetpapers", "version")
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
        self.europe_pmc = europe_pmc()
        self.directory_url = os.path.join(
            str(os.getcwd()))
        self.download_tools = download_tools("europepmc")

    def make_initial_columns_for_paper_dict(self, pmcid, resultant_dict):
        """

        :param pmcid: pmcid of the paper for which fields will be created
        :param resultant_dict: dict in which the fields will be created
        :returns: dict with the initial fields created for pmcid

        """
        resultant_dict[pmcid] = {}
        resultant_dict[pmcid]["downloaded"] = False
        resultant_dict[pmcid]["pdfdownloaded"] = False
        resultant_dict[pmcid]["jsondownloaded"] = False
        resultant_dict[pmcid]["csvmade"] = False
        resultant_dict[pmcid]["htmlmade"] = False
        return resultant_dict
    # this is the function that will the the result from search and will download and save the files.

    def makecsv(self, searchvariable, makecsv=False, makehtml=False, update=False):
        """Writes the json and csv for searchvaraible dict

        :param searchvariable: dict): Python dictionary which contains all the research papers (given by europe_pmc.europepmc))
        :param makecsv: bool): whether to make csv files (Default value = False)
        :param update: dict): if provided, will add the research papers to the searchvariable dict (Default value = False)
        :param makehtml: Default value = False)
        :returns: searchvariable

        """
        import pandas as pd
        import json
        import os
        import logging
        resultant_dict = {}
        if searchvariable:
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
            htmlurl = os.path.join(
                str(os.getcwd()), 'eupmc_results.html')
            self.download_tools.check_or_make_directory(directory_url)
            self.download_tools.makejson(jsonurl, resultant_dict)
            resultant_dict_for_csv = self.download_tools.make_dict_for_csv(
                resultant_dict)
            df = pd.DataFrame.from_dict(resultant_dict_for_csv, )
            df_transposed = df.T
            if makecsv:
                self.download_tools.write_or_append_to_csv(df_transposed)
            if makehtml:
                self.download_tools.make_html_from_dataframe(df, htmlurl)
            return searchvariable
        else:
            logging.warning("API gave empty result")
            return False

    def write_meta_data_for_paper(self, paper, paper_number, resultant_dict):
        """Adds pdf and html url as well as makes the paper key in resultant_dict

        :param paper: python dictionary for the paper
        :param paper_number: paper number to log
        :param resultant_dict: dictionary to add paper as well as pdf,html url to
        :returns: htmlurl, paperpmcid, pdfurl, resultant_dict)

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
        """Writes urls to dictionary

        :param htmlurl: list containing html urls for the paper
        :param paper: python dictionary of the paper
        :param paper_number: paper number to log
        :param pdfurl: list containing pdf urls for the paper
        :param dict_for_paper: python dictionary to write the urls to
        :returns: dict_for_paper

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
            author_list = []
            for author in paper["authorList"]["author"]:
                author_list.append(author['fullName'])
            dict_for_paper[self.AUTHORINFO
                           ] = author_list
        except:
            logging.warning(
                f"Author list not found for paper {paper_number}")
        try:
            dict_for_paper[self.TITLE] = paper[self.TITLE]
        except:
            logging.warning(
                f"Title not found for paper {paper_number}")

    def make_references(self, directory_url, paperid, source, referenceurl):
        """Downloads the references for the paper with pmcid (paperid) to reference url

        :param directory_url: directory containing referenceurl
        :param paperid: pmc id of the paper
        :param source: source to get the citations from
        :param referenceurl: path to write the references to

        """
        getreferences = self.download_tools.getreferences(
            paperid, source)
        self.writexml(directory_url, referenceurl, getreferences)

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

    def make_citations(self, source, citationurl, directory_url, paperid):
        """Downloads the citations for the paper with pmcid (paperid) to citation url

        :param source: source to get the citations from
        :param citationurl: path to write the citations to
        :param directory_url: directory containing citationurl
        :param paperid: pmc id of the paper

        """
        getcitations = self.download_tools.getcitations(
            paperid, source)
        self.writexml(directory_url, citationurl, getcitations)

    def makexmlfiles(self, final_xml_dict, getpdf=False, makecsv=False, makehtml=False, makexml=False, references=False,
                     citations=False, supplementaryFiles=False, zipFiles=False):
        """Writes the pdf,csv,xml,references,citations,supplementaryFiles for the individual papers

        :param final_xml_dict: Python dictionary containg all the papers
        :param getpdf: bool): whether to make pdfs (Default value = False)
        :param makecsv: bool): whether to make csv for the metadata (Default value = False)
        :param makexml: bool): whether to make xml file for the paper (Default value = False)
        :param references: bool): whether to download references (Default value = False)
        :param citations: bool): whether to download citations (Default value = False)
        :param supplementaryFiles: bool): whether to download supplementary files (Default value = False)
        :param makehtml: Default value = False)
        :param zipFiles:  (Default value = False)

        """
        import logging
        import os
        import time
        if makexml:
            self.download_tools.log_making_xml()
        paper_number = 0
        for paper in final_xml_dict:
            start = time.time()
            paper_number += 1
            pmcid = paper
            tree = self.download_tools.getxml(pmcid)
            citationurl, destination_url, directory_url, jsonurl, referenceurl, supplementaryfilesurl, htmlurl, zipurl = self.get_urls_to_write_to(
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
                self.download_tools.getsupplementaryfiles(
                    pmcid, directory_url, supplementaryfilesurl)
            if zipFiles:
                self.download_tools.getsupplementaryfiles(
                    pmcid, directory_url, zipurl, fromFtpEndpoint=True)
            if not os.path.isdir(directory_url):
                os.makedirs(directory_url)
            condition_to_down, condition_to_download_csv, condition_to_download_json, condition_to_download_pdf, condition_to_html = self.download_tools.conditions_to_download(
                paperdict)
            if condition_to_down:
                if makexml:
                    self.download_tools.writexml(
                        directory_url, destination_url, tree)
                    logging.info(f"*/Wrote xml for {pmcid}/")
                    paperdict["downloaded"] = True
            if condition_to_download_pdf:
                if getpdf:
                    pdf_destination = os.path.join(
                        str(os.getcwd()), pmcid, "fulltext.pdf")
                    if "pdflinks" in paperdict:
                        if len(paperdict["pdflinks"]) > 0:
                            self.download_tools.writepdf(
                                paperdict["pdflinks"], pdf_destination)
                            paperdict["pdfdownloaded"] = True
                            logging.info(f"Wrote the pdf file for {pmcid}")
            dict_to_write = self.download_tools.clean_dict_for_csv(paperdict)
            if condition_to_download_json:
                self.download_tools.makejson(jsonurl, dict_to_write)
                paperdict["jsondownloaded"] = True
            if condition_to_download_csv:
                if makecsv:
                    self.make_csv(dict_to_write, pmcid)
                    paperdict["csvmade"] = True
            if condition_to_html:
                if makehtml:
                    self.download_tools.make_html_from_dict(
                        dict_to_write, htmlurl)
                    logging.info(f"Wrote the html file for {pmcid}")
                    paperdict["htmlmade"] = True
            self.download_tools.makejson(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'), final_xml_dict)
            stop = time.time()
            logging.debug(f"Time elapsed: {stop - start}")
            logging.debug(f"*/Updating the json*/\n")

    def make_csv(self, dict_to_write, pmcid):
        """Makes csv file for the dict_to_write (python dictionary for the fulltext).

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
        """Writes the conditions to download pdf, json and csv

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
        :returns: tuple containing urls where files for the fulltext will be written

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
            str(os.getcwd()), pmcid, "supplementaryfiles")
        zipurl = os.path.join(
            str(os.getcwd()), pmcid, "ftpfiles")
        htmlurl = os.path.join(str(os.getcwd()), pmcid, "eupmc_result.html")
        return citationurl, destination_url, directory_url, jsonurl, referenceurl, supplementaryfilesurl, htmlurl, zipurl

    def apipaperdownload(self, query, size, onlymakejson=False, getpdf=False, makecsv=False, makehtml=False, makexml=False,
                         references=False, citations=False, supplementaryFiles=False, synonym=True, zipFiles=False):
        """Downloads and writes papers along with the metadata for the given query

        :param query: Query to download papers for
        :param size: Number of papers to be downloaded
        :param onlymakejson: Default value = False)
        :param getpdf: Default value = False)
        :param makecsv: Default value = False)
        :param makehtml: Default value = False)
        :param makexml: Default value = False)
        :param references: Default value = False)
        :param citations: Default value = False)
        :param supplementaryFiles: Default value = False)
        :param synonym: Default value = True)
        :param zipFiles:  (Default value = False)

        """
        import os
        query_result = self.europe_pmc.europepmc(query, size, synonym=synonym)
        is_search_successful = self.makecsv(
            query_result, makecsv=makecsv, makehtml=makehtml)

        if not (onlymakejson) and is_search_successful is not False:
            read_json = self.download_tools.readjsondata(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'))
            self.makexmlfiles(read_json, getpdf=getpdf, makecsv=makecsv, makexml=makexml, makehtml=makehtml,
                              references=references, citations=citations, supplementaryFiles=supplementaryFiles, zipFiles=zipFiles)

    def updatecorpus(self, query, original_json, size, onlymakejson=False, getpdf=False, makehtml=False, makecsv=False, makexml=False,
                     references=False, citations=False, supplementaryFiles=False, synonym=True, zipFiles=False):
        """Updates the corpus with new papers

        :param query: str):  Query to download papers for
        :param original_json: Json of the original corpus in the form of python dictionary
        :param size: int): Number of new papers to download
        :param onlymakejson: Default value = False)
        :param getpdf: Default value = False)
        :param makehtml: Default value = False)
        :param makecsv: Default value = False)
        :param makexml: Default value = False)
        :param references: Default value = False)
        :param citations: Default value = False)
        :param supplementaryFiles: Default value = False)
        :param synonym: Default value = True)
        :param zipFiles:  (Default value = False)

        """
        import os
        query_result = self.europe_pmc.europepmc(
            query, size, update=original_json, synonym=synonym)
        is_search_successful = self.makecsv(query_result, makecsv=makecsv, makehtml=makehtml,
                                            update=original_json)
        if not (onlymakejson) and is_search_successful is not False:
            read_json = self.download_tools.readjsondata(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'))
            self.makexmlfiles(read_json, getpdf=getpdf,
                              makecsv=makecsv, makexml=makexml, makehtml=makehtml, references=references, citations=citations,
                              supplementaryFiles=supplementaryFiles, zipFiles=zipFiles)

    def noexecute(self, query, synonym=True):
        """Tells how many hits found for the query

        :param query: param synonym:
        :param synonym: Default value = True)

        """
        import logging
        builtqueryparams = self.download_tools.buildquery(
            '*', 25, query, synonym=synonym)
        HEADERS = 'headers'
        PAYLOAD = 'payload'
        result = self.download_tools.postquery(
            builtqueryparams[HEADERS], builtqueryparams[PAYLOAD])
        totalhits = result['responseWrapper']['hitCount']
        logging.info(f'Total number of hits for the query are {totalhits}')

    def handle_write_configuration_file(self, args):
        """

        :param args: 

        """
        import configparser
        parser = configparser.ConfigParser()

        parsed_args = vars(args)

        parser.add_section('SAVED')
        for key in parsed_args.keys():
            parser.set('SAVED', key, str(parsed_args[key]))

        with open('saved_config.ini', 'w') as f:
            parser.write(f)

    def handlecli(self):
        """Handles the command line interface using argparse"""
        version = self.version
        import argparse
        import os
        import configargparse
        import logging
        import sys
        from time import gmtime, strftime
        default_path = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
        parser = configargparse.ArgParser(
            description=f"Welcome to Pygetpapers version {version}. -h or --help for help")
        parser.add_argument('--config', is_config_file=True,
                            help='config file path to read query for pygetpapers')

        parser.add_argument("-v", "--version",
                            default=False, action="store_true", help="output the version number")
        parser.add_argument("-q", "--query",
                            type=str, default=False,
                            help="query string transmitted to repository API. Eg. \"Artificial Intelligence\" or \"Plant Parts\". To escape special characters within the quotes, use backslash. Incase of nested quotes, ensure that the initial quotes are double and the qutoes inside are single. For eg: `'(LICENSE:\"cc by\" OR LICENSE:\"cc-by\") AND METHODS:\"transcriptome assembly\"' ` is wrong. We should instead use `\"(LICENSE:'cc by' OR LICENSE:'cc-by') AND METHODS:'transcriptome assembly'\"` ")

        parser.add_argument("-o", "--output",
                            type=str, help="output directory (Default: Folder inside current working directory named )", default=os.path.join(os.getcwd(), default_path))
        parser.add_argument("--save_query", default=False, action='store_true',
                            help="saved the passed query in a config file")
        parser.add_argument("-x", "--xml", default=False, action='store_true',
                            help="download fulltext XMLs if available")
        parser.add_argument("-p", "--pdf", default=False, action='store_true',
                            help="download fulltext PDFs if available")
        parser.add_argument("-s", "--supp", default=False, action='store_true',
                            help="download supplementary files if available	")
        parser.add_argument("-z", "--zip", default=False, action='store_true',
                            help="download files from ftp endpoint if available	")
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
                            help="Stores the per-document metadata as csv.")
        parser.add_argument("--makehtml", default=False, action='store_true',
                            help="Stores the per-document metadata as html.")
        parser.add_argument("--synonym", default=False, action='store_true',
                            help="Results contain synonyms as well.")
        parser.add_argument("--startdate", default=False,
                            type=str,
                            help="Gives papers starting from given date. Format: YYYY-MM-DD")
        parser.add_argument("--enddate", default=False,
                            type=str,
                            help="Gives papers till given date. Format: YYYY-MM-DD")
        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit()
        args = parser.parse_args()
        for arg in vars(args):
            if vars(args)[arg] == "False":
                vars(args)[arg] = False
        if os.path.exists(args.output):
            os.chdir(args.output)
        elif not args.noexecute and not args.update and not args.restart:
            os.makedirs(args.output)
            os.chdir(args.output)
        if args.save_query:
            self.handle_write_configuration_file(args)
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

        if args.restart:
            import os
            import logging
            read_json = self.download_tools.readjsondata(args.restart)
            os.chdir(os.path.dirname(args.restart))
            self.makexmlfiles(read_json, getpdf=args.pdf, makecsv=args.makecsv, makehtml=args.makehtml, makexml=args.xml,
                              references=args.references, citations=args.citations, supplementaryFiles=args.supp, zipFiles=args.zip)
        if not args.query and not args.restart:
            logging.warning('Please specify a query')
            sys.exit(1)

        if args.startdate and not args.enddate:
            args.enddate = strftime("%Y-%d-%m", gmtime())

        if args.startdate and args.enddate:
            args.query = f'({args.query}) AND (FIRST_PDATE:[{args.startdate} TO {args.enddate}])'
        elif args.enddate:
            args.query = f'({args.query}) AND (FIRST_PDATE:[TO {args.enddate}])'

        if args.noexecute:
            self.noexecute(args.query, synonym=args.synonym)
        elif args.version:
            logging.info(version)
        elif args.update:
            read_json = self.download_tools.readjsondata(args.update)
            os.chdir(os.path.dirname(args.update))
            self.updatecorpus(args.query, read_json, args.limit, getpdf=args.pdf,
                              makecsv=args.makecsv, makexml=args.xml, references=args.references, makehtml=args.makehtml,
                              citations=args.citations, supplementaryFiles=args.supp, synonym=args.synonym, zipFiles=args.zip)
        else:
            if args.query:
                self.apipaperdownload(args.query, args.limit,
                                      onlymakejson=args.onlyquery, getpdf=args.pdf, makecsv=args.makecsv, makehtml=args.makehtml,
                                      makexml=args.xml, references=args.references, citations=args.citations,
                                      supplementaryFiles=args.supp, zipFiles=args.zip, synonym=args.synonym)


def demo():
    """Shows demo to use the library to download papers"""
    callgetpapers = pygetpapers()
    query = "artificial intelligence"
    numberofpapers = 210
    callgetpapers.apipaperdownload(query, numberofpapers)


def main():
    """Runs the CLI"""
    callpygetpapers = pygetpapers()
    callpygetpapers.handlecli()


if __name__ == "__main__":
    main()
