from finance.monzo import monzo_api, monzocsv_to_excel
from finance import utils
from finance import constants

def run():
    # get data from monzo and create csv
    account_id = monzo_api.get_account_id()
    transactions = monzo_api.get_transactions(account_id, utils.latest_entry_file(constants.MONZO_LAST_TRANSACTION))
    df = monzo_api.transactions_to_dataframe(transactions)
    monzo_api.save_to_csv(df)

    # csv to xls
    monzocsv_to_excel.append_csv_to_excel()