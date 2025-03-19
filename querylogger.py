import logging

class Logger:
    def __init__(self, filename: str, log_lvl: str):
        self.filename = filename
        self.log_lvl = getattr(logging, log_lvl.upper(), logging.INFO) # logging.WARNING
        logging.basicConfig(level=self.log_lvl, filename=self.filename, filemode="a",
                            format="[+] %(asctime)s:[%(levelname)s]: %(message)s"
                            )

    def add_log_info(self, message: str):
        logging.info(message)
    
    def add_log_debug(self, message: str):
        logging.debug(message)
    
    def add_log_warning(self, message: str):
        logging.warning(message)
    
    def add_log_error(self, message: str):
        logging.error(message)
    
    def add_log_critical(self, message: str):
        logging.critical(message)

if __name__ == '__main__':
    logger = Logger("test.txt", "warning")
    logger.add_log_warning(f"The is a warning message")

