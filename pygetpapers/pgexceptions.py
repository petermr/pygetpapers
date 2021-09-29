import logging


class PygetpapersError(Exception):
    """This error is raised from classes in pygetpapers package.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        logging.warning(self.message)
