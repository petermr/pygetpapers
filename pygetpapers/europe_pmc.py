from pygetpapers.download_tools import download_tools
import pygetpapers


class europe_pmc:
    def __init__(self):
        self.download_tools = download_tools()

    def europepmc(self, query, size, synonym=True, **kwargs):
        """
            Makes the query to europepmc rest api then returns a python dictionary containing the research papers.

            :param query: the query passed on to payload

            :param size: total number of papers

            :param synonym: whether synonym should be or not

            :param kwargs: ensures that the output dict doesnt contain papers already there in update

            :return: Python dictionary containing the research papers.
        """
        import json
        import logging
        size = int(size)
        content = [[]]
        nextCursorMark = ['*', ]
        morepapers = True
        number_of_papers_there = 0
        maximum_hits_per_page = 1000
        while number_of_papers_there <= size and morepapers is True:
            queryparams = self.download_tools.buildquery(
                nextCursorMark[-1], maximum_hits_per_page, query, synonym=synonym)
            builtquery = self.download_tools.postquery(
                queryparams['headers'], queryparams['payload'])
            if "nextCursorMark" in builtquery["responseWrapper"]:
                nextCursorMark.append(
                    builtquery["responseWrapper"]["nextCursorMark"])
                totalhits = builtquery["responseWrapper"]["hitCount"]
                logging.info(f"Total Hits are {totalhits}")
                output_dict = json.loads(json.dumps(builtquery))
                try:
                    for paper in output_dict["responseWrapper"]["resultList"]["result"]:

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
