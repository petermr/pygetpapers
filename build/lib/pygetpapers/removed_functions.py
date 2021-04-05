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
