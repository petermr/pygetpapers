import json
import logging
import os
import time
from numpy import True_

import pandas as pd
from tqdm import tqdm

from pygetpapers.download_tools import DownloadTools
from pygetpapers.pgexceptions import PygetpapersError
from pygetpapers.repositoryinterface import RepositoryInterface

FULLTEXT_XML = "fulltext.xml"
FULLTEXT_PDF = "fulltext.pdf"
RESULTS_JSON = "eupmc_results.json"
RESULT_JSON = "eupmc_result.json"
RESULTS_CSV = "europe_pmc.csv"
REFERENCE_XML = "references.xml"
DOWNLOADED = "downloaded"
CITATION_XML = "citation.xml"
EUROPEPMC = "europe_pmc"
SUPPLEMENTARY_FILES = "supplementaryfiles"
TITLE = "title"
AUTHOR_INFO = "authorinfo"
JOURNAL_TITLE = "journaltitle"
PDF_LINKS = "pdflinks"
HTML_LINKS = "htmllinks"
PMCID = "pmcid"
JOURNAL = "journal"
JOURNAL_INFO = "journalInfo"
FULLTEXT_CSV = "fulltext.csv"
FULL_NAME = "fullName"
RESPONSE_WRAPPER = "responseWrapper"
CURSOR_MARK = "nextCursorMark"
HITCOUNT = "hitCount"
RESULT_LIST = "resultList"
RESULT = "result"
HEADERS = "headers"
PAYLOAD = "payload"
UPDATE = "update"
FTPFILES = "ftpfiles"
EUPMC_HTML = "eupmc_result.html"
FULL_TEXT_URL = "fullTextUrl"
FULL_TEST_URL_LIST = "fullTextUrlList"
DOCUMENT_STYLE = "documentStyle"
URL = "url"
FULL = "full"
ID = "id"
AVAILABILITY = "availability"
OPEN_ACCESS = "Open access"
AUTHOR_LIST = "authorList"
AUTHOR = "author"
CSVMADE = "csvmade"
JSON_DOWNLOADED = "jsondownloaded"
HTML_MADE = "htmlmade"
PDF_DOWNLOADED = "pdfdownloaded"
ABSTRACT = "abstract"
ABSTRACT_TEXT = "abstractText"
KEYWORDS = "Keywords"
KEYWORD = "keyword"
DOCUMENTSTYLE = "documentStyle"
AVAILABILITY = "availability"
OPENACCESS = "Open access"
PDF = "pdf"
HTML = "html"


