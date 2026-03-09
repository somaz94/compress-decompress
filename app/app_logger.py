import logging


class Logger:
    """Logging utility with configurable verbosity"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

    def _setup_logging(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def set_verbose(self, verbose: bool):
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)


logger = Logger()
