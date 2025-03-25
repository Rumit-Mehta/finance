import time
from finance.monzo import monzo_api
from finance import utils
from finance import constants


def run():
    # get data from monzo api
    account_id = monzo_api.get_account_id()
    pots = monzo_api.get_pots(account_id)
    transactions = monzo_api.get_transactions(
        account_id, utils.latest_entry_file(constants.MONZO_LAST_TRANSACTION, "Monzo")
    )
    dataframe = monzo_api.transactions_to_dataframe(transactions)

    # save data to csv
    utils.pots_to_excel(pots)
    monzo_api.save_to_csv(dataframe)
    time.sleep(3)  # Sleep for 3 seconds to give time for the file to be written to disk


# Test the Monzo API
def test():
    # account_id = monzo_api.get_account_id()
    # pots = monzo_api.get_pots(account_id)
    # utils.pots_to_excel(pots)
    return
