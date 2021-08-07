import os
import logging
import sys
import glob
import ntpath
from time import gmtime, strftime
import configargparse
import configparser
import coloredlogs
from tqdm import tqdm
from functools import partialmethod
from pygetpapers.download_tools import DownloadTools
from pygetpapers.europe_pmc import EuropePmc
from pygetpapers.crossref import CrossRef
from pygetpapers.arxiv import Arxiv
from pygetpapers.rxiv import Rxiv
from pygetpapers.rxivist import Rxivist


class Pygetpapers:
    """[summary]"""

    def __init__(self):
        """This function makes all the constants"""
        self.crossref = CrossRef()
        self.arxiv = Arxiv()
        self.europe_pmc = EuropePmc()
        self.rxiv = Rxiv()
        self.rxivist = Rxivist()
        self.download_tools = DownloadTools("europepmc")
        self.version = self.download_tools.get_version()

    @staticmethod
    def handle_adding_terms_from_file(args):
        """This functions handles the adding of terms to the query

        :param args: args passed down from argparse

        """
        with open(args.terms, "r") as file_handler:
            all_terms = file_handler.read()
            terms_list = all_terms.split(",")
            or_ed_terms = " OR ".join(terms_list)
            if args.query:
                args.query = f"({args.query} AND ({or_ed_terms}))"
            else:
                args.query = f"({or_ed_terms})"

    def handle_noexecute(self, args):
        """This functions handles the assigning of apis for no execute command

        :param args: args passed down from argparse

        """
        if args.api == "eupmc":
            self.europe_pmc.eupmc_noexecute(args.query, synonym=args.synonym)
        elif args.api == "crossref":
            self.crossref.noexecute(args.query)
        elif args.api == "biorxiv" or args.api == "medrxiv":
            self.rxiv.noexecute(args.date_or_number_of_papers, source=args.api)
        elif args.api == "rxivist":
            self.rxivist.noexecute(args.query)
        elif args.api == "arxiv":
            self.arxiv.noexecute(args.query)

    def handle_update(self, args):
        """This functions handles the assigning of apis for update

        :param args: args passed down from argparse

        """
        update_file_path = self.get_metadata_results_file()
        logging.info(
            "Please ensure that you are providing the same --api as the one in the corpus or you may get errors")
        if args.api == "eupmc":
            self.europe_pmc.eupmc_update(args, update_file_path)
        elif args.api == "crossref":
            self.crossref.crossref_update(
                args.query, args.limit, filter_dict=args.filter, update=update_file_path
            )
        elif args.api == "biorxiv":
            self.rxiv.rxiv_update(
                args.date_or_number_of_papers,
                args.limit,
                source="biorxiv",
                update=update_file_path,
                makecsv=args.makecsv,
                makexml=args.xml,
                makehtml=args.makehtml,
            )
        elif args.api == "medrxiv":
            self.rxiv.rxiv_update(
                args.date_or_number_of_papers,
                args.limit,
                source="medrxiv",
                update=update_file_path,
                makecsv=args.makecsv,
                makexml=args.xml,
                makehtml=args.makehtml,
            )
        elif args.api == "rxivist":
            self.rxivist.rxivist_update(
                args.query,
                args.limit,
                update=update_file_path,
                makecsv=args.makecsv,
                makexml=args.xml,
                makehtml=args.makehtml,
            )
        elif args.api == "arxiv":
            logging.warning("update currently not supported for arxiv")

    def get_metadata_results_file(self):
        list_of_metadata_jsons = glob.glob(os.path.join(os.getcwd(), "*.json"))
        update_file_path = None
        for file in list_of_metadata_jsons:
            metadata_file = ntpath.basename(file)
            if metadata_file.endswith("results.json"):
                update_file_path = file
        if not update_file_path:
            logging.warning(
                "Corpus not existing in this directory. Please rerun the query without --update or --restart")
            sys.exit(1)
        return update_file_path

    def handle_query_download(self, args):
        """This functions handles the assigning of apis for query download

        :param args: args passed down from argparse

        """
        if args.api == "eupmc":
            self.europe_pmc.eupmc_apipaperdownload(
                args.query,
                args.limit,
                onlymakejson=args.onlyquery,
                getpdf=args.pdf,
                makecsv=args.makecsv,
                makehtml=args.makehtml,
                makexml=args.xml,
                references=args.references,
                citations=args.citations,
                supplementary_files=args.supp,
                zip_files=args.zip,
                synonym=args.synonym,
            )
        elif args.api == "crossref":
            self.crossref.download_and_save_results(
                args.query,
                args.limit,
                filter_dict=args.filter,
                makecsv=args.makecsv,
                makexml=args.xml,
                makehtml=args.makehtml,
            )
        elif args.api == "biorxiv":
            self.rxiv.download_and_save_results(
                args.date_or_number_of_papers,
                args.limit,
                source="biorxiv",
                makecsv=args.makecsv,
                makexml=args.xml,
                makehtml=args.makehtml,
            )
        elif args.api == "medrxiv":
            self.rxiv.download_and_save_results(
                args.date_or_number_of_papers,
                args.limit,
                source="medrxiv",
                makecsv=args.makecsv,
                makexml=args.xml,
                makehtml=args.makehtml,
            )
        elif args.api == "rxivist":
            self.rxivist.download_and_save_results(
                args.query,
                args.limit,
                makecsv=args.makecsv,
                makexml=args.xml,
                makehtml=args.makehtml,
            )
        elif args.api == "arxiv":
            self.arxiv.arxiv(
                args.query,
                args.limit,
                getpdf=args.pdf,
                makecsv=args.makecsv,
                makexml=args.xml,
                makehtml=args.makehtml,
            )

    @staticmethod
    def handle_write_configuration_file(args):
        """This functions handles the writing the args to a configuration file

        :param args: This functions handles the assigning of apis for update

        """
        parser = configparser.ConfigParser()

        parsed_args = vars(args)

        parser.add_section("SAVED")
        for key in parsed_args.keys():
            parser.set("SAVED", key, str(parsed_args[key]))

        with open("saved_config.ini", "w") as file_handler:
            parser.write(file_handler)

    @staticmethod
    def handle_logfile(args, level):
        """This functions handles storing of logs in a logfile

        :param args: args passed down from argparse
        :param level: level of logger

        """
        logging.basicConfig(filename=args.logfile, level=level, filemode="w")
        console = logging.StreamHandler()
        console.setLevel(level)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        # tell the handler to use this format
        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)
        logging.info("Making log file at %s", args.logfile)

    def handle_restart(self, args):
        """This functions handles the assigning of apis for restarting the downloads

        :param args: args passed down from argparse

        """
        restart_file_path = self.get_metadata_results_file()
        if args.api == "eupmc":
            self.europe_pmc.eupmc_restart(args, restart_file_path)
        else:
            logging.warning("Restart currently not supported for this repo")

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

    def handle_output_directory(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        if os.path.exists(args.output):
            os.chdir(args.output)
        elif not args.noexecute and not args.update and not args.restart and not args.version:
            os.makedirs(args.output)
            os.chdir(args.output)

    def handle_query_creation(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        if (
            not args.query
            and not args.restart
            and not args.terms
            and not args.version
            and not args.api == "biorxiv"
            and not args.api == "medrxiv"
        ):
            logging.warning("Please specify a query")
            sys.exit(1)

        if (args.api == "biorxiv" or args.api == "medrxiv") and args.query:
            logging.warning(
                "*rxiv doesnt support giving a query. Please provide a date interval or number of results to get instead")
            sys.exit(1)

        if not args.query and args.terms:
            args.query = None

    def handle_logger_creation(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        coloredlogs.install()
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

    def warn_if_feature_not_supported_for_api(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        if (args.api == "medrxiv" or args.api == "biorxiv"):
            logging.warning(
                "Currently biorxiv api is malfunctioning and returning wrong DOIs")
        if (args.api != "eupmc" and args.api != "arxiv") and args.pdf:
            logging.warning("Pdf is not supported for this api")
        if (args.api != "eupmc" and args.api != "biorxiv" and args.api != "medrxiv") and (args.startdate or args.enddate):
            logging.warning("Date is not supported for this api")
        if (args.api != "crossref") and args.filter:
            logging.warning("filter is not supported for this api")
        if (args.api != "eupmc") and args.synonym:
            logging.warning("synonym is not supported for this api")
        if (args.api != "eupmc") and args.onlyquery:
            logging.warning("onlyquery is not supported for this api")
        if (args.api != "eupmc") and args.onlyquery:
            logging.warning("onlyquery is not supported for this api")
        if (args.api != "eupmc") and args.citations:
            logging.warning("citations is not supported for this api")
        if (args.api != "eupmc") and args.references:
            logging.warning("references is not supported for this api")
        if (args.api != "eupmc") and args.supp:
            logging.warning(
                "supplementary files is not supported for this api")
        if (args.api != "eupmc") and args.zip:
            logging.warning("zip files is not supported for this api")

    def handlecli(self):
        """Handles the command line interface using argparse"""
        version = self.version

        default_path = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
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
            default=os.path.join(os.getcwd(), default_path),
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
            help="[ALL] report how many results match the query, but don't actually download anything",
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
            help="[All] save log to specified file in output directory as well as printing to terminal",
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
            help="[E] Saves json file containing the result of the query in storage. (only eupmc supported)"
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
            help="[All] Location of the txt file which contains terms serperated by a comma which will be"
            "OR'ed among themselves and AND'ed with the query",
        )
        parser.add_argument(
            "--api",
            default="eupmc",
            type=str,
            help="API to search [eupmc, crossref,arxiv,biorxiv,medrxiv,rxivist] (default: eupmc)",
        )
        parser.add_argument(
            "--filter",
            default=None,
            type=str,
            help="[C] filter by key value pair (only crossref supported)",
        )
        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit()
        args = parser.parse_args()
        for arg in vars(args):
            if vars(args)[arg] == "False":
                vars(args)[arg] = False
        self.handle_logger_creation(args)
        self.warn_if_feature_not_supported_for_api(args)
        self.handle_query_creation(args)
        self.handle_output_directory(args)
        if args.version:
            logging.info("You are running pygetpapers version %s", version)
        if args.save_query:
            self.handle_write_configuration_file(args)
        if args.restart:
            self.handle_restart(args)
            sys.exit(1)

        if args.api == "eupmc" or args.api == "medrxiv" or args.api == "biorxiv":
            self.handle_adding_date_to_query(args)

        if args.terms:
            self.handle_adding_terms_from_file(args)

        if args.query and not (args.api == "medrxiv" or args.api == "biorxiv"):
            logging.info("Final query is %s", args.query)

        if args.noexecute:
            self.handle_noexecute(args)
            sys.exit(1)

        elif args.update:
            self.handle_update(args)
            sys.exit(1)

        else:
            if args.query or args.api == "biorxiv" or args.api == "medrxiv":
                self.handle_query_download(args)


def demo():
    """Shows demo to use the library to download papers"""
    callgetpapers = Pygetpapers()
    query = "artificial intelligence"
    numberofpapers = 210
    callgetpapers.europe_pmc.eupmc_apipaperdownload(query, numberofpapers)


def main():
    """Runs the CLI"""
    callpygetpapers = Pygetpapers()
    callpygetpapers.handlecli()


if __name__ == "__main__":
    main()

# TODO:Add tests for arxiv and rxiv and rxivist
# TODO:Fill docstrings
