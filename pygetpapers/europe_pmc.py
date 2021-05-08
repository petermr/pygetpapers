from pygetpapers.download_tools import download_tools
import pygetpapers


class europe_pmc:
    def __init__(self):
        self.download_tools = download_tools("europepmc")

    def europepmc(self, query, size, synonym=True, **kwargs):
        """Makes the query to europepmc rest api then returns a python dictionary containing the research papers.

        Args:
          query: the query passed on to payload
          size: total number of papers
          synonym: whether synonym should be or not (Default value = True)
          kwargs: ensures that the output dict doesnt contain papers already there in update
          **kwargs: 

        Returns:
          Python dictionary containing the research papers.

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

        Args:
          content: list containing all the papers
          kwargs: kwargs of the main function containing whether to update or add papers
          number_of_papers_there: total number of papers found till now
          output_dict: output directory
          size: required number of papers

        Returns:

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

        Args:
          builtquery: api result dictionary
          morepapers: weather to download more papers
          nextCursorMark: list containing all cursor marks

        Returns:

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

        Args:
          maximum_hits_per_page: 
          nextCursorMark: 
          query: 
          synonym: 

        Returns:

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

        Args:
          content: 
          kwargs: 
          number_of_papers_there: 
          paper: 
          size: 

        Returns:

        """
        import logging
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
