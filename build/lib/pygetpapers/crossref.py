from pygetpapers.download_tools import download_tools


class crossref:
    """ """

    def __init__(self):
        pass

    def crossref(self, query, size, filter=None, update=None, **kwargs):
        """

        :param query: param size:
        :param filter: Default value = None)
        :param update: Default value = None)
        :param size: param **kwargs:
        :param **kwargs: 

        """
        import logging
        from habanero import cn
        from habanero import Crossref
        cr = Crossref()
        Crossref(mailto="ayushgarg@science.org.in")
        Crossref(ua_string="pygetpapers/version@0.0.4.6")
        logging.info('Making request to crossref')

        eco = cr.works(query={query},
                       limit=size, filter=filter)
        doi_list = []
        logging.info('Got request result from crossref')

        for item in eco['message']['items']:
            doi_list.append(item["DOI"])
        logging.debug('Added DOIs to a list')
        logging.debug('Requesting metadata in json format')

        total_json_output = cn.content_negotiation(
            ids=doi_list, format="citeproc-json")
        logging.debug('Got metadata in json format')

        total_number_of_results = eco['message']['total-results']
        number_of_papers = eco['message']['items']
        dict_to_return = {'number_of_papers': number_of_papers,
                          'total_hits': total_number_of_results, 'total_json_output': total_json_output}
        return(dict_to_return)

    def make_json_files_for_paper(self, returned_dict):
        """

        :param returned_dict: 

        """
        import os
        import logging
        with open('crossref_results.json', mode='w') as f:
            f.write(str(returned_dict['total_json_output']))
            logging.info('Wrote metadata file for the query')
        paper_numer = 0

        logging.info(
            f'Writing metadata file for the papers at {str(os.getcwd())}')
        for paper in returned_dict['total_json_output']:
            paper_numer += 1
            import json
            dict_of_paper = json.loads(paper)
            doi_of_paper = dict_of_paper['DOI']
            url_encoded_doi_of_paper = doi_of_paper.replace(
                '\\', '_').replace('/', '_')
            if not os.path.isdir(url_encoded_doi_of_paper):
                os.makedirs(url_encoded_doi_of_paper)
            path_to_save_metadata = os.path.join(
                str(os.getcwd()), url_encoded_doi_of_paper, 'crossref_result.json')
            with open(path_to_save_metadata, mode='w') as f:
                f.write(str(paper))
            logging.info(f'Wrote metadata file for the paper {paper_numer}')

    def noexecute(self, query, size, filter=None, **kwargs):
        """

        :param query: param size:
        :param filter: Default value = None)
        :param size: param **kwargs:
        :param **kwargs: 

        """
        import logging
        returned_result = self.crossref(
            query, size=10, filter=filter, **kwargs)
        totalhits = returned_result['total_hits']
        logging.info(f'Total number of hits for the query are {totalhits}')

    def download_and_save_results(self, query, size, filter=None, update=None, **kwargs):
        """

        :param query: param size:
        :param filter: Default value = None)
        :param update: Default value = None)
        :param size: param **kwargs:
        :param **kwargs: 

        """
        returned_result = self.crossref(
            query, size, filter=filter, update=update, **kwargs)
        self.make_json_files_for_paper(returned_result)
