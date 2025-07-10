import json
import logging
import os
from pathlib import Path

from tqdm import tqdm

from pygetpapers.config_loader import get_repository_config
from pygetpapers.download_tools import DownloadTools
from pygetpapers.errors import PygetpapersError
from pygetpapers.pygetpapers import (
    BIORXIV,
)
from pygetpapers.repositoryinterface import (
    COLLECTION,
    DOI,
    RXIV_RESULT,
    RepositoryInterface,
)

TOTAL_HITS = "total_hits"
NEW_RESULTS = "new_results"
UPDATED_DICT = "updated_dict"
JATSXML = "jatsxml"
FULLTEXT_XML = "fulltext.xml"
TOTAL_JSON_OUTPUT = "total_json_output"
MESSAGES = "messages"
TOTAL = "total"
CURSOR_MARK = "cursor_mark"
RXIV = "rxiv"


class Rxiv(RepositoryInterface):
    """Biorxiv and Medrxiv repositories

    At present (2022-03) the API appears only to support date searches.
    The `rxivist` system is layered on top and supports fuller queries

    """

    def __init__(self, api="biorxiv"):
        """Initialize the bioRxiv repository interface.

        Args:
            api: Repository type ('biorxiv' or 'medrxiv')
        """
        self.api = api
        self.download_tools = DownloadTools()
        self.get_url = None
        self.config = get_repository_config("biorxiv")

        # Log repository capabilities
        logging.info("bioRxiv repository capabilities:")
        logging.info(f"  API: {self.config.get_capability('api')}")
        logging.info(f"  Web scraper: {self.config.get_capability('web_scraper')}")
        logging.info(f"  Text queries: {self.config.get_capability('text_queries')}")
        logging.info(f"  Date queries: {self.config.get_capability('date_queries')}")

    def has_capability(self, capability: str) -> bool:
        """Check if the repository has a specific capability.

        Args:
            capability: Name of the capability to check

        Returns:
            True if capability is available, False otherwise
        """
        return self.config.get_capability(capability)

    def rxiv(
        self,
        query,
        cutoff_size,
        source=BIORXIV,
        update=None,
        makecsv=False,
        makehtml=False,
    ):

        if update:
            cursor_mark = update[CURSOR_MARK]
        else:
            cursor_mark = 0
        total_number_of_results = 0
        total_papers_list = []
        logging.info("Making Request to rxiv")
        while len(total_papers_list) <= cutoff_size:
            total_number_of_results, total_papers_list, papers_list = (
                self.make_request_add_papers(
                    query,
                    cursor_mark,
                    source,
                    total_number_of_results,
                    total_papers_list,
                )
            )
            if len(papers_list) == 0:
                logging.warning("No more papers found")
                break
            cursor_mark += 1
        total_result_list = total_papers_list[:cutoff_size]
        json_metadata_dictionary = self.download_tools._make_dict_from_list(
            total_result_list, paper_key=DOI
        )
        for paper in json_metadata_dictionary:
            self.download_tools._add_download_status_keys(
                paper, json_metadata_dictionary
            )
        result_dict = self.download_tools._adds_new_results_to_metadata_dictionary(
            cursor_mark,
            json_metadata_dictionary,
            total_number_of_results,
            update=update,
        )

        metadata_dictionary = result_dict[NEW_RESULTS][TOTAL_JSON_OUTPUT]
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv=makecsv,
            makehtml=makehtml,
            makexml=False,
            metadata_dictionary=metadata_dictionary,
            name=RXIV_RESULT,
        )
        return result_dict

    def make_request_add_papers(
        self, interval, cursor_mark, source, total_number_of_results, total_papers_list
    ):
        self.make_request_url_for_rxiv(cursor_mark, interval, source)
        request_handler = self.download_tools.post_query(self.get_url)
        request_dict = json.loads(request_handler.text)
        papers_list = request_dict[COLLECTION]
        final_list = []
        for paper in papers_list:
            # Ensure DOI has the correct format for pygetpapers
            if DOI in paper and paper[DOI]:
                # Add https://doi.org/ prefix if not present
                if not paper[DOI].startswith("https://doi.org/"):
                    paper[DOI] = "https://doi.org/" + paper[DOI]

                # Add "id" field that download_tools expects (using DOI as ID)
                paper["id"] = paper[DOI]

                if paper[DOI] not in self.doi_done:
                    final_list.append(paper)
                    self.doi_done.append(paper[DOI])
            else:
                logging.warning(
                    f"Paper missing DOI field: {paper.get('title', 'Unknown title')}"
                )
        if TOTAL in request_dict[MESSAGES][0]:
            total_number_of_results = request_dict[MESSAGES][0][TOTAL]
        total_papers_list += final_list
        return total_number_of_results, total_papers_list, final_list

    def make_request_url_for_rxiv(self, cursor_mark, interval, source):
        if isinstance(interval, int):
            self.get_url = "https://api.biorxiv.org/details/{source}/{interval}".format(
                source=source, interval=interval
            )
        else:
            self.get_url = self.download_tools.query_url.format(
                source=source, interval=interval, cursor=cursor_mark
            )

    def rxiv_update(
        self,
        interval,
        cutoff_size,
        source=BIORXIV,
        update=None,
        makecsv=False,
        makexml=False,
        makehtml=False,
    ):

        os.chdir(os.path.dirname(update))
        update = self.download_tools.readjsondata(update)
        logging.info("Reading old json metadata file")
        self.download_and_save_results(
            interval,
            cutoff_size,
            update=update,
            source=source,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )

    def download_and_save_results(
        self,
        query,
        cutoff_size,
        source,
        update=False,
        makecsv=False,
        makexml=False,
        makehtml=False,
    ):

        if update and isinstance(query, int):
            raise PygetpapersError("Update will not work if date not provided")

        result_dict = self.rxiv(
            query,
            cutoff_size,
            update=update,
            source=source,
            makecsv=makecsv,
            makehtml=makehtml,
        )
        if makexml:
            logging.info("Making xml for paper")
            dict_of_papers = result_dict[NEW_RESULTS][TOTAL_JSON_OUTPUT]
            self.make_xml_for_rxiv(dict_of_papers, JATSXML, DOI, FULLTEXT_XML)
        self.download_tools._make_metadata_json_files_for_paper(
            result_dict[NEW_RESULTS],
            updated_dict=result_dict[UPDATED_DICT],
            paper_key=DOI,
            name_of_file=RXIV_RESULT,
        )

    def make_xml_for_rxiv(
        self, dict_of_papers, xml_identifier, paper_id_identifier, filename
    ):

        for paper in tqdm(dict_of_papers):
            dict_of_paper = dict_of_papers[paper]
            xml_url = dict_of_paper[xml_identifier]
            doi_of_paper = dict_of_paper[paper_id_identifier]
            url_encoded_doi_of_paper = self.download_tools.url_encode_id(doi_of_paper)
            self.download_tools.check_or_make_directory(url_encoded_doi_of_paper)
            path_to_save_xml = os.path.join(
                str(os.getcwd()), url_encoded_doi_of_paper, filename
            )
            self.download_tools.queries_the_url_and_writes_response_to_destination(
                xml_url, path_to_save_xml
            )

    def noexecute(self, query_namespace):
        """Test query without downloading papers"""

        query = query_namespace["query"]
        source = query_namespace["api"]

        # Check if query is a text query
        if self._is_text_query(query):
            logging.info("Using bioRxiv web scraper for text query (noexecute mode)")
            try:
                from .biorxiv_integration import BioRxivIntegration

                scraper = BioRxivIntegration()

                # Test the query with a small limit
                result = scraper.search_and_collect(
                    query=query, max_papers=5, save_metadata=False  # Small test limit
                )

                totalhits = result.get("papers_collected", 0)
                logging.info(f"Total number of hits for the query are {totalhits}")

            except ImportError:
                logging.error(
                    "bioRxiv web scraper integration not available for text queries"
                )
                logging.info("Text queries require the web scraper integration")
            except Exception as e:
                logging.error(f"Error testing text query: {e}")
        else:
            # Use existing API for date/number queries
            time_interval = query_namespace["query"]
            result_dict = self.rxiv(time_interval, cutoff_size=10, source=source)
            totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
            logging.info("Total number of hits for the query are %s", totalhits)

    def update(self, query_namespace):

        update_file_path = self.download_tools.get_metadata_results_file()
        logging.info(
            "Please ensure that you are providing the same --api as the one in the "
            "corpus or you may get errors"
        )
        self.rxiv_update(
            query_namespace["query"],
            query_namespace["limit"],
            source=query_namespace["api"],
            update=update_file_path,
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            makehtml=query_namespace["makehtml"],
        )

    def apipaperdownload(self, query_namespace):
        """
        Download papers using API (for dates) or web scraper (for text queries).
        """

        query = query_namespace["query"]

        # Check if query is a date range (format: YYYY-MM-DD/YYYY-MM-DD) or number
        # If it's a text query, use the web scraper
        if self._is_text_query(query):
            logging.info("Using bioRxiv web scraper for text query")
            self._download_with_web_scraper(query_namespace)
        else:
            logging.info("Using bioRxiv API for date/number query")
            self.download_and_save_results(
                query_namespace["query"],
                query_namespace["limit"],
                query_namespace["api"],
                makecsv=query_namespace["makecsv"],
                makexml=query_namespace["xml"],
                makehtml=query_namespace["makehtml"],
            )

    def _is_text_query(self, query):
        """Check if the query is a text query (not a date range or number)"""
        if not query:
            return False

        # Check if it's a number (for API pagination)
        try:
            int(query)
            return False
        except ValueError:
            pass

        # Check if it's a date range (format: YYYY-MM-DD/YYYY-MM-DD)
        if "/" in query and len(query.split("/")) == 2:
            date_parts = query.split("/")
            try:
                # Try to parse as dates
                from datetime import datetime

                datetime.strptime(date_parts[0], "%Y-%m-%d")
                datetime.strptime(date_parts[1], "%Y-%m-%d")
                return False
            except ValueError:
                pass

        # Check if it contains letters (indicating a text query)
        if any(c.isalpha() for c in query):
            return True

        # If it's not a number or date range, it's a text query
        return True

    def _download_with_web_scraper(self, query_namespace):
        """Download papers using the bioRxiv web scraper"""
        try:
            # Import the bioRxiv web scraper integration
            import os

            from .biorxiv_integration import BioRxivIntegration

            # Get the output directory from query_namespace
            output_dir = query_namespace.get("output", "biorxiv_output")

            # Create a temporary scraper to get the papers
            temp_scraper = BioRxivIntegration(output_dir="temp_biorxiv_scraper")

            # Extract parameters
            query = query_namespace["query"]
            limit = query_namespace["limit"]
            makecsv = query_namespace["makecsv"]
            makehtml = query_namespace["makehtml"]

            # Run the web scraper to get papers
            result = temp_scraper.search_and_collect(
                query=query,
                max_papers=limit,
                save_metadata=False,  # We'll save it in the proper location
            )

            papers = result.get("papers", [])
            logging.info(f"Web scraper found {len(papers)} papers.")

            # Create the proper pygetpapers output structure
            # Create and change to the output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            os.chdir(output_dir)

            # Create the metadata structure that pygetpapers expects
            metadata_dict = {}
            total_hits = result.get("papers_collected", len(papers))

            for paper in papers:
                doi = paper["doi"]
                # URL-encode the DOI for the metadata key (as pygetpapers expects)
                url_encoded_doi = doi.replace("/", "_")

                # Save paper metadata
                metadata_dict[url_encoded_doi] = {
                    "doi": doi,
                    "title": paper.get("title", ""),
                    "authors": paper.get("authors", ""),
                    "biorxiv_id": paper.get("biorxiv_id", ""),
                    "search_query": query,
                    "download_timestamp": paper.get("download_timestamp", ""),
                    "file_size": paper.get("file_size", 0),
                    "jsondownloaded": True,
                }

                # Create the paper directory structure
                paper_dir = Path(url_encoded_doi)
                paper_dir.mkdir(exist_ok=True)

                # Copy HTML file if it exists
                html_file = paper.get("html_file")
                if html_file and Path(html_file).exists():
                    import shutil

                    shutil.copy2(html_file, paper_dir / "fulltext.html")

                # Save PDF URL if available
                pdf_url = paper.get("pdf_url")
                if pdf_url:
                    with open(paper_dir / "pdf_url.txt", "w") as f:
                        f.write(pdf_url)

            # Create the results structure that pygetpapers expects
            results_dict = {
                "total_json_output": metadata_dict,
                "total_hits": total_hits,
                "cursor_mark": 1,
            }

            # Save the metadata in pygetpapers format
            self.download_tools._make_metadata_json_files_for_paper(
                results_dict,
                updated_dict={},
                paper_key=DOI,
                name_of_file=RXIV_RESULT,
            )

            # Handle CSV/HTML export if requested
            if makecsv or makehtml:
                self.download_tools.handle_creation_of_csv_html_xml(
                    makecsv=makecsv,
                    makehtml=makehtml,
                    makexml=False,
                    metadata_dictionary=metadata_dict,
                    name=RXIV_RESULT,
                )

            # Clean up temporary directory
            import shutil

            if Path("temp_biorxiv_scraper").exists():
                shutil.rmtree("temp_biorxiv_scraper")

            logging.info(
                "Web scraper completed successfully. Downloaded %d papers to %s",
                len(papers),
                output_dir,
            )

        except ImportError:
            logging.error(
                "bioRxiv web scraper integration not available. "
                "Falling back to API-only mode."
            )
            # Fall back to API-only mode for date queries
            if not self._is_text_query(query_namespace["query"]):
                self.download_and_save_results(
                    query_namespace["query"],
                    query_namespace["limit"],
                    query_namespace["api"],
                    makecsv=query_namespace["makecsv"],
                    makexml=query_namespace["xml"],
                    makehtml=query_namespace["makehtml"],
                )
            else:
                raise PygetpapersError(
                    "Text queries for bioRxiv/medRxiv require the web scraper "
                    "integration. Please install the required dependencies or use "
                    "date-based queries instead."
                )
        except Exception as e:
            logging.error(f"Error in web scraper: {e}")
            raise PygetpapersError(f"Web scraper error: {e}")
