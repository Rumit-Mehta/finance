import logging
import os
from finance import constants
import xlwings as xw


EXCEL_FILE = constants.EXCEL_FILE
SHEET_NAME = constants.SHEET_NAME
CALC_SHEET = constants.CALC_SHEET


def latest_entry_file(file, account):
    """Account used only for logging purposes"""
    with open(file, "r") as file:
        latest_date = file.read()
        logging.debug(f"{account} - Transactions From: {latest_date}")
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

    # Apply detail and category mappings
    detail_mapping = {
        "APPLE.COM/BILL": "Apple Storage 50gb",
        "OPENAI *CHATGPT SUBSCR": "OpenAI Subscription",
    }
    df["Details"] = df["Details"].replace(detail_mapping)

    misc = "Misc / Unknown"
    category_mapping = {
        "eating_out": "Food & Eating Out",
        "cash": misc,
        "other": misc,
        "HOTELS": "Holiday",
        "Holidays": "Holiday",
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

    # If Excel file doesn't exist, create it
    if not os.path.exists(EXCEL_FILE):
        df.to_excel(EXCEL_FILE, sheet_name=SHEET_NAME, index=False)
        print(f"Created new Excel file: {EXCEL_FILE}")
        return

    app = xw.App(visible=False)
    try:
        wb = xw.Book(EXCEL_FILE)
        sheet = wb.sheets[SHEET_NAME]

        # Find the last used row
        last_row = sheet.range("C" + str(sheet.cells.last_cell.row)).end("up").row

        for i, row in df.iterrows():
            new_row = last_row + 1 + i

            sheet.range(f"C{new_row}").value = row["Date"]
            sheet.range(f"C{new_row}").number_format = "DD-MMM-YY"
            sheet.range(f"D{new_row}").value = row["Type"]
            sheet.range(f"E{new_row}").value = row["Category"]
            sheet.range(f"F{new_row}").value = row["Amount (GBP)"]
            sheet.range(f"G{new_row}").value = row["Details"]

            balance_formula = f'=SUMPRODUCT([Amount],--([Date]<=C{new_row}), (([Type]="Expenses") + ([Type]="Savings")) * (-1) + ([Type] = "Income"))'
            sheet.range(f"H{new_row}").value = balance_formula

            sheet.range(f"I{new_row}").value = row["Account"]

            effective_date_formula = f'=IF(AND(D{new_row}="Income", shift_income_status = "Active", DAY(C{new_row})>=shift_income_starting_date),DATE(YEAR(C{new_row}),MONTH(C{new_row})+1,1),(C{new_row}))'
            sheet.range(f"J{new_row}").value = effective_date_formula

        wb.save()
        logging.info(f"Data successfully appended to {EXCEL_FILE} at row {last_row}")
    finally:
        wb.close()
        app.quit()


def pots_to_excel(pots: dict):
    '''Write a dictionary to Excel - used for Monzo pots data specifically'''
    # region - format dict
    # Sort the pots by value in descending order
    sorted_pots = dict(sorted(pots.items(), key=lambda item: item[1], reverse=True))

    # If more than 6 pots, aggregate 6 onwards into "Others"
    if len(sorted_pots) > 6:
        logging.info("More than 6 pots found. Extras will be aggregated into Others") 
        for key, value in list(sorted_pots.items())[5:]:
            sorted_pots["Others"] = sorted_pots.get("Others", 0) + value
            del sorted_pots[key]

    logging.debug(f"Sorted Pots: {sorted_pots}")
    # endregion

    # region - Write to Excel
    app = xw.App(visible=False)
    try:
        wb = xw.Book(EXCEL_FILE)
        sheet = wb.sheets[CALC_SHEET]

        # Start adding data from I19
        start_cell = sheet.range("I19")
        row_offset = 0
        for key, value in sorted_pots.items():
            row = start_cell.row + row_offset
            sheet.range(f"I{row}").value = key
            sheet.range(f"J{row}").value = value
            row_offset += 1

        wb.save()
        logging.info(f"Data successfully appended to {EXCEL_FILE} at row {start_cell.row}")
    finally:
        wb.close()
        app.quit()
    # endregion