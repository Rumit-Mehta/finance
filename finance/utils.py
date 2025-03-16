import logging
import os
import finance.constants as con
import files
from openpyxl import load_workbook
from datetime import timedelta


EXCEL_FILE = con.EXCEL_FILE
SHEET_NAME = "Transactions"


# get the date for the last entry for a spefific account eg. monzo, amex etc
def latest_entry(account: str):

    # load the workbook and sheet
    workbook = load_workbook(EXCEL_FILE)
    ws = workbook["Tracking"]

    # get the indecies for the date and account column
    date_column = 2
    account_column = 8

    # reverse iterate through the sheet
    latest_date = None
    for row in reversed(
        list(ws.iter_rows(min_row=12, values_only=True))
    ):  # Start from row 12
        date_value, account_value = (
            row[date_column],
            row[account_column],
        )  # Adjust based on actual columns
        if account_value and account in str(account_value):
            latest_date = date_value
            break

    # Print the latest date found
    if latest_date:
        print("Latest Monzo transaction date:", latest_date)
        print("Day after Monzo transaction date:", latest_date + timedelta(days=1))
        # you are more interested in the start date which is 1 more than the latest date.
        latest_date = str(latest_date + timedelta(days=1)).split(" ")[0]
    else:
        print("No Monzo tag found in the file.")

    return latest_date


def latest_entry_file(file):
    with open(file, "r") as file:
        latest_date = file.read()
        logging.info(f"Latest Transaction Date: {latest_date}")
    return latest_date


def file_setup():

    required_files = [
        "files/monzo_last_transaction_date.txt",
        "files/trading212_last_transaction_date.txt",
        "files/revolut_last_transaction_date.txt",
    ]

    for file in required_files:
        if not os.path.exists(file):
            with open(file, "w") as f:
                logging.info(f"Created file: {file}")
        else:
            logging.info(f"File exists: {file}")
