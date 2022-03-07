from abc import ABC, abstractmethod

class RepositoryInterface(ABC):
    def __new__(mcls, classname, bases, cls_dict):
        """Makes docstrings appear in docs for subclasses
        """
        cls = ABC.ABCMeta.__new__(mcls, classname, bases, cls_dict)
        mro = cls.__mro__[1:]
        for name, member in cls_dict.iteritems():
            if not getattr(member, '__doc__'):
                for base in mro:
                    try:
                        member.__doc__ = getattr(base, name).__doc__
                        break
                    except AttributeError:
                        pass
        return cls

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