class EuropePmc(RepositoryInterface):
    """Downloads metadata and optionally fulltext from https://europepmc.org"""

    """Can optionally download supplemental author data, the content of which is irregular and
    not weell specified.
    For articles with figures, the links to the figures on the EPMC site are included in the fulltext.xml
    but the figures are NOT included. (We have are adding this functionality to our `docanalysis` and `pyamiimage`
    codes.

    In some cases a "zip" file is provided by EPMC which does contain figures in the paper and supplemntal author data;
    this can be downloaded.
    
    EPMC has a number of additional services including:
        - references and citations denoted by 3-letter codes
    
    pygetpapers can translate a standard date into EPMC format and include it in the query.
    
    """

    def __init__(self):
        self.download_tools = DownloadTools(EUROPEPMC)

    def query(self, query, cutoff_size, synonym=True, cursor_mark="*"):
        """Queries eupmc for given query for given number(cutoff_size) papers

        :param query: query
        :type query: string
        :param cutoff_size: number of papers to get
        :type cutoff_size: int
        :param synonym: whether to get synonyms, defaults to True
        :type synonym: bool, optional
        :return: list containg the papers
        :rtype: list
        """
        cutoff_size = int(cutoff_size)
        maximum_hits_per_page = 1000
        morepapers = True
        len_list_papers = 0
        counter = 0

        while len_list_papers <= cutoff_size and morepapers is True:
            retrieved_metadata_dictionary = self.build_and_send_query(
                maximum_hits_per_page, cursor_mark, query, synonym
            )
            if retrieved_metadata_dictionary:
                counter += 1
                totalhits = retrieved_metadata_dictionary[RESPONSE_WRAPPER][HITCOUNT]
                if counter == 1:
                    logging.info("Total Hits are %s", totalhits)
                if int(totalhits) == 0:
                    logging.warning("Could not find more papers")
                    break
                (
                    list_of_paper_metadata,
                    morepapers,
                ) = self._metadata_dictionary_to_list_of_dictionaries_for_each_paper(
                    retrieved_metadata_dictionary
                )
                len_list_papers += len(list_of_paper_metadata)
                morepapers, cursor_mark = self._add_cursor_mark_if_exists(
                    retrieved_metadata_dictionary
                )
        list_of_paper_metadata = self._remove_extra_papers_from_list(
            cutoff_size, list_of_paper_metadata
        )
        dictionary_with_papers = self._make_dictionary_from_list_of_papers(
            list_of_paper_metadata
        )
        # We use this dictionary_with_papers as a sub dictionary for the metadata_dictionary
        metadata_dictionary = {
            CURSOR_MARK: cursor_mark,
            "papers": dictionary_with_papers,
        }
        return metadata_dictionary

    def _remove_extra_papers_from_list(self, cutoff_size, list_of_paper_metadata):
        if len(list_of_paper_metadata) > cutoff_size:
            list_of_paper_metadata = list_of_paper_metadata[0:cutoff_size]
        return list_of_paper_metadata

    def _metadata_dictionary_to_list_of_dictionaries_for_each_paper(
        self, retireved_metadata_dictionary
    ):
        list_of_paper_metadata = []
        morepapers = True
        if RESULT in retireved_metadata_dictionary[RESPONSE_WRAPPER][RESULT_LIST]:
            single_result = isinstance(
                retireved_metadata_dictionary[RESPONSE_WRAPPER][RESULT_LIST][RESULT],
                dict,
            )
            papers = retireved_metadata_dictionary[RESPONSE_WRAPPER][RESULT_LIST][
                RESULT
            ]
            if single_result and PMCID in papers:
                list_of_paper_metadata.append(papers)
            else:
                for paper in retireved_metadata_dictionary[RESPONSE_WRAPPER][
                    RESULT_LIST
                ][RESULT]:
                    if PMCID in paper:
                        list_of_paper_metadata.append(paper)
        else:
            morepapers = False
            logging.warning("Could not find more papers")
        return list_of_paper_metadata, morepapers

    def _add_cursor_mark_if_exists(self, retireved_metadata_dictionary):
        morepapers = True
        if CURSOR_MARK in retireved_metadata_dictionary[RESPONSE_WRAPPER]:
            cursor_mark = retireved_metadata_dictionary[RESPONSE_WRAPPER][CURSOR_MARK]
        else:
            cursor_mark = None
            morepapers = False
            logging.warning("Could not find more papers")
        return morepapers, cursor_mark

    def build_and_send_query(self, maximum_hits_per_page, cursor_mark, query, synonym):
        """Retrieves metadata from EPMC for given query

        :param maximum_hits_per_page: number of papers to get
        :type maximum_hits_per_page: int
        :param cursor_mark: cursor mark
        :type cursor_mark: string
        :param query:  query
        :type query: string
        :param synonym: whether to get synonyms, defaults to True
        :type synonym: bool
        :return: metadata dictionary
        :rtype: dict
        """
        queryparams = self.buildquery(
            cursor_mark, maximum_hits_per_page, query, synonym=synonym
        )
        try:
            retireved_metadata_dictionary = (
                self.download_tools.gets_result_dict_for_query(
                    queryparams[HEADERS], queryparams[PAYLOAD]
                )
            )
        except:
            retireved_metadata_dictionary = None
        return retireved_metadata_dictionary

    @staticmethod
    def create_parameters_for_paper_download():
        """Creates parameters for paper download

        :return: parameters for paper download tuple
        :rtype: tuple
        """

        list_of_paper_metadata = []
        morepapers = True
        number_of_papers_there = 0
        maximum_hits_per_page = 1000
        return (
            list_of_paper_metadata,
            maximum_hits_per_page,
            morepapers,
            number_of_papers_there,
        )

    def update(self, query_namespace):
        update_path = self.download_tools.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        read_json = self.download_tools.readjsondata(update_path)
        self.run_eupmc_query_and_get_metadata(
            query_namespace["query"],
            update=read_json,
            cutoff_size=query_namespace["limit"],
            getpdf=query_namespace["pdf"],
            makecsv=query_namespace["makecsv"],
            makexml=query_namespace["xml"],
            references=query_namespace["references"],
            makehtml=query_namespace["makehtml"],
            citations=query_namespace["citations"],
            supplementary_files=query_namespace["supp"],
            synonym=query_namespace["synonym"],
            zip_files=query_namespace["zip"],
        )

    def restart(self, query_namespace):
        """Restarts query to add new metadata for existing papers

        :param query_namespace: pygetpaper's name space object
        :type query_namespace: dict
        """
        restart_file_path = self.download_tools.get_metadata_results_file()
        dict_from_previous_run = self.download_tools.readjsondata(restart_file_path)
        os.chdir(os.path.dirname(restart_file_path))
        self.get_supplementary_metadata(
            dict_from_previous_run,
            getpdf=query_namespace["pdf"],
            makecsv=query_namespace["makecsv"],
            makehtml=query_namespace["makehtml"],
            makexml=query_namespace["xml"],
            references=query_namespace["references"],
            citations=query_namespace["citations"],
            supplementary_files=query_namespace["supp"],
            zip_files=query_namespace["zip"],
        )

    def noexecute(self, query_namespace):
        query = query_namespace["query"]
        synonym = query_namespace["synonym"]
        builtqueryparams = self.buildquery("*", 25, query, synonym=synonym)
        result = self.download_tools.gets_result_dict_for_query(
            builtqueryparams[HEADERS], builtqueryparams[PAYLOAD]
        )
        totalhits = result[RESPONSE_WRAPPER][HITCOUNT]
        logging.info("Total number of hits for the query are %s", totalhits)

    def run_eupmc_query_and_get_metadata(
        self,
        query,
        cutoff_size,
        update=None,
        onlymakejson=False,
        getpdf=False,
        makehtml=False,
        makecsv=False,
        makexml=False,
        references=False,
        citations=False,
        supplementary_files=False,
        synonym=True,
        zip_files=False,
    ):
        if update:
            cursor_mark = update[CURSOR_MARK]
        else:
            cursor_mark = "*"
        metadata_dictionary = self.query(
            query, cutoff_size, cursor_mark=cursor_mark, synonym=synonym
        )
        self._make_metadata_json(metadata_dictionary, update=update)
        if not onlymakejson:
            self.get_supplementary_metadata(
                metadata_dictionary,
                getpdf=getpdf,
                makecsv=makecsv,
                makexml=makexml,
                makehtml=makehtml,
                references=references,
                citations=citations,
                supplementary_files=supplementary_files,
                zip_files=zip_files,
            )

    def apipaperdownload(self, query_namespace):
        query = query_namespace["query"]
        cutoff_size = query_namespace["limit"]
        onlymakejson = query_namespace["onlyquery"]
        getpdf = query_namespace["pdf"]
        makecsv = query_namespace["makecsv"]
        makehtml = query_namespace["makehtml"]
        makexml = query_namespace["xml"]
        references = query_namespace["references"]
        citations = query_namespace["citations"]
        supplementary_files = query_namespace["supp"]
        zip_files = query_namespace["zip"]
        synonym = query_namespace["synonym"]
        self.run_eupmc_query_and_get_metadata(
            query,
            cutoff_size,
            onlymakejson=onlymakejson,
            getpdf=getpdf,
            makehtml=makehtml,
            makecsv=makecsv,
            makexml=makexml,
            references=references,
            citations=citations,
            supplementary_files=supplementary_files,
            synonym=synonym,
            zip_files=zip_files,
        )

    @staticmethod
    def buildquery(
        cursormark,
        page_size,
        query,
        synonym=True,
    ):
        """Builds query parameters"""
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        payload = {
            "query": query,
            "resultType": "core",
            "cursorMark": cursormark,
            "pageSize": page_size,
            "synonym": synonym,
            "format": "xml",
            "sort_PMCID": "y",
        }
        logging.debug("*/submitting RESTful query (I)*/")
        return {"headers": headers, "payload": payload}

    def make_html_from_dict(self, dict_to_write_html_from, url, identifier_for_paper):
        """Makes html from dict

        :param dict_to_write_html_from: dict to write html from
        :type dict_to_write_html_from: dict
        :param url: url to write html to
        :type url: str
        """
        df = pd.Series(dict_to_write_html_from).to_frame(dict_to_write_html_from[PMCID])
        self.download_tools.make_html_from_dataframe(df, url)

    def get_urls_to_write_to(self, identifier_for_paper):
        """Gets urls to write the metadata to

        :param identifier_for_paper: identifier for paper
        :type identifier_for_paper: str
        :return: urls to write the metadata to
        :rtype: tuple
        """
        destination_url = os.path.join(
            str(os.getcwd()), identifier_for_paper, FULLTEXT_XML
        )
        directory_url = os.path.join(str(os.getcwd()), identifier_for_paper)
        jsonurl = os.path.join(str(os.getcwd()), identifier_for_paper, RESULT_JSON)
        referenceurl = os.path.join(
            str(os.getcwd()), identifier_for_paper, REFERENCE_XML
        )
        citationurl = os.path.join(str(os.getcwd()), identifier_for_paper, CITATION_XML)
        supplementaryfilesurl = os.path.join(
            str(os.getcwd()), identifier_for_paper, SUPPLEMENTARY_FILES
        )
        zipurl = os.path.join(str(os.getcwd()), identifier_for_paper, FTPFILES)
        htmlurl = os.path.join(str(os.getcwd()), identifier_for_paper, EUPMC_HTML)
        return (
            citationurl,
            destination_url,
            directory_url,
            jsonurl,
            referenceurl,
            supplementaryfilesurl,
            htmlurl,
            zipurl,
        )

    def get_supplementary_metadata(
        self,
        metadata_dictionary_with_all_papers,
        getpdf=False,
        makecsv=False,
        makehtml=False,
        makexml=False,
        references=False,
        citations=False,
        supplementary_files=False,
        zip_files=False,
    ):
        """Gets supplementary metadata

        :param metadata_dictionary_with_all_papers: metadata dictionary
        :type metadata_dictionary_with_all_papers: dict
        :param getpdf: whether to get pdfs
        :type getpdf: bool, optional
        :param makecsv:  whether to create csv output
        :type makecsv: bool, optional
        :param makehtml: whether to create html output
        :type makehtml: bool, optional
        :param makexml: whether to download xml fulltext
        :type makexml: bool, optional
        :param references: whether to download references
        :type references: bool, optional
        :param citations: whether to download citations
        :type citations: bool, optional
        :param supplementary_files: whether to download supplementary_files
        :type supplementary_files: bool, optional
        :param zip_files: whether to download zip_files from the ftp endpoint
        :type zip_files: bool, optional
        """
        html_url = os.path.join(str(os.getcwd()), EUPMC_HTML)
        resultant_dict_for_csv = (
            self.download_tools.removing_added_attributes_from_dictionary(
                metadata_dictionary_with_all_papers["papers"]
            )
        )
        df = pd.DataFrame.from_dict(
            resultant_dict_for_csv,
        )
        df_transposed = df.T
        if makecsv:
            self.download_tools.write_or_append_to_csv(df_transposed)
        if makehtml:
            self.download_tools.make_html_from_dataframe(df, html_url)
        if makexml:
            self.download_tools._log_making_xml()
        paper_number = 0
        dict_of_papers = metadata_dictionary_with_all_papers["papers"]
        for paper in tqdm(dict_of_papers):
            start = time.time()
            paper_number += 1
            identifier_for_paper = dict_of_papers[paper][PMCID]
            tree = self.download_tools.get_request_endpoint_for_xml(
                identifier_for_paper
            )
            (
                citationurl,
                destination_url,
                directory_url,
                jsonurl,
                referenceurl,
                supplementaryfilesurl,
                htmlurl,
                zipurl,
            ) = self.get_urls_to_write_to(identifier_for_paper)
            metadata_dictionary = dict_of_papers[paper]
            self._make_references(references, identifier_for_paper, referenceurl)
            self._make_citations(citations, identifier_for_paper, citationurl)
            self._make_supplementary_files(
                supplementary_files, identifier_for_paper, supplementaryfilesurl
            )
            self._make_zip_files(zip_files, identifier_for_paper, zipurl)
            if not os.path.isdir(directory_url):
                os.makedirs(directory_url)
            (
                condition_to_down,
                condition_to_download_csv,
                condition_to_download_json,
                condition_to_download_pdf,
                condition_to_html,
            ) = self.download_tools._conditions_to_download(metadata_dictionary)
            self._make_xml(
                makexml, tree, destination_url, metadata_dictionary, condition_to_down
            )
            self._make_pdf(
                getpdf,
                identifier_for_paper,
                metadata_dictionary,
                condition_to_download_pdf,
            )
            dict_to_write = self.download_tools._eupmc_clean_dict_for_csv(
                metadata_dictionary
            )
            self._make_json(
                jsonurl, metadata_dictionary, condition_to_download_json, dict_to_write
            )
            self._make_csv(
                makecsv,
                identifier_for_paper,
                metadata_dictionary,
                condition_to_download_csv,
                dict_to_write,
            )
            self._make_html(
                makehtml,
                identifier_for_paper,
                htmlurl,
                metadata_dictionary,
                condition_to_html,
                dict_to_write,
            )
            self.download_tools.dumps_json_to_given_path(
                os.path.join(str(os.getcwd()), RESULTS_JSON),
                metadata_dictionary_with_all_papers,
            )
            stop = time.time()
            logging.debug("Time elapsed: %s", stop - start)
            logging.debug("*/Updating the json*/\n")

    def _make_csv(
        self,
        makecsv,
        identifier_for_paper,
        metadata_dictionary,
        condition_to_download_csv,
        dict_to_write,
    ):
        if condition_to_download_csv:
            if makecsv:
                self._csv_from_dict(dict_to_write, identifier_for_paper)
                metadata_dictionary[CSVMADE] = True

    def _make_json(
        self, jsonurl, metadata_dictionary, condition_to_download_json, dict_to_write
    ):
        if condition_to_download_json:
            self.download_tools.dumps_json_to_given_path(jsonurl, dict_to_write)
            metadata_dictionary[JSON_DOWNLOADED] = True

    def _make_xml(
        self, makexml, tree, destination_url, metadata_dictionary, condition_to_down
    ):
        if condition_to_down:
            if makexml:
                self.download_tools.writexml(destination_url, tree)
                metadata_dictionary[DOWNLOADED] = True

    def _make_zip_files(self, zip_files, identifier_for_paper, zipurl):
        if zip_files:
            self.download_tools.getsupplementaryfiles(
                identifier_for_paper, zipurl, from_ftp_end_point=True
            )

    def _make_html(
        self,
        makehtml,
        identifier_for_paper,
        htmlurl,
        metadata_dictionary,
        condition_to_html,
        dict_to_write,
    ):
        if condition_to_html:
            if makehtml:
                self.make_html_from_dict(dict_to_write, htmlurl, identifier_for_paper)
                logging.debug("Wrote the html file for %s", identifier_for_paper)
                metadata_dictionary[HTML_MADE] = True

    def _make_pdf(
        self,
        getpdf,
        identifier_for_paper,
        metadata_dictionary,
        condition_to_download_pdf,
    ):
        if condition_to_download_pdf:
            if getpdf:
                pdf_destination = os.path.join(
                    str(os.getcwd()), identifier_for_paper, FULLTEXT_PDF
                )
                if "fullTextUrlList" in metadata_dictionary:
                    full_text_list = metadata_dictionary["fullTextUrlList"][
                        "fullTextUrl"
                    ]
                    for paper_links in full_text_list:
                        if (
                            paper_links["availability"] == "Open access"
                            and paper_links["documentStyle"] == "pdf"
                        ):
                            self.download_tools.queries_the_url_and_writes_response_to_destination(
                                paper_links["url"], pdf_destination
                            )
                            metadata_dictionary[PDF_DOWNLOADED] = True
                            logging.info(
                                "Wrote the pdf file for %s", identifier_for_paper
                            )

    def _make_supplementary_files(
        self, supplementary_files, identifier_for_paper, supplementaryfilesurl
    ):
        if supplementary_files:
            self.download_tools.getsupplementaryfiles(
                identifier_for_paper, supplementaryfilesurl
            )

    def _make_citations(self, citations, identifier_for_paper, citationurl):
        if citations:
            self.download_tools.make_citations(
                citations, citationurl, identifier_for_paper
            )
            logging.debug("Made Citations for %s", identifier_for_paper)

    def _make_references(self, references, identifier_for_paper, referenceurl):
        if references:
            self.download_tools.make_references(
                identifier_for_paper, references, referenceurl
            )
            logging.debug("Made references for %s", identifier_for_paper)

    @staticmethod
    def _csv_from_dict(dict_to_write, identifier_for_paper):
        df = pd.Series(dict_to_write).to_frame("Info_By_EuropePMC_Api")
        df.to_csv(os.path.join(str(os.getcwd()), identifier_for_paper, FULLTEXT_CSV))

    def _conditions_to_download(self, metadata_dictionary):
        condition_to_down = metadata_dictionary[DOWNLOADED] is False
        condition_to_download_pdf = metadata_dictionary[PDF_DOWNLOADED] is False
        condition_to_download_json = metadata_dictionary[JSON_DOWNLOADED] is False
        condition_to_download_csv = metadata_dictionary[CSVMADE] is False
        return (
            condition_to_down,
            condition_to_download_csv,
            condition_to_download_json,
            condition_to_download_pdf,
        )

    def _add_fields_to_resultant_dict(
        self, htmlurl, paper, paper_number, pdfurl, dict_for_paper
    ):
        if HTML_LINKS in dict_for_paper:
            dict_for_paper[HTML_LINKS] = htmlurl[0]
        else:
            logging.warning("html url not found for paper %s", paper_number)
        if ABSTRACT in dict_for_paper:
            dict_for_paper[ABSTRACT] = paper[ABSTRACT_TEXT]
        else:
            logging.warning("Abstract not found for paper %s", paper_number)
        if KEYWORDS in dict_for_paper:
            dict_for_paper[KEYWORDS] = paper["keywordList"][KEYWORD]
        else:
            logging.warning("Keywords not found for paper %s", paper_number)
        if PDF_LINKS in dict_for_paper:
            dict_for_paper[PDF_LINKS] = pdfurl[0]
        else:
            logging.warning("pdf url not found for paper %s", paper_number)
        if JOURNAL_TITLE in dict_for_paper:
            dict_for_paper[JOURNAL_TITLE] = paper[JOURNAL_INFO][JOURNAL][TITLE]
        else:
            logging.warning("journalInfo not found for paper %s", paper_number)
        if AUTHOR_LIST in dict_for_paper:
            author_list = []
            for author in paper[AUTHOR_LIST][AUTHOR]:
                author_list.append(author[FULL_NAME])
            dict_for_paper[AUTHOR_INFO] = author_list
        else:
            logging.warning("Author list not found for paper %s", paper_number)
        if TITLE in dict_for_paper:
            dict_for_paper[TITLE] = paper[TITLE]
        else:
            logging.warning("Title not found for paper %s", paper_number)

    def _make_metadata_json(self, resultant_dict, update=False):
        if update:
            resultant_dict["papers"].update(update["papers"])
        directory_url = os.path.join(str(os.getcwd()))
        jsonurl = os.path.join(str(os.getcwd()), RESULTS_JSON)
        self.download_tools.check_or_make_directory(directory_url)
        self.download_tools.dumps_json_to_given_path(jsonurl, resultant_dict)
        return resultant_dict

    def _make_dictionary_from_list_of_papers(self, list_of_paper_metadata):
        resultant_dict = {}
        for paper_number, paper in tqdm(enumerate(list_of_paper_metadata)):
            paper_number += 1
            identifier_for_paper = paper[PMCID]
            resultant_dict = self.download_tools._make_initial_columns_for_paper_dict(
                identifier_for_paper, resultant_dict
            )
            resultant_dict[identifier_for_paper].update(paper)
        return resultant_dict
