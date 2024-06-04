import subprocess
import time

from logger import logger


while True:
    logger.debug('Start application ...')

    logger.debug('Start tg_bot.py ...')
    subprocess.call(['python', 'src/tg_bot.py'])

    time.sleep(0.1)

    logger.debug('Application is running.')