

class ConfigReader():
    """
    reads the config file and extracts data
    """
    def __init__(self):
        pass

    def read_item(self, key, config_file):
        """
        read value for key using config file
        """
        """
        config = configparser.ConfigParser()
config.read('example.ini')
config.sections()
config['forge.example']['User']
"""
        with config_file:
            config = configparser.ConfigParser()
            config.read_string(config_file)
            sections = config.sections()
            for section in sections:
                logger.info(f"section {section}")
