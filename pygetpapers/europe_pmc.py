import json
import logging
import os
import time

import pandas as pd
from tqdm import tqdm

from pygetpapers.download_tools import DownloadTools
from pygetpapers.pgexceptions import PygetpapersError

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

class EuropePmc:
    """ """

    def __init__(self):
        """[summary]"""
        self.download_tools = DownloadTools(EUROPEPMC)

    def europepmc(self, query, size, synonym=True, **kwargs):
        """[summary]

        :param query: [description]
        :type query: [type]
        :param size: [description]
        :type size: [type]
        :param synonym: [description], defaults to True
        :type synonym: bool, optional
        :return: [description]
        :rtype: [type]
        """
        size = int(size)
        (
            content,
            counter,
            maximum_hits_per_page,
            morepapers,
            next_cursor_mark,
            number_of_papers_there,
        ) = self.create_parameters_for_paper_download()
        while number_of_papers_there <= size and morepapers is True:
            builtquery = self.build_and_send_query(
                maximum_hits_per_page, next_cursor_mark, query, synonym
            )
            if builtquery:
                counter += 1
                totalhits = builtquery[RESPONSE_WRAPPER][HITCOUNT]
                if counter == 1:
                    logging.info("Total Hits are %s", totalhits)
                output_dict = json.loads(json.dumps(builtquery))
                try:
                    number_of_papers_there = self.create_final_paper_list(
                        content, kwargs, number_of_papers_there, output_dict, size
                    )
                except PygetpapersError as exception:
                    logging.debug(exception)
                    morepapers = False
                    logging.warning("Could not find more papers")
                    break
                morepapers = self.add_cursor_mark_if_exists(
                    builtquery, morepapers, next_cursor_mark
                )
        if len(content[0]) > size:
            content[0] = content[0][0:size]
        return content

    def create_final_paper_list(
        self, content, kwargs, number_of_papers_there, output_dict, size
    ):
        """[summary]

        :param content: [description]
        :type content: [type]
        :param kwargs: [description]
        :type kwargs: [type]
        :param number_of_papers_there: [description]
        :type number_of_papers_there: [type]
        :param output_dict: [description]
        :type output_dict: [type]
        :param size: [description]
        :type size: [type]
        :return: [description]
        :rtype: [type]
        """
        check_if_only_result = isinstance(
            output_dict[RESPONSE_WRAPPER][RESULT_LIST][RESULT], dict
        )
        if check_if_only_result:
            paper = output_dict[RESPONSE_WRAPPER][RESULT_LIST][RESULT]
            number_of_papers_there = self.append_paper_to_list(
                content, kwargs, number_of_papers_there, paper, size
            )
        else:
            for paper in output_dict[RESPONSE_WRAPPER][RESULT_LIST][RESULT]:
                number_of_papers_there = self.append_paper_to_list(
                    content, kwargs, number_of_papers_there, paper, size
                )
        return number_of_papers_there

    def add_cursor_mark_if_exists(self, builtquery, morepapers, next_cursor_mark):
        """[summary]

        :param builtquery: [description]
        :type builtquery: [type]
        :param morepapers: [description]
        :type morepapers: [type]
        :param next_cursor_mark: [description]
        :type next_cursor_mark: [type]
        :return: [description]
        :rtype: [type]
        """

        if CURSOR_MARK in builtquery[RESPONSE_WRAPPER]:
            next_cursor_mark.append(
                builtquery[RESPONSE_WRAPPER][CURSOR_MARK])
        else:
            morepapers = False
            logging.warning("Could not find more papers")
        return morepapers

    def build_and_send_query(
        self, maximum_hits_per_page, next_cursor_mark, query, synonym
    ):
        """[summary]

        :param maximum_hits_per_page: [description]
        :type maximum_hits_per_page: [type]
        :param next_cursor_mark: [description]
        :type next_cursor_mark: [type]
        :param query: [description]
        :type query: [type]
        :param synonym: [description]
        :type synonym: [type]
        :return: [description]
        :rtype: [type]
        """
        
        queryparams = self.download_tools.buildquery(
            next_cursor_mark[-1], maximum_hits_per_page, query, synonym=synonym
        )
        builtquery = self.download_tools.postquery(
            queryparams[HEADERS], queryparams[PAYLOAD]
        )
        return builtquery

    @staticmethod
    def create_parameters_for_paper_download():
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        
        content = [[]]
        next_cursor_mark = [
            "*",
        ]
        morepapers = True
        number_of_papers_there = 0
        maximum_hits_per_page = 1000
        counter = 0
        return (
            content,
            counter,
            maximum_hits_per_page,
            morepapers,
            next_cursor_mark,
            number_of_papers_there,
        )

    def append_paper_to_list(self, content, kwargs, number_of_papers_there, paper, size):
        """[summary]

        :param content: [description]
        :type content: [type]
        :param kwargs: [description]
        :type kwargs: [type]
        :param number_of_papers_there: [description]
        :type number_of_papers_there: [type]
        :param paper: [description]
        :type paper: [type]
        :param size: [description]
        :type size: [type]
        :return: [description]
        :rtype: [type]
        """
        if UPDATE in kwargs:
            if PMCID in paper and paper[PMCID] not in kwargs[UPDATE]:
                if number_of_papers_there <= size:
                    content[0].append(paper)
                    number_of_papers_there += 1
        else:
            if PMCID in paper:
                if number_of_papers_there <= size:
                    content[0].append(paper)
                    number_of_papers_there += 1
            else:
                pass
        return number_of_papers_there

    def update(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        update_path = self.download_tools.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        read_json = self.download_tools.readjsondata(update_path)
        os.chdir(os.path.dirname(update_path))
        self.updatecorpus(
            args.query,
            read_json,
            args.limit,
            getpdf=args.pdf,
            makecsv=args.makecsv,
            makexml=args.xml,
            references=args.references,
            makehtml=args.makehtml,
            citations=args.citations,
            supplementary_files=args.supp,
            synonym=args.synonym,
            zip_files=args.zip,
        )

    def restart(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        restart_file_path = self.download_tools.get_metadata_results_file()
        read_json = self.download_tools.readjsondata(restart_file_path)
        os.chdir(os.path.dirname(restart_file_path))
        self.makexmlfiles(
            read_json,
            getpdf=args.pdf,
            makecsv=args.makecsv,
            makehtml=args.makehtml,
            makexml=args.xml,
            references=args.references,
            citations=args.citations,
            supplementary_files=args.supp,
            zip_files=args.zip,
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        synonym = args.synonym
        builtqueryparams = self.download_tools.buildquery(
            "*", 25, query, synonym=synonym
        )
        result = self.download_tools.postquery(
            builtqueryparams[HEADERS], builtqueryparams[PAYLOAD]
        )
        totalhits = result[RESPONSE_WRAPPER][HITCOUNT]
        logging.info("Total number of hits for the query are %s", totalhits)

    def updatecorpus(
        self,
        query,
        original_json,
        size,
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
        """[summary]

        :param query: [description]
        :type query: [type]
        :param original_json: [description]
        :type original_json: [type]
        :param size: [description]
        :type size: [type]
        :param onlymakejson: [description], defaults to False
        :type onlymakejson: bool, optional
        :param getpdf: [description], defaults to False
        :type getpdf: bool, optional
        :param makehtml: [description], defaults to False
        :type makehtml: bool, optional
        :param makecsv: [description], defaults to False
        :type makecsv: bool, optional
        :param makexml: [description], defaults to False
        :type makexml: bool, optional
        :param references: [description], defaults to False
        :type references: bool, optional
        :param citations: [description], defaults to False
        :type citations: bool, optional
        :param supplementary_files: [description], defaults to False
        :type supplementary_files: bool, optional
        :param synonym: [description], defaults to True
        :type synonym: bool, optional
        :param zip_files: [description], defaults to False
        :type zip_files: bool, optional
        """
        query_result = self.europepmc(
            query, size, update=original_json, synonym=synonym
        )
        is_search_successful = self.makecsv(
            query_result, makecsv=makecsv, makehtml=makehtml, update=original_json
        )
        if not onlymakejson and is_search_successful is not False:
            read_json = self.download_tools.readjsondata(
                os.path.join(str(os.getcwd()), RESULTS_JSON)
            )
            self.makexmlfiles(
                read_json,
                getpdf=getpdf,
                makecsv=makecsv,
                makexml=makexml,
                makehtml=makehtml,
                references=references,
                citations=citations,
                supplementary_files=supplementary_files,
                zip_files=zip_files,
            )

    def apipaperdownload(
        self, args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        size = args.limit
        onlymakejson = args.onlyquery
        getpdf = args.pdf
        makecsv = args.makecsv
        makehtml = args.makehtml
        makexml = args.xml
        references = args.references
        citations = args.citations
        supplementary_files = args.supp
        zip_files = args.zip
        synonym = args.synonym
        query_result = self.europepmc(query, size, synonym=synonym)
        is_search_successful = self.makecsv(
            query_result, makecsv=makecsv, makehtml=makehtml
        )

        if not onlymakejson and is_search_successful:
            read_json = self.download_tools.readjsondata(
                os.path.join(str(os.getcwd()), RESULTS_JSON)
            )
            self.makexmlfiles(
                read_json,
                getpdf=getpdf,
                makecsv=makecsv,
                makexml=makexml,
                makehtml=makehtml,
                references=references,
                citations=citations,
                supplementary_files=supplementary_files,
                zip_files=zip_files,
            )

    def get_urls_to_write_to(self, pmcid):
        """[summary]

        :param pmcid: [description]
        :type pmcid: [type]
        :return: [description]
        :rtype: [type]
        """
        destination_url = os.path.join(
            str(os.getcwd()), pmcid, FULLTEXT_XML)
        directory_url = os.path.join(str(os.getcwd()), pmcid)
        jsonurl = os.path.join(str(os.getcwd()), pmcid, RESULT_JSON)
        referenceurl = os.path.join(
            str(os.getcwd()), pmcid, REFERENCE_XML)
        citationurl = os.path.join(str(os.getcwd()), pmcid, CITATION_XML)
        supplementaryfilesurl = os.path.join(
            str(os.getcwd()), pmcid, SUPPLEMENTARY_FILES
        )
        zipurl = os.path.join(str(os.getcwd()), pmcid, FTPFILES)
        htmlurl = os.path.join(str(os.getcwd()), pmcid, EUPMC_HTML)
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

    def makexmlfiles(
        self,
        final_xml_dict,
        getpdf=False,
        makecsv=False,
        makehtml=False,
        makexml=False,
        references=False,
        citations=False,
        supplementary_files=False,
        zip_files=False,
    ):
        """[summary]

        :param final_xml_dict: [description]
        :type final_xml_dict: [type]
        :param getpdf: [description], defaults to False
        :type getpdf: bool, optional
        :param makecsv: [description], defaults to False
        :type makecsv: bool, optional
        :param makehtml: [description], defaults to False
        :type makehtml: bool, optional
        :param makexml: [description], defaults to False
        :type makexml: bool, optional
        :param references: [description], defaults to False
        :type references: bool, optional
        :param citations: [description], defaults to False
        :type citations: bool, optional
        :param supplementary_files: [description], defaults to False
        :type supplementary_files: bool, optional
        :param zip_files: [description], defaults to False
        :type zip_files: bool, optional
        """
        if makexml:
            self.download_tools.log_making_xml()
        paper_number = 0
        for paper in tqdm(final_xml_dict):
            start = time.time()
            paper_number += 1
            pmcid = paper
            tree = self.download_tools.getxml(pmcid)
            (
                citationurl,
                destination_url,
                directory_url,
                jsonurl,
                referenceurl,
                supplementaryfilesurl,
                htmlurl,
                zipurl,
            ) = self.get_urls_to_write_to(pmcid)
            paperdict = final_xml_dict[paper]
            paperid = paperdict[ID]
            if references:
                self.download_tools.make_references(
                    directory_url, paperid, references, referenceurl
                )
                logging.debug("Made references for %s", pmcid)
            if citations:
                self.download_tools.make_citations(
                    citations, citationurl, directory_url, paperid
                )
                logging.debug("Made Citations for %s", pmcid)
            if supplementary_files:
                self.download_tools.getsupplementaryfiles(
                    pmcid, directory_url, supplementaryfilesurl
                )
            if zip_files:
                self.download_tools.getsupplementaryfiles(
                    pmcid, directory_url, zipurl, from_ftp_end_point=True
                )
            if not os.path.isdir(directory_url):
                os.makedirs(directory_url)
            (
                condition_to_down,
                condition_to_download_csv,
                condition_to_download_json,
                condition_to_download_pdf,
                condition_to_html,
            ) = self.download_tools.conditions_to_download(paperdict)
            if condition_to_down:
                if makexml:
                    self.download_tools.writexml(
                        directory_url, destination_url, tree)
                    paperdict[DOWNLOADED] = True
            if condition_to_download_pdf:
                if getpdf:
                    pdf_destination = os.path.join(
                        str(os.getcwd()), pmcid, FULLTEXT_PDF
                    )
                    if "fullTextUrlList" in paperdict:
                        full_text_list = paperdict["fullTextUrlList"]["fullTextUrl"]
                        for paper_links in full_text_list:
                            if (paper_links["availability"] == "Open access" and paper_links["documentStyle"] == "pdf"):
                                self.download_tools.write_content_to_destination(
                                    paper_links["url"], pdf_destination
                                )
                                paperdict[PDF_DOWNLOADED] = True
                                logging.info("Wrote the pdf file for %s", pmcid)
            dict_to_write = self.download_tools.clean_dict_for_csv(paperdict)
            if condition_to_download_json:
                self.download_tools.makejson(jsonurl, dict_to_write)
                paperdict[JSON_DOWNLOADED] = True
            if condition_to_download_csv:
                if makecsv:
                    self.make_csv(dict_to_write, pmcid)
                    paperdict[CSVMADE] = True
            if condition_to_html:
                if makehtml:
                    self.download_tools.make_html_from_dict(
                        dict_to_write, htmlurl)
                    logging.debug("Wrote the html file for %s", pmcid)
                    paperdict[HTML_MADE] = True
            self.download_tools.makejson(
                os.path.join(str(os.getcwd()),
                             RESULTS_JSON), final_xml_dict
            )
            stop = time.time()
            logging.debug("Time elapsed: %s", stop - start)
            logging.debug("*/Updating the json*/\n")

    @staticmethod
    def make_csv(dict_to_write, pmcid):
        """[summary]

        :param dict_to_write: [description]
        :type dict_to_write: [type]
        :param pmcid: [description]
        :type pmcid: [type]
        """
        df = pd.Series(dict_to_write).to_frame("Info_By_EuropePMC_Api")
        df.to_csv(os.path.join(str(os.getcwd()), pmcid, FULLTEXT_CSV))

    def conditions_to_download(self, paperdict):
        """[summary]

        :param paperdict: [description]
        :type paperdict: [type]
        :return: [description]
        :rtype: [type]
        """
        condition_to_down = paperdict[DOWNLOADED] is False
        condition_to_download_pdf = paperdict[PDF_DOWNLOADED] is False
        condition_to_download_json = paperdict[JSON_DOWNLOADED] is False
        condition_to_download_csv = paperdict[CSVMADE] is False
        return (
            condition_to_down,
            condition_to_download_csv,
            condition_to_download_json,
            condition_to_download_pdf,
        )

    def add_fields_to_resultant_dict(
        self, htmlurl, paper, paper_number, pdfurl, dict_for_paper
    ):
        """[summary]

        :param htmlurl: [description]
        :type htmlurl: [type]
        :param paper: [description]
        :type paper: [type]
        :param paper_number: [description]
        :type paper_number: [type]
        :param pdfurl: [description]
        :type pdfurl: [type]
        :param dict_for_paper: [description]
        :type dict_for_paper: [type]
        """
        if HTML_LINKS in dict_for_paper:
            dict_for_paper[HTML_LINKS] = htmlurl[0]
        else :
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
            dict_for_paper[JOURNAL_TITLE] = paper[JOURNAL_INFO][JOURNAL][
                TITLE
            ]
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

    def write_meta_data_for_paper(self, paper, paper_number, resultant_dict):
        """[summary]

        :param paper: [description]
        :type paper: [type]
        :param paper_number: [description]
        :type paper_number: [type]
        :param resultant_dict: [description]
        :type resultant_dict: [type]
        :return: [description]
        :rtype: [type]
        """
        logging.debug("Reading Query Result for paper %s", paper_number)
        pdfurl = []
        htmlurl = []
        for x in paper[FULL_TEST_URL_LIST][FULL_TEXT_URL]:
            if x[DOCUMENTSTYLE] == PDF and x[AVAILABILITY] == OPENACCESS:
                pdfurl.append(x[URL])

            if x[DOCUMENTSTYLE] == HTML and x[AVAILABILITY] == OPENACCESS:
                htmlurl.append(x[URL])
        paperpmcid = paper[PMCID]
        resultant_dict = self.download_tools.make_initial_columns_for_paper_dict(
            paperpmcid, resultant_dict
        )
        resultant_dict[paperpmcid].update(paper)
        return htmlurl, paperpmcid, pdfurl, resultant_dict

    def makecsv(self, searchvariable, makecsv=False, makehtml=False, update=False):
        """[summary]

        :param searchvariable: [description]
        :type searchvariable: [type]
        :param makecsv: [description], defaults to False
        :type makecsv: bool, optional
        :param makehtml: [description], defaults to False
        :type makehtml: bool, optional
        :param update: [description], defaults to False
        :type update: bool, optional
        :return: [description]
        :rtype: [type]
        """
        resultant_dict = {}
        if searchvariable:
            for paper_number, papers in tqdm(enumerate(searchvariable)):
                output_dict = json.loads(json.dumps(papers))
                for paper in output_dict:
                    if PMCID in paper:
                        paper_number += 1
                        (
                            html_url,
                            paperpmcid,
                            pdfurl,
                            resultant_dict,
                        ) = self.write_meta_data_for_paper(
                            paper, paper_number, resultant_dict
                        )
                        
                        logging.debug(
                            "Wrote Meta Data to a dictionary that will be written to "
                            "all the chosen metadata file formats for paper %s",
                            paperpmcid,
                        )

            if update:
                resultant_dict.update(update)
            directory_url = os.path.join(str(os.getcwd()))
            jsonurl = os.path.join(str(os.getcwd()),  RESULTS_JSON)
            html_url = os.path.join(str(os.getcwd()), EUPMC_HTML)
            self.download_tools.check_or_make_directory(directory_url)
            self.download_tools.makejson(jsonurl, resultant_dict)
            resultant_dict_for_csv = self.download_tools.make_dict_for_csv(
                resultant_dict
            )
            df = pd.DataFrame.from_dict(
                resultant_dict_for_csv,
            )
            df_transposed = df.T
            if makecsv:
                self.download_tools.write_or_append_to_csv(df_transposed)
            if makehtml:
                self.download_tools.make_html_from_dataframe(df, html_url)
            return searchvariable
        else:
            logging.warning("API gave empty result")
            return False
