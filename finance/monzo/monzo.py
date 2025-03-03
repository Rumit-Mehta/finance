from finance.monzo import monzo_api as api
from finance.utils import latest_entry

def run():
    account_id = api.get_account_id()
    date = latest_entry("Monzo")
    transactions = api.get_transactions(account_id, date)
    df = api.transactions_to_dataframe(transactions)
    api.save_to_csv(df)