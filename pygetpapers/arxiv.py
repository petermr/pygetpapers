import logging
import os

from tqdm import tqdm

import arxiv
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


class Arxiv:
    """Arxiv class which handles arxiv repository"""

    def __init__(self):
        """[summary]"""
        self.download_tools = DownloadTools(ARXIV)

    def arxiv(
            self, query, size, getpdf=False, makecsv=False, makexml=False, makehtml=False
    ):
        """[summary]

        :param query: [description]
        :type query: [type]
        :param size: [description]
        :type size: [type]
        :param getpdf: [description], defaults to False
        :type getpdf: bool, optional
        :param makecsv: [description], defaults to False
        :type makecsv: bool, optional
        :param makexml: [description], defaults to False
        :type makexml: bool, optional
        :param makehtml: [description], defaults to False
        :type makehtml: bool, optional
        :return: [description]
        :rtype: [type]
        """
        logging.info("Making request to Arxiv through pygetpapers")
        search = arxiv.Search(
            query=query, max_results=size, sort_by=arxiv.SortCriterion.Relevance
        )

        return_dict = {}
        logging.info("Got request result from Arxiv through pygetpapers")

        self.make_dict_from_arxiv_output(return_dict, search)
        for paper in return_dict:
            self.download_tools.add_download_status_keys(paper, return_dict)
        if getpdf:
            self.download_pdf(return_dict)
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv, makehtml, makexml, return_dict, ARXIV_RESULT
        )
        self.make_json_from_arxiv_dict(return_dict)

        return return_dict

    def make_json_from_arxiv_dict(self, return_dict):
        """[summary]

        :param return_dict: [description]
        :type return_dict: [type]
        """
        jsonurl = os.path.join(os.getcwd(), ARXIV_RESULTS_JSON)
        self.download_tools.makejson(jsonurl, return_dict)
        for result in tqdm(return_dict):
            return_dict[result][JSONDOWNLOADED] = True
            self.download_tools.check_or_make_directory(result)
            jsonurl = os.path.join(os.getcwd(), result, ARXIV_RESULT_JSON)
            self.download_tools.makejson(jsonurl, return_dict[result])

    @staticmethod
    def make_dict_from_arxiv_output(return_dict, search):
        """[summary]

        :param return_dict: [description]
        :type return_dict: [type]
        :param search: [description]
        :type search: [type]
        """
        for result in search.get():
            url_encoded_id_of_paper = str(result.entry_id).rsplit("/", 1)[-1]

            return_dict[url_encoded_id_of_paper] = {}
            paper_dict = return_dict[url_encoded_id_of_paper]
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

    def download_pdf(self, return_dict):
        """[summary]

        :param return_dict: [description]
        :type return_dict: [type]
        """
        logging.info("Downloading Pdfs for papers")
        for result in tqdm(return_dict):
            self.download_tools.check_or_make_directory(
                os.path.join(os.getcwd(), result)
            )
            pdf_url = os.path.join(os.getcwd(), result, FULLTEXT_PDF)
            self.download_tools.write_content_to_destination(
                return_dict[result][PDF_URL], pdf_url
            )
            return_dict[result][PDFDOWNLOADED] = True

    @staticmethod
    def noexecute(args):
        """[summary]

        :param query: [description]
        :type query: [type]
        """
        logging.info("Arxiv api working for the query %s", args.query)

    @staticmethod
    def update(args):
        logging.warning("update currently not supported for arxiv")

    def apipaperdownload(self, args):
        self.arxiv(
            args.query,
            args.limit,
            getpdf=args.pdf,
            makecsv=args.makecsv,
            makexml=args.xml,
            makehtml=args.makehtml,
        )   