import requests
import logging
import pandas as pd

# Set up logging
logger = logging.getLogger(__name__)


# Fetch account ID
def get_account_id():
    ACCESS_TOKEN = __load_access_token()
    url = "https://api.monzo.com/accounts"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)

    # response.raise_for_status()
    if response.status_code in [200, 201, 204]:
        accounts = response.json()["accounts"]
        logging.debug(f"successful connection to {url}")
        if accounts:
            logging.info("DONE 1/4 - Access acount ID")
            return accounts[0]["id"]  # Using the first account
    raise Exception("Failed to retrieve Monzo account ID.")


# Fetch transactions
def get_transactions(account_id, date_from):
    ACCESS_TOKEN = __load_access_token()
    url = "https://api.monzo.com/transactions"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    params = {
        "account_id": account_id,
        "expand[]": "merchant",  # Expands merchant info if available
        "since": str(date_from),
        "limit": 100,  # Max number of transactions to fetch
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        transactions = response.json()["transactions"]

        # if transactions isnt empty
        if transactions:
            # Get the date of the last transaction (assuming the list is in chronological order)
            last_transaction_date = transactions[-1]["created"]
            logging.info(f"DONE 2/4  - Fetched transactions from {date_from}")
            # Send the date to a text file, overriding previous date
            with open(
                "files/last-transactions/monzo_last_transaction_date.txt", "w"
            ) as file:
                file.write(f"{last_transaction_date}")
                logging.debug(f"Last transaction date saved: {last_transaction_date}")
        else:
            logging.warning("No transactions found.")

        return response.json()["transactions"]

    raise Exception("Failed to retrieve transactions.")


# Fetch pots and filter out relevant information
def get_pots(account_id):
    dict = {}
    ACCESS_TOKEN = __load_access_token()

    url = "https://api.monzo.com/pots"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    params = {"current_account_id": account_id}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code in [200, 201, 204]:
        pots = response.json()["pots"]
        for pot in pots:
            key = pot["name"]
            value = pot["balance"] / 100  # Monzo amounts are in pence
            dict[key] = value
        return dict
    else:
        raise Exception("Failed to retrieve pots.")


# Convert transactions to a DataFrame
def transactions_to_dataframe(transactions):
    data = []
    for txn in transactions:
        data.append(
            {
                "Date": txn["created"],
                "Amount (GBP)": txn["amount"] / 100,  # Monzo amounts are in pence
                "Description": txn.get("description", ""),
                "Merchant": (
                    txn.get("merchant", {}).get("name", "N/A")
                    if txn.get("merchant")
                    else "N/A"
                ),
                "Category": txn.get("category", "N/A"),
                "Notes": txn.get("notes", ""),
            }
        )

    if data:
        logging.info("DONE 3/4 - Converted transactions to dataframe")

    return pd.DataFrame(data)


# Save DataFrame to CSV
def save_to_csv(df, filename="files/input-files/monzo_transactions.csv"):
    """Save the DataFrame to a CSV file if the DataFrame is not empty"""
    if df.empty:
        logging.warning("No transactions to save.")
        open(filename, "w").close()
    else:
        logging.info("DONE 4/4 - Saved transactions to CSV")
        df.to_csv(filename, index=False)


# Load access token from file
def __load_access_token():
    with open("files/monzo_access_token.txt", "r") as file:
        return file.read().strip()
