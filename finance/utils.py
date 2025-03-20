import logging
import os
import finance.constants as con
import files
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from datetime import timedelta


EXCEL_FILE = con.EXCEL_FILE
SHEET_NAME = con.SHEET_NAME


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


def latest_entry_file(file, account):
    """Account used only for logging purposes"""
    with open(file, "r") as file:
        latest_date = file.read()
        logging.info(f"{account} - Transactions From: {latest_date}")
    return latest_date


def file_setup():
    # TODO: make this more dynamic instead of hardcoding the file paths
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


def csv_to_excel(df):

    # Expecting the df to have the following columns
    # Date, Amount (GBP), Details, Category, Type, Account, Balance, Effective Date
    expected_columns = [
        "Date",
        "Amount (GBP)",
        "Details",
        "Category",
        "Type",
        "Account",
        "Balance",
        "Effective Date",
    ]

    # Check if DataFrame has only the expected columns
    if set(df.columns) != set(expected_columns):
        raise ValueError(
            f"Unexpected columns in DataFrame. Expected: {expected_columns}, Found: {list(df.columns)}"
        )

    # Update Details with custom mappings
    detail_mapping = {
        "APPLE.COM/BILL": "Apple Storage 50gb",
        "OPENAI *CHATGPT SUBSCR": "OpenAI Subscription",
    }
    df["Details"] = df["Details"].replace(detail_mapping)

    # Update 'Category' with custom mappings
    misc = "Misc / Unknown"
    category_mapping = {
        "eating_out": "Food & Eating Out",
        "cash": misc,
        "other": misc,
        "HOTELS": "Holiday",
    }
    df["Category"] = df["Category"].replace(category_mapping).str.title()
    df.loc[df["Category"].str.contains("Holiday", case=False, na=False), "Type"] = (
        "Goals"
    )

    # Changing Category depending on the detail
    details_to_category = {
        "Apple Storage 50gb": "Work",
        "OpenAI Subscription": "Work",
        "g2a.com": "Entertainment",
        "Goa Miles": "Transport",
    }
    for keyword, category in details_to_category.items():
        df.loc[
            df["Details"].str.contains(keyword, case=False, na=False), "Category"
        ] = category

    # Check if Excel file exists else create one
    if not os.path.exists(EXCEL_FILE):
        df.to_excel(EXCEL_FILE, sheet_name=SHEET_NAME, index=False, engine="openpyxl")
        print(f"Created new Excel file: {EXCEL_FILE}")
        return

    # Load existing workbook and find the last row
    workbook = load_workbook(EXCEL_FILE)
    sheet = workbook[SHEET_NAME]

    # Get the table
    table = sheet.tables["Tracking"]

    # Get the current table range
    start_cell, end_cell = table.ref.split(":")
    start_col_letter = start_cell[0]
    end_col_letter = end_cell[0]
    end_row = int(end_cell[1:])

    # Table Formatting
    font_style = Font(size=10)
    indent_style = Alignment(indent=1)
    indent_style_small = Alignment(indent=0.5)
    indent_style_left = Alignment(indent=1, horizontal="left")

    # Loop through all rows in df and add each to the table
    for i, (_, row) in enumerate(df.iterrows()):
        new_row_index = end_row + 1 + i

        # Column C (Date)
        cell = sheet.cell(row=new_row_index, column=3, value=row["Date"])
        cell.font = font_style
        cell.alignment = indent_style_left
        cell.number_format = "DD-MMM-YY"  # This applies the date format in Excel

        # Column D (Type)
        cell = sheet.cell(row=new_row_index, column=4, value=row["Type"])
        cell.font = font_style

        # Column E (Category)
        cell = sheet.cell(row=new_row_index, column=5, value=row["Category"])
        cell.font = font_style
        cell.alignment = indent_style

        # Column F (Amount)
        cell = sheet.cell(row=new_row_index, column=6, value=row["Amount (GBP)"])
        cell.font = font_style
        cell.alignment = indent_style_left

        # Column G (Details)
        cell = sheet.cell(row=new_row_index, column=7, value=row["Details"])
        cell.font = font_style
        cell.alignment = indent_style

        # Column H (Balance)
        row["Balance"] = (
            f'=SUMPRODUCT([Amount],--([Date]<=C{new_row_index}), (([Type]="Expenses") + ([Type]="Savings")) * (-1) + ([Type] = "Income"))'
        )
        cell = sheet.cell(row=new_row_index, column=8, value=row["Balance"])
        cell.font = font_style
        cell.alignment = indent_style

        # Column I (Account)
        cell = sheet.cell(row=new_row_index, column=9, value=row["Account"])
        cell.font = font_style
        cell.alignment = indent_style

        # Column J (Effective Date)
        row["Effective Date"] = (
            f'=IF(AND(D{new_row_index}="Income", shift_income_status = "Active", DAY(C{new_row_index})>=shift_income_starting_date),DATE(YEAR(C{new_row_index}),MONTH(C{new_row_index})+1,1),(C{new_row_index}))'
        )
        cell = sheet.cell(row=new_row_index, column=10, value=row["Effective Date"])
        cell.font = font_style
        cell.alignment = indent_style

    # Update the table's range to include all new rows
    total_new_rows = len(df)
    new_end_row = end_row + total_new_rows
    table.ref = f"{start_col_letter}{start_cell[1:]}:{end_col_letter}{new_end_row}"
    logging.info(f"Data successfully appended to {EXCEL_FILE} at row {end_row}")

    # Save the workbook
    workbook.save(EXCEL_FILE)
