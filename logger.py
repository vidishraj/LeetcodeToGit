import logging

class Logger:
    """Logger class to configure logging for Akkountant."""

    def __init__(self, name: str):
        """Initialize the logger with the given name."""
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)  # Setting the logging level

        # Creating the logs directory if it doesn't exist
        # log_dir = 'logs'
        # if not os.path.exists(log_dir):
        #     os.makedirs(log_dir)

        # Creating handlers for different log levels
        self._setup_handlers("")

    def _setup_handlers(self, log_dir: str):
        """Set up file handlers for different log levels."""
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }

        # Creating console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Creating formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

    def get_logger(self):
        """Return the configured logger."""
        return self._logger