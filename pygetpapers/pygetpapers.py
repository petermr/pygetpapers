import ast
import configparser
import importlib
import logging
import os
import sys
import xml.etree.ElementTree as ET
from functools import partialmethod
from time import gmtime, strftime

import coloredlogs
import configargparse
from tqdm import tqdm

from pygetpapers.download_tools import DownloadTools
from pygetpapers.pgexceptions import PygetpapersError

MEDRXIV = "medrxiv"
CROSSREF = "crossref"
BIORXIV = "biorxiv"
ARXIV = "arxiv"
EUPMC = "eupmc"
SAVED_CONFIG_INI = "saved_config.ini"
SAVED = "SAVED"
RESULTS_JSON = "results.json"
RXIVIST = "rxivist"
TERM = "term"
ENTRY = 'entry'
EUROPEPMC = "europe_pmc"
PYGETPAPERS="pygetpapers"
CONFIG_INI = "config.ini"
CLASSNAME="class_name"
LIBRARYNAME="library_name"
FEATURESNOTSUPPORTED = "features_not_supported"

class ApiPlugger:
    
    def __init__(self,api):
        """[summary]

        :param api: [description]
        :type api: [type]
        """
        self.download_tools = DownloadTools(api)
        self.setup_api_support_variables(self.download_tools.config, api)
        api_class = getattr(importlib.import_module(f'{PYGETPAPERS}.{self.library_name}'),self.class_name)
        self.api= api_class()
        

    
    def assist_warning_api(self, query_namespace):
        """[summary]

        :param query_namespace: [description]
        :type query_namespace: [type]
        :raises PygetpapersError: [description]
        """ 
        for feature in self.features_not_supported_by_api:
            if query_namespace[feature]:
                logging.warning(f'{feature} is not supported by {query_namespace["api"]}')
        if query_namespace["query"] and (query_namespace["api"] == BIORXIV or query_namespace["api"] == MEDRXIV):
            raise PygetpapersError(
                "*rxiv doesnt support giving a query. Please provide a date interval or number of "
                "results to get instead")
        if (
            not query_namespace["query"]
            and not query_namespace["restart"]
            and not query_namespace["terms"]
            and not query_namespace["api"] == BIORXIV
            and not query_namespace["api"] == MEDRXIV
            and not query_namespace["version"]
        ):
            raise PygetpapersError("Please specify a query")

    def setup_api_support_variables(self, config, api):
        """[summary]

        :param config: [description]
        :type config: [type]
        :param api: [description]
        :type api: [type]
        """
        self.class_name = config.get(api,CLASSNAME)
        self.library_name = config.get(api,LIBRARYNAME)
        self.date_query = config.get(api,"date_query") == "SUPPORTED"
        self.term = config.get(api,"term") == "SUPPORTED"
        self.update = config.get(api,"update") == "SUPPORTED"
        self.restart = config.get(api,"restart") == "SUPPORTED"
        self.features_not_supported_by_api = ast.literal_eval(config.get(api,FEATURESNOTSUPPORTED))

    @staticmethod
    def _add_date_to_query(query_namespace):
        """Builds query from simple dates in --startdate and --enddate. (See https://pygetpapers.readthedocs.io/en/latest/index.html#download-papers-within-certain-start-and-end-date-range)
        Edits the namespace object's query flag.

        :param query_namespace: namespace object from argparse (using --startdate and --enddate)

        """

        if query_namespace["startdate"] and not query_namespace["enddate"]:
            query_namespace["enddate"] = strftime("%Y-%m-%d", gmtime())

        if not query_namespace["startdate"]:
            query_namespace["date_or_number_of_papers"] = query_namespace["limit"]
        else:
            query_namespace["date_or_number_of_papers"] = f'{query_namespace["startdate"]}/{query_namespace["enddate"]}'

        if query_namespace["startdate"] and query_namespace["enddate"]:
            query_namespace["query"] = (
                f'({query_namespace["query"]}) AND (FIRST_PDATE:[{query_namespace["startdate"]} TO {query_namespace["enddate"]}])'
            )
        elif query_namespace["enddate"]:
            query_namespace["query"] = f'({query_namespace["query"]}) AND (FIRST_PDATE:[TO {query_namespace["enddate"]}])'

    @staticmethod
    def add_terms_from_file(query_namespace):
        """Builds query from terms mentioned in a text file described in the argparse namespace object. See (https://pygetpapers.readthedocs.io/en/latest/index.html?highlight=terms#querying-using-a-term-list)
        Edits the namespace object's query flag.

        :param query_namespace: namespace object from argparse (using --terms and --notterms)

        """
        if query_namespace["terms"]:
            terms_path = query_namespace["terms"]
            separator = "AND"
        elif query_namespace["notterms"]:
            terms_path = query_namespace["notterms"]
            separator = "AND NOT"
        if terms_path.endswith('.txt'):
            with open(terms_path, "r") as file_handler:
                all_terms = file_handler.read()
            terms_list = all_terms.split(",")
        elif terms_path.endswith('.xml'):
            tree = ET.parse(terms_path)
            root = tree.getroot()
            terms_list = []
            for para in root.iter(ENTRY):
                terms_list.append(para.attrib[TERM])

        or_ed_terms = " OR ".join(terms_list)
        #modify query in namespace object
        if query_namespace["query"]:
            query_namespace["query"] = f'({query_namespace["query"]} {separator} ({or_ed_terms}))'
        else:
            if query_namespace["terms"]:
                query_namespace["query"] = f"({or_ed_terms})"
            elif query_namespace["notterms"]:
                raise PygetpapersError("Please provide a query with not")


    def check_query_syntax_and_values(self, query_namespace):
        """[summary]

        :param query_namespace: [description]
        :type query_namespace: [type]
        """
        try:
            self.assist_warning_api(query_namespace)
        except PygetpapersError as err:
            logging.warning(err.message)
            return

        if not query_namespace["query"] and query_namespace["terms"]:
            query_namespace["query"] = None

        if self.term:
            if query_namespace["terms"] or query_namespace["notterms"]:
                try:
                    self.add_terms_from_file(query_namespace)
                except PygetpapersError as err:
                    logging.warning(err.message)
                    return

        try:
            self._add_date_to_query(query_namespace)
        except PygetpapersError as err:
            logging.warning(err.message)
            return

        if query_namespace["noexecute"]:
            try:
                self.api.noexecute(query_namespace)
            except PygetpapersError as err:
                logging.warning(err.message)
                return
        elif query_namespace["restart"] and self.restart:
            try:
                self.api.restart(query_namespace)
            except PygetpapersError as err:
                logging.warning(err.message)
                return
        elif query_namespace["update"] and self.update:
            logging.info(
                "Please ensure that you are providing the same --api as the one in the corpus or "
                "you may get errors")
            try:
                self.api.update(query_namespace)
            except PygetpapersError as err:
                logging.warning(err.message)
                return
        else:
            try:
                self.api.apipaperdownload(query_namespace)
            except PygetpapersError as err:
                logging.warning(err.message)
                return

