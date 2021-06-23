from pygetpapers.download_tools import download_tools


class europe_pmc:
    """ """

    def __init__(self):
        import os
        import configparser
        with open(os.path.join(os.path.dirname(__file__), "config.ini")) as f:
            config_file = f.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_string(config_file)
        self.LOGGING_URL = os.path.join(str(os.getcwd()), '*', 'fulltext.xml')
        self.EUPMCJSON = os.path.join(str(os.getcwd()), 'eupmc_results.json')
        self.EUPMCCSVURL = os.path.join(str(os.getcwd()), 'europe_pmc.csv')
        self.TITLE = "title"
        self.AUTHORINFO = "authorinfo"
        self.JOURNALTITLE = "journaltitle"
        self.PDFLINKS = "pdflinks"
        self.HTMLLINKS = "htmllinks"
        self.PMCID = "pmcid"
        self.RESPONSE_WRAPPER = "responseWrapper"
        self.CURSOR_MARK = "nextCursorMark"
        self.directory_url = os.path.join(
            str(os.getcwd()))
        self.download_tools = download_tools("europepmc")

    def europepmc(self, query, size, synonym=True, **kwargs):
        """Makes the query to europepmc rest api then returns a python dictionary containing the research papers.

        :param query: the query passed on to payload
        :param size: total number of papers
        :param synonym: whether synonym should be or not (Default value = True)
        :param kwargs: ensures that the output dict doesnt contain papers already there in update
        :param **kwargs: 
        :returns: Python dictionary containing the research papers.

        """
        import json
        import logging
        size = int(size)
        content, counter, maximum_hits_per_page, morepapers, nextCursorMark, number_of_papers_there = self.create_parameters_for_paper_download()
        while number_of_papers_there <= size and morepapers is True:
            counter += 1
            builtquery = self.build_and_send_query(
                maximum_hits_per_page, nextCursorMark, query, synonym)
            totalhits = builtquery["responseWrapper"]["hitCount"]
            if counter == 1:
                logging.info(f"Total Hits are {totalhits}")
            output_dict = json.loads(json.dumps(builtquery))
            try:
                number_of_papers_there = self.create_final_paper_list(content, kwargs, number_of_papers_there,
                                                                      output_dict, size)
            except:
                morepapers = False
                logging.warning("Could not find more papers")
                break
            morepapers = self.add_cursor_mark_if_exists(
                builtquery, morepapers, nextCursorMark)
        if len(content[0]) > size:
            content[0] = content[0][0:size]
        return content

    def create_final_paper_list(self, content, kwargs, number_of_papers_there, output_dict, size):
        """Checks the number of results and then adds them to the list containing all the papers called content

        :param content: list containing all the papers
        :param kwargs: kwargs of the main function containing whether to update or add papers
        :param number_of_papers_there: total number of papers found till now
        :param output_dict: output directory
        :param size: required number of papers

        """
        check_if_only_result = type(
            output_dict["responseWrapper"]["resultList"]["result"]) == dict
        if check_if_only_result:
            paper = output_dict["responseWrapper"]["resultList"]["result"]
            number_of_papers_there = self.append_paper_to_list(content, kwargs, number_of_papers_there, paper,
                                                               size)
        else:
            for paper in output_dict["responseWrapper"]["resultList"]["result"]:
                number_of_papers_there = self.append_paper_to_list(content, kwargs, number_of_papers_there, paper,
                                                                   size)
        return number_of_papers_there

    def add_cursor_mark_if_exists(self, builtquery, morepapers, nextCursorMark):
        """Adds the cursor mark if it exists in the api result

        :param builtquery: api result dictionary
        :param morepapers: weather to download more papers
        :param nextCursorMark: list containing all cursor marks

        """
        import logging

        if "nextCursorMark" in builtquery["responseWrapper"]:
            nextCursorMark.append(
                builtquery["responseWrapper"]["nextCursorMark"])
        else:
            morepapers = False
            logging.warning("Could not find more papers")
        return morepapers

    def build_and_send_query(self, maximum_hits_per_page, nextCursorMark, query, synonym):
        """

        :param maximum_hits_per_page: param nextCursorMark:
        :param query: param synonym:
        :param nextCursorMark: param synonym:
        :param synonym: 

        """
        queryparams = self.download_tools.buildquery(
            nextCursorMark[-1], maximum_hits_per_page, query, synonym=synonym)
        builtquery = self.download_tools.postquery(
            queryparams['headers'], queryparams['payload'])
        return builtquery

    def create_parameters_for_paper_download(self):
        """ """
        content = [[]]
        nextCursorMark = ['*', ]
        morepapers = True
        number_of_papers_there = 0
        maximum_hits_per_page = 1000
        counter = 0
        return content, counter, maximum_hits_per_page, morepapers, nextCursorMark, number_of_papers_there

    def append_paper_to_list(self, content, kwargs, number_of_papers_there, paper, size):
        """

        :param content: param kwargs:
        :param number_of_papers_there: param paper:
        :param size: param kwargs:
        :param paper: param kwargs:
        :param kwargs: 

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

    def eupmc_update(self, args):
        """

        :param args:

        """
        import os
        read_json = self.download_tools.readjsondata(args.update)
        os.chdir(os.path.dirname(args.update))
        self.updatecorpus(args.query, read_json, args.limit, getpdf=args.pdf,
                          makecsv=args.makecsv, makexml=args.xml, references=args.references, makehtml=args.makehtml,
                          citations=args.citations, supplementaryFiles=args.supp, synonym=args.synonym,
                          zipFiles=args.zip)

    def eupmc_restart(self, args):
        """

        :param args:

        """
        import os
        read_json = self.download_tools.readjsondata(args.restart)
        os.chdir(os.path.dirname(args.restart))
        self.makexmlfiles(read_json, getpdf=args.pdf, makecsv=args.makecsv, makehtml=args.makehtml, makexml=args.xml,
                          references=args.references, citations=args.citations, supplementaryFiles=args.supp,
                          zipFiles=args.zip)

    def eupmc_noexecute(self, query, synonym=True):
        """Tells how many hits found for the query

        :param query: param synonym:
        :param synonym: Default value = True)

        """
        import logging
        builtqueryparams = self.download_tools.buildquery(
            '*', 25, query, synonym=synonym)
        HEADERS = 'headers'
        PAYLOAD = 'payload'
        result = self.download_tools.postquery(
            builtqueryparams[HEADERS], builtqueryparams[PAYLOAD])
        totalhits = result['responseWrapper']['hitCount']
        logging.info(f'Total number of hits for the query are {totalhits}')

    def updatecorpus(self, query, original_json, size, onlymakejson=False, getpdf=False, makehtml=False, makecsv=False, makexml=False,
                     references=False, citations=False, supplementaryFiles=False, synonym=True, zipFiles=False):
        """Updates the corpus with new papers

        :param query: str):  Query to download papers for
        :param original_json: Json of the original corpus in the form of python dictionary
        :param size: int): Number of new papers to download
        :param onlymakejson: Default value = False)
        :param getpdf: Default value = False)
        :param makehtml: Default value = False)
        :param makecsv: Default value = False)
        :param makexml: Default value = False)
        :param references: Default value = False)
        :param citations: Default value = False)
        :param supplementaryFiles: Default value = False)
        :param synonym: Default value = True)
        :param zipFiles: Default value = False)

        """
        import os
        query_result = self.europepmc(
            query, size, update=original_json, synonym=synonym)
        is_search_successful = self.makecsv(query_result, makecsv=makecsv, makehtml=makehtml,
                                            update=original_json)
        if not (onlymakejson) and is_search_successful is not False:
            read_json = self.download_tools.readjsondata(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'))
            self.makexmlfiles(read_json, getpdf=getpdf,
                              makecsv=makecsv, makexml=makexml, makehtml=makehtml, references=references, citations=citations,
                              supplementaryFiles=supplementaryFiles, zipFiles=zipFiles)

    def eupmc_apipaperdownload(self, query, size, onlymakejson=False, getpdf=False, makecsv=False, makehtml=False, makexml=False,
                               references=False, citations=False, supplementaryFiles=False, synonym=True, zipFiles=False):
        """Downloads and writes papers along with the metadata for the given query

        :param query: Query to download papers for
        :param size: Number of papers to be downloaded
        :param onlymakejson: Default value = False)
        :param getpdf: Default value = False)
        :param makecsv: Default value = False)
        :param makehtml: Default value = False)
        :param makexml: Default value = False)
        :param references: Default value = False)
        :param citations: Default value = False)
        :param supplementaryFiles: Default value = False)
        :param synonym: Default value = True)
        :param zipFiles: Default value = False)

        """
        import os
        query_result = self.europepmc(query, size, synonym=synonym)
        is_search_successful = self.makecsv(
            query_result, makecsv=makecsv, makehtml=makehtml)

        if not (onlymakejson) and is_search_successful is not False:
            read_json = self.download_tools.readjsondata(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'))
            self.makexmlfiles(read_json, getpdf=getpdf, makecsv=makecsv, makexml=makexml, makehtml=makehtml,
                              references=references, citations=citations, supplementaryFiles=supplementaryFiles, zipFiles=zipFiles)

    def get_urls_to_write_to(self, pmcid):
        """

        :param pmcid: pmcid to write the urls for
        :returns: tuple containing urls where files for the fulltext will be written

        """
        import os
        destination_url = os.path.join(
            str(os.getcwd()), pmcid, "fulltext.xml")
        directory_url = os.path.join(str(os.getcwd()), pmcid)
        jsonurl = os.path.join(
            str(os.getcwd()), pmcid, "eupmc_result.json")
        referenceurl = os.path.join(
            str(os.getcwd()), pmcid, "references.xml")
        citationurl = os.path.join(
            str(os.getcwd()), pmcid, "citation.xml")
        supplementaryfilesurl = os.path.join(
            str(os.getcwd()), pmcid, "supplementaryfiles")
        zipurl = os.path.join(
            str(os.getcwd()), pmcid, "ftpfiles")
        htmlurl = os.path.join(str(os.getcwd()), pmcid, "eupmc_result.html")
        return citationurl, destination_url, directory_url, jsonurl, referenceurl, supplementaryfilesurl, htmlurl, zipurl

    def makexmlfiles(self, final_xml_dict, getpdf=False, makecsv=False, makehtml=False, makexml=False, references=False,
                     citations=False, supplementaryFiles=False, zipFiles=False):
        """Writes the pdf,csv,xml,references,citations,supplementaryFiles for the individual papers

        :param final_xml_dict: Python dictionary containg all the papers
        :param getpdf: bool): whether to make pdfs (Default value = False)
        :param makecsv: bool): whether to make csv for the metadata (Default value = False)
        :param makexml: bool): whether to make xml file for the paper (Default value = False)
        :param references: bool): whether to download references (Default value = False)
        :param citations: bool): whether to download citations (Default value = False)
        :param supplementaryFiles: bool): whether to download supplementary files (Default value = False)
        :param makehtml: Default value = False)
        :param zipFiles: Default value = False)

        """
        import logging
        import os
        import time
        if makexml:
            self.download_tools.log_making_xml()
        paper_number = 0
        for paper in final_xml_dict:
            start = time.time()
            paper_number += 1
            pmcid = paper
            tree = self.download_tools.getxml(pmcid)
            citationurl, destination_url, directory_url, jsonurl, referenceurl, supplementaryfilesurl, htmlurl, zipurl = self.get_urls_to_write_to(
                pmcid)
            paperdict = final_xml_dict[paper]
            paperid = paperdict["full"]["id"]
            if references:
                self.download_tools.make_references(directory_url, paperid,
                                                    references, referenceurl)
                logging.info(f"Made references for {pmcid}")
            if citations:
                self.download_tools.make_citations(citations, citationurl,
                                                   directory_url, paperid)
                logging.info(f"Made Citations for {pmcid}")
            if supplementaryFiles:
                self.download_tools.getsupplementaryfiles(
                    pmcid, directory_url, supplementaryfilesurl)
            if zipFiles:
                self.download_tools.getsupplementaryfiles(
                    pmcid, directory_url, zipurl, fromFtpEndpoint=True)
            if not os.path.isdir(directory_url):
                os.makedirs(directory_url)
            condition_to_down, condition_to_download_csv, condition_to_download_json, condition_to_download_pdf, condition_to_html = self.download_tools.conditions_to_download(
                paperdict)
            if condition_to_down:
                if makexml:
                    self.download_tools.writexml(
                        directory_url, destination_url, tree)
                    logging.info(f"*/Wrote xml for {pmcid}/")
                    paperdict["downloaded"] = True
            if condition_to_download_pdf:
                if getpdf:
                    pdf_destination = os.path.join(
                        str(os.getcwd()), pmcid, "fulltext.pdf")
                    if "pdflinks" in paperdict:
                        if len(paperdict["pdflinks"]) > 0:
                            self.download_tools.writepdf(
                                paperdict["pdflinks"], pdf_destination)
                            paperdict["pdfdownloaded"] = True
                            logging.info(f"Wrote the pdf file for {pmcid}")
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
                    logging.info(f"Wrote the html file for {pmcid}")
                    paperdict["htmlmade"] = True
            self.download_tools.makejson(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'), final_xml_dict)
            stop = time.time()
            logging.debug(f"Time elapsed: {stop - start}")
            logging.debug(f"*/Updating the json*/\n")

    def make_csv(self, dict_to_write, pmcid):
        """Makes csv file for the dict_to_write (python dictionary for the fulltext).

        :param dict_to_write: Python dictionary to write the csv from
        :param pmcid: pmcid of the paper

        """
        import pandas as pd
        import os
        df = pd.Series(dict_to_write).to_frame(
            'Info_By_EuropePMC_Api')
        df.to_csv(os.path.join(
            str(os.getcwd()), pmcid, "fulltext.csv"))

    def conditions_to_download(self, paperdict):
        """Writes the conditions to download pdf, json and csv

        :param paperdict: dictionary to write rules for

        """
        condition_to_down = paperdict["downloaded"] is False
        condition_to_download_pdf = paperdict["pdfdownloaded"] is False
        condition_to_download_json = paperdict["jsondownloaded"] is False
        condition_to_download_csv = paperdict["csvmade"] is False
        return condition_to_down, condition_to_download_csv, condition_to_download_json, condition_to_download_pdf

    def add_fields_to_resultant_dict(self, htmlurl, paper, paper_number, pdfurl, dict_for_paper):
        """Writes urls to dictionary

        :param htmlurl: list containing html urls for the paper
        :param paper: python dictionary of the paper
        :param paper_number: paper number to log
        :param pdfurl: list containing pdf urls for the paper
        :param dict_for_paper: python dictionary to write the urls to
        :returns: dict_for_paper

        """
        import logging
        try:
            dict_for_paper[self.HTMLLINKS] = htmlurl[0]
        except:
            logging.warning(
                f"html url not found for paper {paper_number}")
        try:
            dict_for_paper["abstract"] = paper["abstractText"]
        except:
            logging.warning(
                f"Abstract not found for paper {paper_number}")

        try:
            dict_for_paper["Keywords"] = paper["keywordList"]["keyword"]
        except:
            logging.warning(
                f"Keywords not found for paper {paper_number}")
        try:
            dict_for_paper[self.PDFLINKS] = pdfurl[0]
        except:
            logging.warning(
                f"pdf url not found for paper {paper_number}")
        try:
            dict_for_paper[self.JOURNALTITLE] = paper["journalInfo"]["journal"][self.TITLE]
        except:
            logging.warning(
                f"journalInfo not found for paper {paper_number}")
        try:
            author_list = []
            for author in paper["authorList"]["author"]:
                author_list.append(author['fullName'])
            dict_for_paper[self.AUTHORINFO
                           ] = author_list
        except:
            logging.warning(
                f"Author list not found for paper {paper_number}")
        try:
            dict_for_paper[self.TITLE] = paper[self.TITLE]
        except:
            logging.warning(
                f"Title not found for paper {paper_number}")

    def write_meta_data_for_paper(self, paper, paper_number, resultant_dict):
        """Adds pdf and html url as well as makes the paper key in resultant_dict

        :param paper: python dictionary for the paper
        :param paper_number: paper number to log
        :param resultant_dict: dictionary to add paper as well as pdf,html url to
        :returns: htmlurl, paperpmcid, pdfurl, resultant_dict)

        """
        import logging
        logging.debug(
            f"Reading Query Result for paper {paper_number}")
        pdfurl = []
        htmlurl = []
        for x in paper["fullTextUrlList"]["fullTextUrl"]:
            if x["documentStyle"] == "pdf" and x["availability"] == "Open access":
                pdfurl.append(x["url"])

            if x["documentStyle"] == "html" and x["availability"] == "Open access":
                htmlurl.append(x["url"])
        paperpmcid = paper["pmcid"]
        resultant_dict = self.make_initial_columns_for_paper_dict(
            paperpmcid, resultant_dict)
        resultant_dict[paperpmcid]["full"] = paper
        return htmlurl, paperpmcid, pdfurl, resultant_dict

    def makecsv(self, searchvariable, makecsv=False, makehtml=False, update=False):
        """Writes the json and csv for searchvaraible dict

        :param searchvariable: dict): Python dictionary which contains all the research papers (given by europe_pmc.europepmc))
        :param makecsv: bool): whether to make csv files (Default value = False)
        :param update: dict): if provided, will add the research papers to the searchvariable dict (Default value = False)
        :param makehtml: Default value = False)
        :returns: searchvariable

        """
        import pandas as pd
        import json
        import os
        import logging
        resultant_dict = {}
        if searchvariable:
            for paper_number, papers in enumerate(searchvariable):
                output_dict = json.loads(json.dumps(papers))
                for paper in output_dict:
                    if self.PMCID in paper:
                        paper_number += 1
                        htmlurl, paperpmcid, pdfurl, resultant_dict = self.write_meta_data_for_paper(
                            paper, paper_number, resultant_dict)
                        self.add_fields_to_resultant_dict(
                            htmlurl, paper, paper_number, pdfurl, resultant_dict[paperpmcid])
                        logging.debug(
                            f'Wrote Meta Data to a dictionary that will be written to all the chosen metadata file formats for paper {paperpmcid}')
            if update:
                resultant_dict.update(update)
            directory_url = os.path.join(
                str(os.getcwd()))
            jsonurl = os.path.join(
                str(os.getcwd()), 'eupmc_results.json')
            htmlurl = os.path.join(
                str(os.getcwd()), 'eupmc_results.html')
            self.download_tools.check_or_make_directory(directory_url)
            self.download_tools.makejson(jsonurl, resultant_dict)
            resultant_dict_for_csv = self.download_tools.make_dict_for_csv(
                resultant_dict)
            df = pd.DataFrame.from_dict(resultant_dict_for_csv, )
            df_transposed = df.T
            if makecsv:
                self.download_tools.write_or_append_to_csv(df_transposed)
            if makehtml:
                self.download_tools.make_html_from_dataframe(df, htmlurl)
            return searchvariable
        else:
            logging.warning("API gave empty result")
            return False

    def make_initial_columns_for_paper_dict(self, pmcid, resultant_dict):
        """

        :param pmcid: pmcid of the paper for which fields will be created
        :param resultant_dict: dict in which the fields will be created
        :returns: dict with the initial fields created for pmcid

        """
        resultant_dict[pmcid] = {}
        resultant_dict[pmcid]["downloaded"] = False
        resultant_dict[pmcid]["pdfdownloaded"] = False
        resultant_dict[pmcid]["jsondownloaded"] = False
        resultant_dict[pmcid]["csvmade"] = False
        resultant_dict[pmcid]["htmlmade"] = False
        return resultant_dict
    # this is the function that will the the result from search and will download and save the files.
