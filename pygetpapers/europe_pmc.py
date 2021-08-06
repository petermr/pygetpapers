import time
import json
import logging
import os
import pandas as pd
from tqdm import tqdm
from functools import partialmethod

from pygetpapers.download_tools import DownloadTools


class EuropePmc:
    """ """

    def __init__(self):
        """[summary]"""
        self.logging_url = os.path.join(str(os.getcwd()), "*", "fulltext.xml")
        self.eupmc_json = os.path.join(str(os.getcwd()), "eupmc_results.json")
        self.eupmc_csv_url = os.path.join(str(os.getcwd()), "europe_pmc.csv")
        self.title = "title"
        self.author_info = "authorinfo"
        self.journal_title = "journaltitle"
        self.pdf_links = "pdflinks"
        self.html_links = "htmllinks"
        self.pmcid = "pmcid"
        self.response_wrapper = "responseWrapper"
        self.cursor_mark = "nextCursorMark"
        self.directory_url = os.path.join(str(os.getcwd()))
        self.download_tools = DownloadTools("europepmc")

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
            counter += 1
            builtquery = self.build_and_send_query(
                maximum_hits_per_page, next_cursor_mark, query, synonym
            )
            totalhits = builtquery["responseWrapper"]["hitCount"]
            if counter == 1:
                logging.info("Total Hits are %s", totalhits)
            output_dict = json.loads(json.dumps(builtquery))
            try:
                number_of_papers_there = self.create_final_paper_list(
                    content, kwargs, number_of_papers_there, output_dict, size
                )
            except Exception as exception:
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
            output_dict["responseWrapper"]["resultList"]["result"], dict
        )
        if check_if_only_result:
            paper = output_dict["responseWrapper"]["resultList"]["result"]
            number_of_papers_there = self.append_paper_to_list(
                content, kwargs, number_of_papers_there, paper, size
            )
        else:
            for paper in output_dict["responseWrapper"]["resultList"]["result"]:
                number_of_papers_there = self.append_paper_to_list(
                    content, kwargs, number_of_papers_there, paper, size
                )
        return number_of_papers_there

    @staticmethod
    def add_cursor_mark_if_exists(builtquery, morepapers, next_cursor_mark):
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

        if "nextCursorMark" in builtquery["responseWrapper"]:
            next_cursor_mark.append(
                builtquery["responseWrapper"]["nextCursorMark"])
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
            queryparams["headers"], queryparams["payload"]
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

    @staticmethod
    def append_paper_to_list(content, kwargs, number_of_papers_there, paper, size):
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
        if "update" in kwargs:
            if "pmcid" in paper and paper["pmcid"] not in kwargs["update"]:
                if number_of_papers_there <= size:
                    content[0].append(paper)
                    number_of_papers_there += 1
        else:
            if "pmcid" in paper:
                if number_of_papers_there <= size:
                    content[0].append(paper)
                    number_of_papers_there += 1
            else:
                pass
        return number_of_papers_there

    def eupmc_update(self, args, update_path):
        """[summary]

        :param args: [description]
        :type args: [type]
        :param update_path: [description]
        :type update_path: [type]
        """
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

    def eupmc_restart(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        read_json = self.download_tools.readjsondata(args.restart)
        os.chdir(os.path.dirname(args.restart))
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

    def eupmc_noexecute(self, query, synonym=True):
        """[summary]

        :param query: [description]
        :type query: [type]
        :param synonym: [description], defaults to True
        :type synonym: bool, optional
        """
        builtqueryparams = self.download_tools.buildquery(
            "*", 25, query, synonym=synonym
        )
        headers = "headers"
        payload = "payload"
        result = self.download_tools.postquery(
            builtqueryparams[headers], builtqueryparams[payload]
        )
        totalhits = result["responseWrapper"]["hitCount"]
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
                os.path.join(str(os.getcwd()), "eupmc_results.json")
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

    def eupmc_apipaperdownload(
        self,
        query,
        size,
        onlymakejson=False,
        getpdf=False,
        makecsv=False,
        makehtml=False,
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
        :param size: [description]
        :type size: [type]
        :param onlymakejson: [description], defaults to False
        :type onlymakejson: bool, optional
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
        :param synonym: [description], defaults to True
        :type synonym: bool, optional
        :param zip_files: [description], defaults to False
        :type zip_files: bool, optional
        """
        query_result = self.europepmc(query, size, synonym=synonym)
        is_search_successful = self.makecsv(
            query_result, makecsv=makecsv, makehtml=makehtml
        )

        if not onlymakejson and is_search_successful is not False:
            read_json = self.download_tools.readjsondata(
                os.path.join(str(os.getcwd()), "eupmc_results.json")
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

    @staticmethod
    def get_urls_to_write_to(pmcid):
        """[summary]

        :param pmcid: [description]
        :type pmcid: [type]
        :return: [description]
        :rtype: [type]
        """
        destination_url = os.path.join(str(os.getcwd()), pmcid, "fulltext.xml")
        directory_url = os.path.join(str(os.getcwd()), pmcid)
        jsonurl = os.path.join(str(os.getcwd()), pmcid, "eupmc_result.json")
        referenceurl = os.path.join(str(os.getcwd()), pmcid, "references.xml")
        citationurl = os.path.join(str(os.getcwd()), pmcid, "citation.xml")
        supplementaryfilesurl = os.path.join(
            str(os.getcwd()), pmcid, "supplementaryfiles"
        )
        zipurl = os.path.join(str(os.getcwd()), pmcid, "ftpfiles")
        htmlurl = os.path.join(str(os.getcwd()), pmcid, "eupmc_result.html")
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
            paperid = paperdict["full"]["id"]
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
                    paperdict["downloaded"] = True
            if condition_to_download_pdf:
                if getpdf:
                    pdf_destination = os.path.join(
                        str(os.getcwd()), pmcid, "fulltext.pdf"
                    )
                    if "pdflinks" in paperdict:
                        if len(paperdict["pdflinks"]) > 0:
                            self.download_tools.write_content_to_destination(
                                paperdict["pdflinks"], pdf_destination
                            )
                            paperdict["pdfdownloaded"] = True
                            logging.debug("Wrote the pdf file for %s", pmcid)
            dict_to_write = self.download_tools.clean_dict_for_csv(paperdict)
            if condition_to_download_json:
                self.download_tools.makejson(jsonurl, dict_to_write)
                paperdict["jsondownloaded"] = True
            if condition_to_download_csv:
                if makecsv:
                    self.make_csv(dict_to_write, pmcid)
                    paperdict["csvmade"] = True
            if condition_to_html:
                if makehtml:
                    self.download_tools.make_html_from_dict(
                        dict_to_write, htmlurl)
                    logging.debug("Wrote the html file for %s", pmcid)
                    paperdict["htmlmade"] = True
            self.download_tools.makejson(
                os.path.join(str(os.getcwd()),
                             "eupmc_results.json"), final_xml_dict
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
        df.to_csv(os.path.join(str(os.getcwd()), pmcid, "fulltext.csv"))

    @staticmethod
    def conditions_to_download(paperdict):
        """[summary]

        :param paperdict: [description]
        :type paperdict: [type]
        :return: [description]
        :rtype: [type]
        """
        condition_to_down = paperdict["downloaded"] is False
        condition_to_download_pdf = paperdict["pdfdownloaded"] is False
        condition_to_download_json = paperdict["jsondownloaded"] is False
        condition_to_download_csv = paperdict["csvmade"] is False
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
        try:
            dict_for_paper[self.html_links] = htmlurl[0]
        except Exception as exception:
            logging.debug(exception)
            logging.warning("html url not found for paper %s", paper_number)
        try:
            dict_for_paper["abstract"] = paper["abstractText"]
        except Exception as exception:
            logging.debug(exception)
            logging.warning("Abstract not found for paper %s", paper_number)

        try:
            dict_for_paper["Keywords"] = paper["keywordList"]["keyword"]
        except Exception as exception:
            logging.debug(exception)
            logging.warning("Keywords not found for paper %s", paper_number)
        try:
            dict_for_paper[self.pdf_links] = pdfurl[0]
        except Exception as exception:
            logging.debug(exception)
            logging.warning("pdf url not found for paper %s", paper_number)
        try:
            dict_for_paper[self.journal_title] = paper["journalInfo"]["journal"][
                self.title
            ]
        except Exception as exception:
            logging.debug(exception)
            logging.warning("journalInfo not found for paper %s", paper_number)
        try:
            author_list = []
            for author in paper["authorList"]["author"]:
                author_list.append(author["fullName"])
            dict_for_paper[self.author_info] = author_list
        except Exception as exception:
            logging.debug(exception)
            logging.warning("Author list not found for paper %s", paper_number)
        try:
            dict_for_paper[self.title] = paper[self.title]
        except Exception as exception:
            logging.debug(exception)
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
        for x in paper["fullTextUrlList"]["fullTextUrl"]:
            if x["documentStyle"] == "pdf" and x["availability"] == "Open access":
                pdfurl.append(x["url"])

            if x["documentStyle"] == "html" and x["availability"] == "Open access":
                htmlurl.append(x["url"])
        paperpmcid = paper["pmcid"]
        resultant_dict = self.download_tools.make_initial_columns_for_paper_dict(
            paperpmcid, resultant_dict
        )
        resultant_dict[paperpmcid]["full"] = paper
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
                    if self.pmcid in paper:
                        paper_number += 1
                        (
                            html_url,
                            paperpmcid,
                            pdfurl,
                            resultant_dict,
                        ) = self.write_meta_data_for_paper(
                            paper, paper_number, resultant_dict
                        )
                        self.add_fields_to_resultant_dict(
                            html_url,
                            paper,
                            paper_number,
                            pdfurl,
                            resultant_dict[paperpmcid],
                        )
                        logging.debug(
                            "Wrote Meta Data to a dictionary that will be written to "
                            "all the chosen metadata file formats for paper %s",
                            paperpmcid,
                        )

            if update:
                resultant_dict.update(update)
            directory_url = os.path.join(str(os.getcwd()))
            jsonurl = os.path.join(str(os.getcwd()), "eupmc_results.json")
            html_url = os.path.join(str(os.getcwd()), "eupmc_results.html")
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
