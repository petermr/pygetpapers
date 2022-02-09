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

class Dict2Class(object):
      
    def __init__(self, my_dict):
          
        for key in my_dict:
            setattr(self, key, my_dict[key])
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
        

    
    def assist_warning_api(self,args):
        """[summary]

        :param args: [description]
        :type args: [type]
        :raises PygetpapersError: [description]
        """ 
        for feature in self.features_not_supported_by_api:
            if getattr(args,feature):
                logging.warning(f"{feature} is not supported by {args.api}")
        if args.query and (args.api == BIORXIV or args.api == MEDRXIV):
            raise PygetpapersError(
                "*rxiv doesnt support giving a query. Please provide a date interval or number of "
                "results to get instead")
        if (
            not args.query
            and not args.restart
            and not args.terms
            and not args.api == BIORXIV
            and not args.api == MEDRXIV
            and not args.version
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
    def handle_adding_date_to_query(args):
        """This functions handles the adding date to the query

        :param args: args passed down from argparse

        """

        if args.startdate and not args.enddate:
            args.enddate = strftime("%Y-%m-%d", gmtime())

        if not args.startdate:
            args.date_or_number_of_papers = args.limit
        else:
            args.date_or_number_of_papers = f"{args.startdate}/{args.enddate}"

        if args.startdate and args.enddate:
            args.query = (
                f"({args.query}) AND (FIRST_PDATE:[{args.startdate} TO {args.enddate}])"
            )
        elif args.enddate:
            args.query = f"({args.query}) AND (FIRST_PDATE:[TO {args.enddate}])"

    @staticmethod
    def handle_adding_terms_from_file(args):
        """This functions handles the adding of terms to the query

        :param args: args passed down from argparse

        """
        if args.terms:
            terms = args.terms
            seperator = "AND"
        elif args.notterms:
            terms = args.notterms
            seperator = "AND NOT"
        if terms.endswith('.txt'):
            with open(terms, "r") as file_handler:
                all_terms = file_handler.read()
            terms_list = all_terms.split(",")
        elif terms.endswith('.xml'):
            tree = ET.parse(terms)
            root = tree.getroot()
            terms_list = []
            for para in root.iter(ENTRY):
                terms_list.append(para.attrib[TERM])

        or_ed_terms = " OR ".join(terms_list)

        if args.query:
            args.query = f"({args.query} {seperator} ({or_ed_terms}))"
        else:
            if args.terms:
                args.query = f"({or_ed_terms})"
            elif args.notterms:
                raise PygetpapersError("Please provide a query with not")


    def handle_cli_logic(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        try:
            self.assist_warning_api(args)
        except PygetpapersError as err:
            logging.warning(err.message)
            return

        if not args.query and args.terms:
            args.query = None

        if self.term:
            if args.terms or args.notterms:
                try:
                    self.handle_adding_terms_from_file(args)
                except PygetpapersError as err:
                    logging.warning(err.message)
                    return

        try:
            self.handle_adding_date_to_query(args)
        except PygetpapersError as err:
            logging.warning(err.message)
            return

        if args.noexecute:
            try:
                self.api.noexecute(args)
            except PygetpapersError as err:
                logging.warning(err.message)
                return
        elif args.restart and self.restart:
            try:
                self.api.restart(args)
            except PygetpapersError as err:
                logging.warning(err.message)
                return
        elif args.update and self.update:
            logging.info(
                "Please ensure that you are providing the same --api as the one in the corpus or "
                "you may get errors")
            try:
                self.api.update(args)
            except PygetpapersError as err:
                logging.warning(err.message)
                return
        else:
            try:
                self.api.apipaperdownload(args)
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
    def handle_write_configuration_file(args):
        """This functions handles the writing the args to a configuration file

        :param args: This functions handles the assigning of apis for update

        """
        parser = configparser.ConfigParser()

        parsed_args = vars(args)

        parser.add_section(SAVED)
        for key in parsed_args.keys():
            parser.set(SAVED, key, str(parsed_args[key]))

        with open(SAVED_CONFIG_INI, "w") as file_handler:
            parser.write(file_handler)

    def handle_logfile(self, args, level):
        """This functions handles storing of logs in a logfile

        :param args: args passed down from argparse
        :param level: level of logger

        """
        location_to_store_logs = os.path.join(args.output, args.logfile)
        self.download_tools.check_or_make_directory(args.output)
        logging.basicConfig(filename=location_to_store_logs,
                            level=level, filemode="a")
        console = logging.StreamHandler()
        console.setLevel(level)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)
        logging.info("Making log file at %s", location_to_store_logs)

    @staticmethod
    def handle_output_directory(args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        if os.path.exists(args.output):
            os.chdir(args.output)
        elif not args.noexecute and not args.update and not args.restart and not args.version:
            os.makedirs(args.output)
            os.chdir(args.output)

    def handle_logger_creation(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        levels = {
            "critical": logging.CRITICAL,
            "error": logging.ERROR,
            "warn": logging.WARNING,
            "warning": logging.WARNING,
            "info": logging.INFO,
            "debug": logging.DEBUG,
        }
        level = levels.get(args.loglevel.lower())

        if level == logging.DEBUG:
            tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)

        if args.logfile:
            self.handle_logfile(args, level)
        else:
            coloredlogs.install(level=level, fmt='%(levelname)s: %(message)s')
    
    def run_command(self,output=False,query=False,save_query=False,xml=False,pdf=False,supp=False,zip=False,references=False,noexecute=False,citations=False,limit=100,restart=False,update=False,onlyquery=False,makecsv=False,makehtml=False,synonym=False,startdate=False,enddate=False,terms=False,notterms=False,api="europe_pmc",filter=None,loglevel="info",logfile=False,version=False):
        got_parameters = locals()
        if output==False:
            got_parameters["output"]=self.default_path
        args= Dict2Class(got_parameters)
        self.handle_running_of_args(args)

    def handle_running_of_args(self,args):
        self.handle_logger_creation(args)
        self.handle_output_directory(args)
        if args.version:
            logging.info("You are running pygetpapers version %s", self.version)
            return
        if args.save_query:
            self.handle_write_configuration_file(args)
        if args.api not in list(self.download_tools.config):
            raise PygetpapersError("API not supported yet")
            return 
        api_handler = ApiPlugger(args.api)
        api_handler.handle_cli_logic(args)
        
    def handlecli(self):
        """Handles the command line interface using argparse"""
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
        args = parser.parse_args()
        for arg in vars(args):
            if vars(args)[arg] == "False":
                vars(args)[arg] = False
        self.handle_running_of_args(args)
        


def main():
    """Runs the CLI"""
    callpygetpapers = Pygetpapers()
    callpygetpapers.handlecli()


if __name__ == "__main__":
    main()

# TODO:Fill docstrings
# TODO: -results.json only the last file gets chosen
# TODO:Add a guide on how to add new repositories
