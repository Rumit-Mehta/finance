import logging
import os
import numpy as np
import pandas as pd
from finance import constants
from finance import utils
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment

INPUT_FOLDER = constants.INPUT_FILE_PATH
T212_DATE_FILE = constants.TRADING212_LAST_TRANSACTION
REV_DATE_FILE = constants.REVOLUT_LAST_TRANSACTION


def run():
    # If path does not exist
    if not os.path.exists(INPUT_FOLDER):
        logging.error(f"Input folder {INPUT_FOLDER} does not exist.")
        return

    processed_items = []
    unprocessed_items = []

    # Loop through each item in the folder
    for file_name in os.listdir(INPUT_FOLDER):

        file_path = os.path.join(INPUT_FOLDER, file_name)

        # Only intersted in csv files
        if not os.path.isfile(file_path) or not file_name.lower().endswith(".csv"):
            unprocessed_items.append(file_name)
            continue

        # Process the file
        logging.info(f"Processing file: {file_name}")
        df = pd.read_csv(file_path, header=None)

        if df.empty:
            logging.warning(f"File {file_name} is empty")
            unprocessed_items.append(file_name)
            continue

        # Check the first cell to determine the source of the csv
        first_cell = df.iloc[0, 0]

        match first_cell:
            # Trading 212 CSV
            case "Action":
                process_trading212_csv(df)
                processed_items.append(file_name)

            # Revolut CSV
            case "Type":
                process_revolut_csv(df)
                processed_items.append(file_name)

            # Default case
            case _:
                logging.warning("Unknown CSV format")
                unprocessed_items.append(file_name)

    # Log the results
    logging.info(f"Processed files: {processed_items}")
    logging.info(f"Unprocessed files: {unprocessed_items}")
    logging.info("Finished processing CSV files")


def process_trading212_csv(df):
    # Get the date of the last transaction
    start_date = utils.latest_entry_file(T212_DATE_FILE)

    # Convert the date column to datetime and filter the DataFrame
    df.columns = df.iloc[0]  # Set first row as header
    df = df[1:].reset_index(drop=True)  # Remove header row from data

    if "Time" in df.columns:
        df["Time"] = df["Time"].str.split(".").str[0]  # Remove everything after the dot
        df["Time"] = pd.to_datetime(df["Time"], errors="coerce")

    if start_date:
        start_date = pd.to_datetime(start_date, errors="coerce")
        df = df[df["Time"] > start_date]  # Filter only new transactions

    if df.empty:
        logging.info("No new transactions to process.")
        return
    
    # Filter the df
    selected_columns = ["Action", "Time", "Total", "Merchant name", "Merchant category"]
    df = df[selected_columns]
    df = df[df["Action"] != "Deposit"]  # Remove 'Deposit' rows

    # Merge 'Spending cashback' rows into one row
    cashback_rows = df[df["Action"] == "Spending cashback"]
    if not cashback_rows.empty:
        total_cashback = (
            cashback_rows["Total"].astype(float).sum()
        )  # Ensure numeric before summing
        latest_cashback_time = cashback_rows["Time"].max()  # Get the latest timestamp
        df = df[df["Action"] != "Spending cashback"]  # Remove original rows
        new_row = pd.DataFrame(
            [
                {
                    "Action": "Spending cashback",
                    "Time": latest_cashback_time,  # Set to latest timestamp
                    "Total": total_cashback,
                    "Merchant name": None,
                    "Merchant category": "Other"
                }
            ]
        )
        df = pd.concat([df, new_row], ignore_index=True)

    # Initialising new columns
    df["Account"] = "T212"
    df["Action"] = np.where(df["Total"].astype(float) < 0, "Expenses", "Income")
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").abs()
    df["Balance"] = (
        '=SUMPRODUCT([Amount],--([Date]<=[@Date]), (([Type]="Expenses") + ([Type]="Savings")) * (-1) + ([Type] = "Income"))'
    )
    df["Effective Date"] = (
        '=IF(AND([@Type]="Income", shift_income_status = "Active", DAY([@Date])>=shift_income_starting_date),DATE(YEAR([@Date]),MONTH([@Date])+1,1),([@Date]))'
    )

    # Renaming Columns
    df.rename(columns = {
        "Action": "Type",
        "Time": "Date",
        "Total": "Amount (GBP)",
        "Merchant name": "Details",
        "Merchant category": "Category"
    },inplace=True)

    # Process the filtered data
    logging.info(f"Processing {len(df)} new transactions.")
    logging.debug(df)

def process_revolut_csv(df):
    logging.info("Revolut CSV detected")
