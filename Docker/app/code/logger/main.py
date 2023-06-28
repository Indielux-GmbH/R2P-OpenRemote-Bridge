import configparser
from logging import basicConfig, getLogger

colors = {
    'black': '\u001b[30m',
    'red': '\u001b[31m',
    'green': '\u001b[32m',
    'yellow': '\u001b[33m',
    'blue': '\u001b[34m',
    'magenta': '\u001b[35m',
    'cyan': '\u001b[36m',
    'white': '\u001b[37m',
    'reset': '\u001b[0m',
}


class Logger:

    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        if self.config['logging']['level'] == 'DEBUG':
            self.set_debug()
        elif self.config['logging']['level'] == 'INFO':
            self.set_info()
        elif self.config['logging']['level'] == 'WARNING':
            self.set_warning()
        elif self.config['logging']['level'] == 'ERROR':
            self.set_error()
        elif self.config['logging']['level'] == 'CRITICAL':
            self.set_critical()
        else:
            self.set_debug()
            getLogger(__name__).critical("CRITICAL ERROR IN config - [logging] - Enabling DEBUG")

    @staticmethod
    def set_debug():
        basicConfig(level="DEBUG",
                    format="""| \u001b[35m%(levelname)-8s\u001b[0m | %(asctime)s | %(name)-30s | %(funcName)-30s | line %(lineno)-3d in %(pathname)-65s | %(message)s""")

    @staticmethod
    def set_info():
        basicConfig(level="INFO",
                    format="""| \u001b[32m%(levelname)-8s\u001b[0m | %(asctime)s | %(message)s""")

    @staticmethod
    def set_warning():
        basicConfig(level="WARNING",
                    format="""| \u001b[33m%(levelname)-8s\u001b[0m | %(asctime)s | %(name)-30s | %(funcName)-30s | line %(lineno)-3d in %(pathname)-65s | %(message)s""")

    @staticmethod
    def set_error():
        basicConfig(level="ERROR",
                    format="""| \u001b[31m%(levelname)-8s\u001b[0m | %(asctime)s | %(name)-30s | %(funcName)-30s | line %(lineno)-3d in %(pathname)-65s | %(message)s""")

    @staticmethod
    def set_critical():
        basicConfig(level="CRITICAL",
                    format="""| \u001b%(levelname)-8s\u001b[0m | %(asctime)s | %(name)-30s | %(funcName)-30s | line %(lineno)-3d in %(pathname)-65s | %(message)s""")
