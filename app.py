from finance import constants, utils
from finance.monzo import monzo
from finance.read_csv import read_csv
import logging

logging.basicConfig(
    level=constants.LOGGING_LEVEL, format="%(levelname)s: %(asctime)s - %(message)s"
)


def main():

    # Get Monzo transactions from API and append to Excel
    monzo.run()

    # Get CSV data from other banks and append to Excel
    read_csv.run()


if __name__ == "__main__":
    main()
    print("- - DONE - -")
