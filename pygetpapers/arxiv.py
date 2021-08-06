import os
import logging
import arxiv
from tqdm import tqdm
from pygetpapers.download_tools import DownloadTools


class Arxiv:
    """Arxiv class which handles arxiv repository"""

    def __init__(self):
        """[summary]"""
        self.download_tools = DownloadTools("arxiv")

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
            self.download_tools.add_keys_for_conditions(paper, return_dict)
        if getpdf:
            self.download_pdf(return_dict)
        self.download_tools.handle_creation_of_csv_html_xml(
            makecsv, makehtml, makexml, return_dict, "arxiv-result"
        )
        self.make_json_from_arxiv_dict(return_dict)

        return return_dict

    def make_json_from_arxiv_dict(self, return_dict):
        """[summary]

        :param return_dict: [description]
        :type return_dict: [type]
        """
        jsonurl = os.path.join(os.getcwd(), "arxiv_results.json")
        self.download_tools.makejson(jsonurl, return_dict)
        for result in tqdm(return_dict):
            return_dict[result]["jsondownloaded"] = True
            self.download_tools.check_or_make_directory(result)
            jsonurl = os.path.join(os.getcwd(), result, "arxiv_result.json")
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
            paper_dict["date_updated"] = str(
                result.updated)
            paper_dict["date_published"] = str(
                result.published
            )
            paper_dict["title"] = str(result.title)
            paper_dict["authors"] = str(
                result.authors)
            paper_dict["summary"] = str(
                result.summary)
            paper_dict["comment"] = str(
                result.comment)
            paper_dict["journal_ref"] = str(
                result.journal_ref
            )
            paper_dict["doi"] = str(result.doi)
            paper_dict["primary_category"] = str(
                result.primary_category
            )
            paper_dict["categories"] = str(
                result.categories)
            paper_dict["links"] = str(result.links)
            paper_dict["pdf_url"] = str(
                result.pdf_url)
            paper_dict["entry_id"] = str(
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
            pdf_url = os.path.join(os.getcwd(), result, "fulltext.pdf")
            self.download_tools.write_content_to_destination(
                return_dict[result]["pdf_url"], pdf_url
            )
            return_dict[result]["pdfdownloaded"] = True

    @staticmethod
    def noexecute(query):
        """[summary]

        :param query: [description]
        :type query: [type]
        """
        logging.info("Arxiv api working for the query %s", query)
