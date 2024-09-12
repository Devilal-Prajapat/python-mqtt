import logging
import logging.handlers
import time
import os

MAX_FILE_SIZE = 5*1000*1024  # 5MB
FORMAT = '%(asctime)s : %(levelname)s : %(filename)s : %(message)s'

loger = logging.getLogger(__name__)
loger.setLevel(logging.DEBUG)
logging.basicConfig(format=FORMAT)

def init_logger(filename):

    log_file_name = f"{filename}.log"
    logging.basicConfig(format=FORMAT)
    formater = logging.Formatter(FORMAT)
    
    # stream_handler = logging.StreamHandler()
    # stream_handler.setFormatter(fmt=formater)
    # loger.addHandler(stream_handler)

    # file_handler = logging.FileHandler(log_file_name)
    file_handler = logging.handlers.RotatingFileHandler(log_file_name,maxBytes=MAX_FILE_SIZE,backupCount=2)
    file_handler.setFormatter(fmt=formater)
    loger.addHandler(file_handler)
    

if __name__ == "__main__":
    ## get current file name
    file_name, file_extension = os.path.splitext(os.path.basename(os.path.abspath(__file__)))
    init_logger(file_name)
    while True:
        loger.info(loger)
        time.sleep(5)
