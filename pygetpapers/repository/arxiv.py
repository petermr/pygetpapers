import logging
import os

from tqdm import tqdm

import arxiv as arxiv_wrapper
from pygetpapers.download_tools import DownloadTools
from pygetpapers.pgexceptions import PygetpapersError

PDFDOWNLOADED = "pdfdownloaded"

PDF_URL = "pdf_url"

FULLTEXT_PDF = "fulltext.pdf"

ENTRY_ID = "entry_id"

LINKS = "links"

CATEGORIES = "categories"

PRIMARY_CATEGORY = "primary_category"

DOI = "doi"

JOURNAL_REF = "journal_ref"

COMMENT = "comment"

SUMMARY = "summary"

AUTHORS = "authors"

TITLE = "title"

DATE_PUBLISHED = "date_published"

DATE_UPDATED = "date_updated"

ARXIV_RESULT_JSON = "arxiv_result.json"

JSONDOWNLOADED = "jsondownloaded"

ARXIV_RESULTS_JSON = "arxiv_results.json"

ARXIV_RESULT = "arxiv-result"

ARXIV = "arxiv"

from pygetpapers.repositoryinterface import RepositoryInterface

class Arxiv(RepositoryInterface):
    """arxiv.org repository
    
    This uses a PyPI code `arxiv` to download metadata. It is not clear whether this is 
    created by the `arXiv` project or layered on top of the public API. 
    
    `arXiv` current practice for bulk data download (e.g. PDFs) is described in
https://arxiv.org/help/bulk_data. Please be considerate and also include a rate limit.
    
    """

    def __init__(self):
        self.download_tools = DownloadTools(ARXIV)

    def arxiv(
            self, query, cutoff_size, getpdf=False, makecsv=False, makexml=False, makehtml=False
    ):
        """Builds the arxiv searcher and writes the xml, pdf, csv and html

        :param query: query given to arxiv
        :type query: string
        :param cutoff_size: number of papers to retrieve
        :type cutoff_size: int
        :param getpdf: whether to get pdf
        :type getpdf: bool, optional
        :param makecsv: whether to get csv 
        :type makecsv: bool
        :param makehtml: whether to get html 
        :type makehtml: bool
        :param makexml: whether to get xml 
        :type makexml: bool
        :return: dictionary of results retrieved from arxiv
        :rtype: dict
        """
        logging.info("Making request to Arxiv through pygetpapers")
        search = arxiv_wrapper.Search(
            query=query, max_results=cutoff_size, sort_by=arxiv_wrapper.SortCriterion.Relevance
        )

        logging.info("Got request result from Arxiv through pygetpapers")
        search_results = search.get()
        metadata_dictionary = self._make_metadata_dict_from_arxiv_output(search_results)

        for paper in metadata_dictionary:
            self.download_tools._add_download_status_keys(paper, metadata_dictionary)
        if getpdf:
            self.download_pdf(metadata_dictionary)
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv, makehtml, makexml, metadata_dictionary, ARXIV_RESULT
        )
        self.write_metadata_json_from_arxiv_dict(metadata_dictionary)

        return metadata_dictionary

    def write_metadata_json_from_arxiv_dict(self, metadata_dictionary):
        """Iterates through metadata_dictionary and makes json metadata file for papers

        :param metadata_dictionary: metadata dictionary for papers
        :type metadata_dictionary: dict
        """
        jsonurl = os.path.join(os.getcwd(), ARXIV_RESULTS_JSON)
        self.download_tools.dumps_json_to_given_path(jsonurl, metadata_dictionary)
        for result in tqdm(metadata_dictionary):
            metadata_dictionary[result][JSONDOWNLOADED] = True
            self.download_tools.check_or_make_directory(result)
            jsonurl = os.path.join(os.getcwd(), result, ARXIV_RESULT_JSON)
            self.download_tools.dumps_json_to_given_path(jsonurl, metadata_dictionary[result])

    @staticmethod
    def _make_metadata_dict_from_arxiv_output(search_results):
        metadata_dictionary = {}
        for result in search_results:
            url_encoded_id_of_paper = str(result.entry_id).rsplit("/", 1)[-1]

            metadata_dictionary[url_encoded_id_of_paper] = {}
            paper_dict = metadata_dictionary[url_encoded_id_of_paper]
            paper_dict[DATE_UPDATED] = str(
                result.updated)
            paper_dict[DATE_PUBLISHED] = str(
                result.published
            )
            paper_dict[TITLE] = str(result.title)
            paper_dict[AUTHORS] = str(
                result.authors)
            paper_dict[SUMMARY] = str(
                result.summary)
            paper_dict[COMMENT] = str(
                result.comment)
            paper_dict[JOURNAL_REF] = str(
                result.journal_ref
            )
            paper_dict[DOI] = str(result.doi)
            paper_dict[PRIMARY_CATEGORY] = str(
                result.primary_category
            )
            paper_dict[CATEGORIES] = str(
                result.categories)
            paper_dict[LINKS] = str(result.links)
            paper_dict[PDF_URL] = str(
                result.pdf_url)
            paper_dict[ENTRY_ID] = str(
                result.entry_id)
        return metadata_dictionary

    def download_pdf(self, metadata_dictionary):
        """Downloads pdfs for papers in metadata dictionary

        :param metadata_dictionary: metadata dictionary for papers
        :type metadata_dictionary: dict
        """
        logging.info("Downloading Pdfs for papers")
        for result in tqdm(metadata_dictionary):
            self.download_tools.check_or_make_directory(
                os.path.join(os.getcwd(), result)
            )
            pdf_url = os.path.join(os.getcwd(), result, FULLTEXT_PDF)
            self.download_tools.queries_the_url_and_writes_response_to_destination(
                metadata_dictionary[result][PDF_URL], pdf_url
            )
            metadata_dictionary[result][PDFDOWNLOADED] = True

    @staticmethod
    def noexecute(query_namespace):
        logging.info("Arxiv api working for the query %s", query_namespace["query"])

    @staticmethod
    def update(query_namespace):
        logging.warning("update currently not supported for arxiv")

    def apipaperdownload(self, query_namespace):
        self.arxiv(
            query_namespace["query"],
            query_namespace["limit"],
            query_namespace["pdf"],
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            makehtml=query_namespace["makehtml"],
        )   
