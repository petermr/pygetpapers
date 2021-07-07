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
        """

        :param query: param size:
        :param getpdf: Default value = False)
        :param makecsv: Default value = False)
        :param makexml: Default value = False)
        :param makehtml: Default value = False)
        :param size:

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
        """

        :param return_dict:

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
        """

        :param return_dict: param search:
        :param search:

        """
        for result in search.get():
            url_encoded_id_of_paper = str(result.entry_id).rsplit("/", 1)[-1]

            return_dict[url_encoded_id_of_paper] = {}
            return_dict[url_encoded_id_of_paper]["date_updated"] = str(
                result.updated)
            return_dict[url_encoded_id_of_paper]["date_published"] = str(
                result.published
            )
            return_dict[url_encoded_id_of_paper]["title"] = str(result.title)
            return_dict[url_encoded_id_of_paper]["authors"] = str(
                result.authors)
            return_dict[url_encoded_id_of_paper]["summary"] = str(
                result.summary)
            return_dict[url_encoded_id_of_paper]["comment"] = str(
                result.comment)
            return_dict[url_encoded_id_of_paper]["journal_ref"] = str(
                result.journal_ref
            )
            return_dict[url_encoded_id_of_paper]["doi"] = str(result.doi)
            return_dict[url_encoded_id_of_paper]["primary_category"] = str(
                result.primary_category
            )
            return_dict[url_encoded_id_of_paper]["categories"] = str(
                result.categories)
            return_dict[url_encoded_id_of_paper]["links"] = str(result.links)
            return_dict[url_encoded_id_of_paper]["pdf_url"] = str(
                result.pdf_url)
            return_dict[url_encoded_id_of_paper]["entry_id"] = str(
                result.entry_id)

    def download_pdf(self, return_dict):
        """

        :param return_dict:

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
        """

        :param query:

        """
        logging.info("Arxiv api working for the query %s", query)
