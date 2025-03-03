import os
import pandas as pd
from finance import constants
from openpyxl import load_workbook

# File paths
CSV_FILE = constants.CSV_FILE
EXCEL_FILE = constants.EXCEL_FILE
SHEET_NAME = constants.SHEET_NAME


# Function to append CSV data to the end of an existing table in Excel
def append_csv_to_excel(csv_file=CSV_FILE, excel_file=EXCEL_FILE, sheet_name=SHEET_NAME):
    
    # Ensure the monzo folder exists
    os.makedirs("monzo", exist_ok=True)
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found.")
        return
    
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Select the relevant columns
    selected_columns = ["Date", "Amount (GBP)", "Merchant", "Category"]
    df_filtered = df[selected_columns] 
    print(df_filtered)

    # Check if Excel file exists
    if not os.path.exists(excel_file):
        # If Excel file does not exist, create it with headers
        df.to_excel(excel_file, sheet_name=sheet_name, index=False, engine="openpyxl")
        print(f"Created new Excel file: {excel_file}")
        return

    # Load existing workbook and find the last row
    with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        workbook = load_workbook(excel_file)
        sheet = workbook[sheet_name]
        
        # Find the last row of data
        last_row = sheet.max_row

        # Append data to the table, starting from the next available row
        df.to_excel(writer, sheet_name=sheet_name, index=False, header=False, startrow=last_row)
        
        print(f"Data successfully appended to {excel_file} at row {last_row}")

append_csv_to_excel()






