from pygetpapers.download_tools import download_tools


class arxiv:
    """ """

    def __init__(self):
        self.download_tools = download_tools("arxiv")

    def arxiv(self, query, size, getpdf=False,
              makecsv=False, makexml=False, makehtml=False):
        """

        :param query: param size:
        :param getpdf: Default value = False)
        :param makecsv: Default value = False)
        :param makexml: Default value = False)
        :param makehtml: Default value = False)
        :param size: 

        """
        import arxiv
        import logging
        import pandas as pd
        logging.info("Making request to Arxiv through pygetpapers")
        search = arxiv.Search(
            query=query,
            max_results=size,
            sort_by=arxiv.SortCriterion.Relevance
        )

        return_dict = {}
        logging.info("Got request result from Arxiv through pygetpapers")

        self.make_dict_from_arxiv_output(return_dict, search)

        df = pd.DataFrame.from_dict(return_dict)
        self.make_json_from_arxiv_dict(return_dict)

        if getpdf:
            self.download_pdf(return_dict)
        if makecsv:
            self.make_csv_for_arxiv_dict(df, return_dict)
        if makehtml:
            self.make_html_for_arxiv_dict(df, return_dict)
        if makexml:
            self.make_xml_for_arxiv_dict(return_dict)

        return return_dict

    def make_xml_for_arxiv_dict(self, return_dict):
        """

        :param return_dict: 

        """
        import os
        from dict2xml import dict2xml
        import logging
        total_xml = dict2xml(return_dict,
                             wrap='root', indent="   ")
        logging.info(f'Making xml files for metadata at {os.getcwd()}')
        xmlurl = os.path.join(os.getcwd(), 'arxiv_results.xml')
        with open(xmlurl, 'w') as f:
            f.write(total_xml)
        paper = 0
        for result in return_dict:
            paper += 1
            total_xml_of_paper = dict2xml(
                return_dict[result], wrap='root', indent="   ")
            xmlurl_of_paper = os.path.join(
                os.getcwd(), result, 'arxiv_result.xml')
            with open(xmlurl_of_paper, 'w') as f:
                f.write(total_xml_of_paper)
            logging.info(f'Wrote xml files for paper {paper}')

    def make_html_for_arxiv_dict(self, df, return_dict):
        """

        :param df: param return_dict:
        :param return_dict: 

        """
        import os
        import logging
        logging.info(f'Making html files for metadata at {os.getcwd()}')
        paper = 0
        htmlurl = os.path.join(os.getcwd(), 'arxiv_results.html')
        self.download_tools.make_html_from_dataframe(df, htmlurl)
        for result in return_dict:
            paper += 1
            url = os.path.join(os.getcwd(), result, 'arxiv_result.html')
            df_for_paper = self.make_dataframe_for_paper_dict(
                result, return_dict)
            self.download_tools.make_html_from_dataframe(df_for_paper, url)
            logging.info(f'Wrote xml files for paper {paper}')

    def make_dataframe_for_paper_dict(self, result, return_dict):
        """

        :param result: param return_dict:
        :param return_dict: 

        """
        import pandas as pd
        dict_for_df = {k: [v]
                       for k, v in return_dict[result].items()}
        df_for_paper = pd.DataFrame(dict_for_df)
        return df_for_paper

    def make_csv_for_arxiv_dict(self, df, return_dict):
        """

        :param df: param return_dict:
        :param return_dict: 

        """
        import os
        import logging
        logging.info(f'Making csv files for metadata at {os.getcwd()}')
        paper = 0
        self.download_tools.write_or_append_to_csv(df, 'arxiv_results.csv')
        for result in return_dict:
            paper += 1
            url = os.path.join(os.getcwd(), result, 'arxiv_result.csv')
            df_for_paper = self.make_dataframe_for_paper_dict(
                result, return_dict)
            self.download_tools.write_or_append_to_csv(
                df_for_paper, url)
            logging.info(f'Wrote csv files for paper {paper}')

    def make_json_from_arxiv_dict(self, return_dict):
        """

        :param return_dict: 

        """
        import os
        jsonurl = os.path.join(os.getcwd(), 'arxiv_results.json')
        self.download_tools.makejson(jsonurl, return_dict)
        for result in return_dict:
            self.download_tools.check_or_make_directory(result)
            jsonurl = os.path.join(os.getcwd(), result, 'arxiv_result.json')
            self.download_tools.makejson(
                jsonurl, return_dict[result])

    def make_dict_from_arxiv_output(self, return_dict, search):
        """

        :param return_dict: param search:
        :param search: 

        """
        for result in search.get():
            url_encoded_id_of_paper = str(result.entry_id).rsplit('/', 1)[-1]

            return_dict[url_encoded_id_of_paper] = {}
            return_dict[url_encoded_id_of_paper]['date_updated'] = str(
                result.updated)
            return_dict[url_encoded_id_of_paper]['date_published'] = str(
                result.published)
            return_dict[url_encoded_id_of_paper]['title'] = str(result.title)
            return_dict[url_encoded_id_of_paper]['authors'] = str(
                result.authors)
            return_dict[url_encoded_id_of_paper]['summary'] = str(
                result.summary)
            return_dict[url_encoded_id_of_paper]['comment'] = str(
                result.comment)
            return_dict[url_encoded_id_of_paper]['journal_ref'] = str(
                result.journal_ref)
            return_dict[url_encoded_id_of_paper]['doi'] = str(result.doi)
            return_dict[url_encoded_id_of_paper]['primary_category'] = str(
                result.primary_category)
            return_dict[url_encoded_id_of_paper]['categories'] = str(
                result.categories)
            return_dict[url_encoded_id_of_paper]['links'] = str(result.links)
            return_dict[url_encoded_id_of_paper]['pdf_url'] = str(
                result.pdf_url)
            return_dict[url_encoded_id_of_paper]['entry_id'] = str(
                result.entry_id)

    def download_pdf(self, return_dict):
        """

        :param return_dict: 

        """
        import os
        import logging
        for result in return_dict:
            pdf_url = os.path.join(os.getcwd(), result, 'fulltext.pdf')
            self.download_tools.writepdf(
                return_dict[result]['pdf_url'], pdf_url)
            logging.info(f'Made pdf for {result}')

    def noexecute(self, query):
        """

        :param query: 

        """
        import logging
        logging.info(f"Arxiv api working for the query {query}")
