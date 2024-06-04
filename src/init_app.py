import subprocess
import time

from logger import logger


while True:
    logger.debug('Init application ...')

    logger.debug('Start create_chunks.py ...')
    subprocess.call(['python', 'create_chunks.py'])

    logger.debug('Start create_db.py ...')
    subprocess.call(['python', 'create_db.py'])

    time.sleep(0.1)

    logger.debug('Application is initialized.')