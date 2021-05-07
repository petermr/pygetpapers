def europepmc(self, query, size, synonym=True, externalfile=True, fulltext=True, **kwargs):
    import requests
    import xmltodict
    import lxml.etree
    import logging
    import lxml
    import os
    import json
    size = int(size)
    content = [[]]
    nextCursorMark = ['*', ]
    morepapers = True
    number_of_papers_there = 0
    condition_to_download_papers = number_of_papers_there <= size and morepapers == True
    while condition_to_download_papers:
        queryparams = self.buildquery(
            nextCursorMark[-1], 1000, query, synonym=synonym)
        builtquery = self.postquery(
            queryparams['headers'], queryparams['payload'])
        if self.CURSOR_MARK in builtquery[self.RESPONSE_WRAPPER]:
            nextCursorMark.append(
                builtquery[self.RESPONSE_WRAPPER][self.CURSOR_MARK])
            totalhits = builtquery[self.RESPONSE_WRAPPER]["hitCount"]
            logging.info(f"Total Hits are {totalhits}")
            output_dict = json.loads(json.dumps(builtquery))
            try:
                for paper in output_dict["responseWrapper"]["resultList"]["result"]:
                    number_of_papers_there = self.handle_update_and_addition_of_paper_to_dict(content, kwargs,
                                                                                              number_of_papers_there, paper, size)
            except:
                morepapers = False
                logging.warning("Could not find more papers")
                break
        else:
            morepapers = False
            logging.warning("Could not find more papers")
    if number_of_papers_there > size:
        content[0] = content[0][0:size]
    return content


def handle_update_and_addition_of_paper_to_dict(self, content, kwargs, number_of_papers_there, paper, size):
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
    return number_of_papers_there

    def makexmlfiles(self, final_xml_dict, getpdf=False, makecsv=False, makexml=False, references=False,
                     citations=False, supplementaryFiles=False):
        """
        Writes the *pdf,*csv,*xml,*references,*citations,*supplementaryFiles for the individual papers

        :param final_xml_dict: Python dictionary containg all the papers

        :param getpdf(bool): whether to make pdfs

        :param makecsv(bool): whether to make csv for the metadata

        :param makexml(bool): whether to make xml file for the paper

        :param references(bool): whether to download references

        :param citations(bool): whether to download citations

        :param supplementaryFiles(bool): whether to download supplementary files

        """
        import logging
        import os
        import time
        import multiprocessing
        number_of_processes = len(final_xml_dict)
        process_xml = multiprocessing.Pool(processes=number_of_processes)
        process_references = multiprocessing.Pool(
            processes=number_of_processes)
        process_citations = multiprocessing.Pool(processes=number_of_processes)
        processes_supp = multiprocessing.Pool(processes=number_of_processes)
        process_pdfs = multiprocessing.Pool(processes=number_of_processes)
        process_csv = multiprocessing.Pool(processes=number_of_processes)
        if makexml:
            super().log_making_xml()
        paper_number = 0
        for paper in final_xml_dict:
            start = time.time()
            paper_number += 1
            pmcid = paper
            tree = self.getxml(pmcid)
            citationurl, destination_url, directory_url, jsonurl, referenceurl, supplementaryfilesurl = self.get_urls_to_write_to(
                pmcid)
            paperdict = final_xml_dict[paper]
            paperid = paperdict["full"]["id"]
            if references:
                process_references.apply_async(self.make_references, (directory_url, paperid,
                                                                      references, referenceurl))
                logging.info(f"Made references for {pmcid}")
            if citations:
                process_citations.apply_async(self.make_citations, (citations, citationurl,
                                                                    directory_url, paperid))
                logging.info(f"Made Citations for {pmcid}")
            if supplementaryFiles:
                processes_supp.apply_async(
                    self.getsupplementaryfiles, (paperid, directory_url, supplementaryfilesurl))
                logging.info(f"Made Supplementary files for {pmcid}")
            if not os.path.isdir(directory_url):
                os.makedirs(directory_url)
            condition_to_down, condition_to_download_csv, condition_to_download_json, condition_to_download_pdf = super().conditions_to_download(
                paperdict)
            if condition_to_down:
                if makexml:
                    process_xml.apply_async(
                        super().writexml, (directory_url, destination_url, tree))
                    logging.info(f"*/Wrote xml for {pmcid}/")
                    paperdict["downloaded"] = True
            if condition_to_download_pdf:
                if getpdf:
                    pdf_destination = os.path.join(
                        str(os.getcwd()), pmcid, "fulltext.pdf")
                    if "pdflinks" in paperdict:
                        if len(paperdict["pdflinks"]) > 0:
                            process_pdfs.apply_async(
                                super().writepdf, (paperdict["pdflinks"], pdf_destination))
                            paperdict["pdfdownloaded"] = True
                            logging.info(f"Wrote the pdf file for {pmcid}")
            dict_to_write = super().clean_dict_for_csv(paperdict)
            if condition_to_download_json:
                super().makejson(jsonurl, dict_to_write)
                paperdict["jsondownloaded"] = True
            if condition_to_download_csv:
                if makecsv:
                    self.make_csv(dict_to_write, pmcid)
                    paperdict["csvmade"] = True
            super().makejson(os.path.join(
                str(os.getcwd()), 'eupmc_results.json'), final_xml_dict)
            stop = time.time()
            logging.debug(f"Time elapsed: {stop - start}")
            logging.debug(f"*/Updating the json*/\n")
        process_xml.close()
        process_xml.join()
        process_references.close()
        process_references.join()
        process_citations.close()
        process_citations.join()
        processes_supp.close()
        processes_supp.join()
        process_pdfs.close()
        process_pdfs.join()
        process_csv.close()
        process_csv.join()
