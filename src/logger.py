import logging
import os
from datetime import datetime

#this is directory
LOGS_DIR = 'logs'
os.makedirs(LOGS_DIR,exist_ok=True)


#now code to store files in the directory based on dates
LOG_FILE = os.path.join(LOGS_DIR,f"log_{datetime.now().strftime('%Y-%m-%d')}.log")
# log_2025-03-25.log  

logging.basicConfig(filename=LOG_FILE,
                    format='%(asctime)s-%(levelname)s-%(message)s',
                    level=logging.INFO #IT MEANS ONLY INFO, WARNING AND ERROR MESSAGES WILL BE SHOWN
)


#used to init logger in diff files
def get_logger(name):
    logger = logging.getLogger(name) #will create a logger with 'name' given
    logger.setLevel(logging.INFO)
    return logger


