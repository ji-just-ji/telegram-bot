import logging


class Logger:
    """Sets up and manages logging"""
    
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("bot.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
