import logging
import logging.handlers
import time
import os

MAX_FILE_SIZE = 5*1000*1024  # 5MB
FORMAT = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'

## get current file name
file_name, file_extension = os.path.splitext(os.path.basename(os.path.abspath(__file__)))
log_file_name = f"{file_name}.log"

logging.basicConfig(format=FORMAT)
loger = logging.getLogger(__name__)
formater = logging.Formatter(FORMAT)

# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(fmt=formater)
# loger.addHandler(stream_handler)

# file_handler = logging.FileHandler(log_file_name)
file_handler = logging.handlers.RotatingFileHandler(log_file_name,maxBytes=MAX_FILE_SIZE,backupCount=2)
file_handler.setFormatter(fmt=formater)
loger.addHandler(file_handler)
loger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    while True:
        loger.info(loger)
        time.sleep(5)
