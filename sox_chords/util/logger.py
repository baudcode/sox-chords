from __future__ import print_function
import logging
from pprint import PrettyPrinter

pprinter = PrettyPrinter()


def pp(*data):
    if len(data) == 1:
        print(data[0])
    else:
        global pprinter
        pprinter.pprint(data)


logger = logging.Logger('music')
logger.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
# _formatter = logging.Formatter(
#    '%(asctime)s [%(threadName)s] - %(name)s - %(levelname)s - %(message)s')
_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()

# output of subprocess call will not be printed into the console if using logging.INFO
# this prohibits printing of subprocess call output twice
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(_formatter)
fh = logging.FileHandler('deepmusic.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(_formatter)
