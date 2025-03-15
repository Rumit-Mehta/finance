from finance import constants
from finance.monzo import monzo
import logging

logging.basicConfig(
    level=constants.LOGGING_LEVEL, format="%(asctime)s -  %(levelname)s - %(message)s"
)


def main():
    # Get Monzo transactions and add to spreadsheet
    monzo.run()


if __name__ == "__main__":
    main()
    print("- - DONE - -")
