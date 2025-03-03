import os
import monzo

from dotenv import load_dotenv

load_dotenv('config/.env.local', override=True)

EXCEL_FILE = "files/finance_masters_sheet.xlsx"
ACCESS_TOKEN = os.getenv('MONZO_SECRET_ACCESS_TOKEN')

# Excel rows for Tracking table
XL_DATE_ROW = 3
XL_TYPE_ROW = 4
XL_CATEGORY_ROW = 5
XL_AMOUNT_ROW = 6
XL_DETAILS_ROW = 7

if __name__ == '__main__':
    print(ACCESS_TOKEN)