class Pygetpapers:
    """[summary]"""

    def __init__(self):
        """This function makes all the constants"""
        self.download_tools = DownloadTools()
        self.version = self.download_tools.get_version()
        default_path = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
        self.default_path= os.path.join(os.getcwd(), default_path)

    @staticmethod
    def write_configuration_file(query_namespace):
        """Writes the argparse namespace to SAVED_CONFIG_INI

        :param query_namespace: argparse namespace object

        """
        parser = configparser.ConfigParser()

        parsed_args = vars(query_namespace)

        parser.add_section(SAVED)
        for key in parsed_args.keys():
            parser.set(SAVED, key, str(parsed_args[key]))

        with open(SAVED_CONFIG_INI, "w") as file_handler:
            parser.write(file_handler)

    def write_logfile(self, query_namespace, level):
        """This functions stores logs to a logfile

        :param query_namespace: argparse namespace object
        :param level: level of logger (See https://docs.python.org/3/library/logging.html#logging-levels)

        """
        location_to_store_logs = os.path.join(query_namespace["output"], query_namespace["logfile"])
        self.download_tools.check_or_make_directory(query_namespace["output"])
        logging.basicConfig(filename=location_to_store_logs,
                            level=level, filemode="a")
        console = logging.StreamHandler()
        console.setLevel(level)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)
        logging.info("Making log file at %s", location_to_store_logs)

    @staticmethod
    def makes_output_directory(query_namespace):
        """[summary]

        :param query_namespace: [description]
        :type query_namespace: [type]
        """
        if os.path.exists(query_namespace["output"]):
            os.chdir(query_namespace["output"])
        elif not query_namespace["noexecute"] and not query_namespace["update"] and not query_namespace["restart"] and not query_namespace["version"]:
            os.makedirs(query_namespace["output"])
            os.chdir(query_namespace["output"])

    def generate_logger(self, query_namespace):
        """[summary]

        :param query_namespace: [description]
        :type query_namespace: [type]
        """
        levels = {
            "critical": logging.CRITICAL,
            "error": logging.ERROR,
            "warn": logging.WARNING,
            "warning": logging.WARNING,
            "info": logging.INFO,
            "debug": logging.DEBUG,
        }
        level = levels.get(query_namespace["loglevel"].lower())

        if level == logging.DEBUG:
            tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)

        if query_namespace["logfile"]:
            self.write_logfile(query_namespace, level)
        else:
            coloredlogs.install(level=level, fmt='%(levelname)s: %(message)s')
    
    def run_command(self,output=None,query=None,save_query=False,xml=False,pdf=False,supp=False,zip=False,references=False,noexecute=False,citations=False,limit=100,restart=False,update=False,onlyquery=False,makecsv=False,makehtml=False,synonym=False,startdate=False,enddate=False,terms=False,notterms=False,api="europe_pmc",filter=None,loglevel="info",logfile=False,version=False):
        """_summary_

        :param output: _description_, defaults to None
        :type output: _type_, optional
        :param query: _description_, defaults to None
        :type query: _type_, optional
        :param save_query: _description_, defaults to False
        :type save_query: bool, optional
        :param xml: _description_, defaults to False
        :type xml: bool, optional
        :param pdf: _description_, defaults to False
        :type pdf: bool, optional
        :param supp: _description_, defaults to False
        :type supp: bool, optional
        :param zip: _description_, defaults to False
        :type zip: bool, optional
        :param references: _description_, defaults to False
        :type references: bool, optional
        :param noexecute: _description_, defaults to False
        :type noexecute: bool, optional
        :param citations: _description_, defaults to False
        :type citations: bool, optional
        :param limit: _description_, defaults to 100
        :type limit: int, optional
        :param restart: _description_, defaults to False
        :type restart: bool, optional
        :param update: _description_, defaults to False
        :type update: bool, optional
        :param onlyquery: _description_, defaults to False
        :type onlyquery: bool, optional
        :param makecsv: _description_, defaults to False
        :type makecsv: bool, optional
        :param makehtml: _description_, defaults to False
        :type makehtml: bool, optional
        :param synonym: _description_, defaults to False
        :type synonym: bool, optional
        :param startdate: _description_, defaults to False
        :type startdate: bool, optional
        :param enddate: _description_, defaults to False
        :type enddate: bool, optional
        :param terms: _description_, defaults to False
        :type terms: bool, optional
        :param notterms: _description_, defaults to False
        :type notterms: bool, optional
        :param api: _description_, defaults to "europe_pmc"
        :type api: str, optional
        :param filter: _description_, defaults to None
        :type filter: _type_, optional
        :param loglevel: _description_, defaults to "info"
        :type loglevel: str, optional
        :param logfile: _description_, defaults to False
        :type logfile: bool, optional
        :param version: _description_, defaults to False
        :type version: bool, optional
        """
        got_parameters = locals()
        if output==False:
            got_parameters["output"]=self.default_path
        self.runs_pygetpapers_for_given_args(got_parameters)

    def runs_pygetpapers_for_given_args(self,query_namespace):
        self.generate_logger(query_namespace)
        self.makes_output_directory(query_namespace)
        if query_namespace["version"]:
            logging.info("You are running pygetpapers version %s", self.version)
            return
        if query_namespace["save_query"]:
            self.write_configuration_file(query_namespace)
        if query_namespace["api"] not in list(self.download_tools.config):
            raise PygetpapersError("API not supported yet")
            return 
        api_handler = ApiPlugger(query_namespace["api"])
        api_handler.check_query_syntax_and_values(query_namespace)
        
    def create_argparser(self):
        """_summary_
        """        
        version = self.version

        parser = configargparse.ArgParser(
            description=f"Welcome to Pygetpapers version {version}. -h or --help for help",
            add_config_file_help=False,
        )
        parser.add_argument(
            "--config",
            is_config_file=True,
            help="config file path to read query for pygetpapers",
        )

        parser.add_argument(
            "-v",
            "--version",
            default=False,
            action="store_true",
            help="output the version number",
        )
        parser.add_argument(
            "-q",
            "--query",
            type=str,
            default=False,
            help="query string transmitted to repository API. "
                 'Eg. "Artificial Intelligence" or "Plant Parts". '
                 "To escape special characters within the quotes, use backslash. "
                 "Incase of nested quotes, ensure that the initial "
                 "quotes are double and the qutoes inside are single. "
                 'For eg: `\'(LICENSE:"cc by" OR LICENSE:"cc-by") '
                 'AND METHODS:"transcriptome assembly"\' ` '
                 "is wrong. We should instead use `\"(LICENSE:'cc by' OR LICENSE:'cc-by') "
                 "AND METHODS:'transcriptome assembly'\"` ",
        )

        parser.add_argument(
            "-o",
            "--output",
            type=str,
            help="output directory (Default: Folder inside current working directory named )",
            default=self.default_path,
        )
        parser.add_argument(
            "--save_query",
            default=False,
            action="store_true",
            help="saved the passed query in a config file",
        )
        parser.add_argument(
            "-x",
            "--xml",
            default=False,
            action="store_true",
            help="download fulltext XMLs if available or save metadata as XML",
        )
        parser.add_argument(
            "-p",
            "--pdf",
            default=False,
            action="store_true",
            help="[E][A] download fulltext PDFs if available (only eupmc and arxiv supported)",
        )
        parser.add_argument(
            "-s",
            "--supp",
            default=False,
            action="store_true",
            help="[E] download supplementary files if available (only eupmc supported)	",
        )
        parser.add_argument(
            "-z",
            "--zip",
            default=False,
            action="store_true",
            help="[E] download files from ftp endpoint if available (only eupmc supported)	",
        )
        parser.add_argument(
            "--references",
            type=str,
            default=False,
            help="[E] Download references if available. (only eupmc supported)"
                 "Requires source for references (AGR,CBA,CTX,ETH,HIR,MED,PAT,PMC,PPR).",
        )
        parser.add_argument(
            "-n",
            "--noexecute",
            default=False,
            action="store_true",
            help="[ALL] report how many results match the query, but don't actually download "
                 "anything",
        )

        parser.add_argument(
            "--citations",
            type=str,
            default=False,
            help="[E] Download citations if available (only eupmc supported). "
                 "Requires source for citations (AGR,CBA,CTX,ETH,HIR,MED,PAT,PMC,PPR).",
        )
        parser.add_argument(
            "-l",
            "--loglevel",
            default="info",
            help="[All] Provide logging level.  "
                 "Example --log warning <<info,warning,debug,error,critical>>, default='info'",
        )
        parser.add_argument(
            "-f",
            "--logfile",
            default=False,
            type=str,
            help="[All] save log to specified file in output directory as well as printing to "
                 "terminal",
        )
        parser.add_argument(
            "-k",
            "--limit",
            default=100,
            type=int,
            help="[All] maximum number of hits (default: 100)",
        )

        parser.add_argument(
            "-r",
            "--restart",
            action="store_true",
            help="[E] Downloads the missing flags for the corpus."
                 "Searches for already existing corpus in the output directory",
        )

        parser.add_argument(
            "-u",
            "--update",
            action="store_true",
            help="[E][B][M][C] Updates the corpus by downloading new papers. "
                 "Requires -k or --limit "
                 "(If not provided, default will be used) and -q or --query "
                 "(must be provided) to be given. "
                 "Searches for already existing corpus in the output directory",
        )
        parser.add_argument(
            "--onlyquery",
            action="store_true",
            help="[E] Saves json file containing the result of the query in storage. (only eupmc "
                 "supported) "
                 "The json file can be given to --restart to download the papers later.",
        )
        parser.add_argument(
            "-c",
            "--makecsv",
            default=False,
            action="store_true",
            help="[All] Stores the per-document metadata as csv.",
        )
        parser.add_argument(
            "--makehtml",
            default=False,
            action="store_true",
            help="[All] Stores the per-document metadata as html.",
        )
        parser.add_argument(
            "--synonym",
            default=False,
            action="store_true",
            help="[E] Results contain synonyms as well.",
        )
        parser.add_argument(
            "--startdate",
            default=False,
            type=str,
            help="[E][B][M] Gives papers starting from given date. Format: YYYY-MM-DD",
        )
        parser.add_argument(
            "--enddate",
            default=False,
            type=str,
            help="[E][B][M] Gives papers till given date. Format: YYYY-MM-DD",
        )
        parser.add_argument(
            "--terms",
            default=False,
            type=str,
            help="[All] Location of the file which contains terms serperated by a comma or an ami "
                 "dict which will be "
                 "OR'ed among themselves and AND'ed with the query",
        )
        parser.add_argument(
            "--notterms",
            default=False,
            type=str,
            help="[All] Location of the txt file which contains terms serperated by a comma or an "
                 "ami dict which will be "
                 "OR'ed among themselves and NOT'ed with the query",
        )
        parser.add_argument(
            "--api",
            default="europe_pmc",
            type=str,
            help="API to search [europe_pmc, crossref,arxiv,biorxiv,medrxiv,rxivist] (default: europe_pmc)",
        )
        parser.add_argument(
            "--filter",
            default=None,
            type=str,
            help="[C] filter by key value pair (only crossref supported)",
        )
        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            return
        query_namespace = vars(parser.parse_args())
        for arg in (query_namespace):
            if (query_namespace)[arg] == "False":
                (query_namespace)[arg] = False
        self.runs_pygetpapers_for_given_args(query_namespace)
        


def main():
    """Runs the CLI"""
    callpygetpapers = Pygetpapers()
    callpygetpapers.create_argparser()


if __name__ == "__main__":
    main()

#TODO: add half a sentence about config queries