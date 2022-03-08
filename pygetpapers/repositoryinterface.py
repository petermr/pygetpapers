from abc import ABC, abstractmethod
import logging
from pygetpapers.download_tools import DownloadTools

TOTAL_HITS = "total_hits"
NEW_RESULTS = "new_results"
RXIV_RESULT = "rxiv_result"
UPDATED_DICT = "updated_dict"
JATSXML = "jatsxml"
FULLTEXT_XML = "fulltext.xml"
DOI = "doi"
TOTAL_JSON_OUTPUT = "total_json_output"
BIORXIV = "biorxiv"
MESSAGES = "messages"
TOTAL = "total"
COLLECTION = "collection"
CURSOR_MARK = "cursor_mark"
RXIV = "rxiv"
class RepositoryInterface(ABC):
    
    @abstractmethod
    def noexecute(self, query_namespace):
        """Takes in the query_namespace object as the parameter and runs the query search for given search parameters but only prints the output and not write to disk.

        :param query_namespace: pygetpaper's namespace object containing the queries from argparse
        :type query_namespace: dict
        """
        pass
        
    @abstractmethod        
    def update(self, query_namespace):
        """If there is a previously existing corpus, this function reads in the 'cursor mark' from the previous run, increments in, and adds new papers for the given parameters to the existing corpus.

        :param query_namespace: pygetpaper's namespace object containing the queries from argparse
        :type query_namespace: dict
        """
        pass
    
    @abstractmethod
    def apipaperdownload(self, query_namespace):
        """Takes in the query_namespace object as the parameter and runs the query search for given search parameters.

        :param query_namespace: pygetpaper's namespace object containing the queries from argparse
        :type query_namespace: dict
        """
        pass

 