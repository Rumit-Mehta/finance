import os
from dotenv import load_dotenv

load_dotenv("config/.env.local", override=True)
# Logging
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")

# security
ACCESS_TOKEN = os.getenv("MONZO_SECRET_ACCESS_TOKEN")
MONZO_CLIENT_SECRET = os.getenv("MONZO_CLIENT_SECRET")
MONZO_CLIENT_ID = os.getenv("MONZO_CLIENT_ID")
FLASK_SECRET = os.getenv("FLASK_SECRET_KEY")


# files
EXCEL_FILE = os.getenv("EXCEL_FILE")
CSV_FILE = os.getenv("CSV_FILE")
SHEET_NAME = os.getenv("SHEET_NAME")
MONZO_LAST_TRANSACTION = os.getenv("MONZO_LAST_TRANSACTION_FILE")

# Excel rows for Tracking table
XL_DATE_ROW = 3
XL_TYPE_ROW = 4
XL_CATEGORY_ROW = 5
XL_AMOUNT_ROW = 6
XL_DETAILS_ROW = 7
XL_ACCOUNT_ROW = 9

