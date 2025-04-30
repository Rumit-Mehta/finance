from finance import constants, utils
from finance.monzo import monzo
from finance.read_csv import read_csv
import logging

logging.basicConfig(
    level=constants.LOGGING_LEVEL, format="%(levelname)s: %(asctime)s - %(message)s"
)


def main():

    # Get Monzo transactions from API
    monzo.run()

    # Get CSV data from all the banks and append to Excel
    read_csv.run()


def test():
    monzo.test()


if __name__ == "__main__":
    main()
    print("- - FINISHED - -")
