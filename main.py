import logging
import sys

from PyQt5.QtWidgets import (QApplication)

from config.config import Config
from ui import FreeTTS

if __name__ == "__main__":
    logging.basicConfig(filename='log.log', level=logging.DEBUG, format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    config = Config()

    app = QApplication(sys.argv)
    ex = FreeTTS(config)
    sys.exit(app.exec_())
