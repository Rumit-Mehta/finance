import logging
from finance import constants
from finance.utils import file_setup

logging.basicConfig(
    level=constants.LOGGING_LEVEL, format="%(levelname)s: %(asctime)s - %(message)s"
)


def setup():
    # setup the files
    file_setup()


if __name__ == "__main__":
    setup()
    print("- - Finished Setup - -")
